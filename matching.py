# matching.py - Debug Version
import os
import re
import requests
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import Dict, List, Tuple

# ===== CONFIG =====
HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
HF_HEADERS = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}

# Load local embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def call_llm(prompt):
    """Call Hugging Face API for LLM extraction with debug output."""
    print(f"🤖 LLM Prompt: {prompt[:200]}...")
    
    payload = {
        "inputs": prompt, 
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.1,
            "do_sample": True
        }
    }
    
    try:
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=60)
        print(f"📡 API Response Status: {response.status_code}")
        
        response.raise_for_status()
        data = response.json()
        print(f"📄 Raw API Response: {data}")
        
        if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
            result = data[0]["generated_text"].strip()
            print(f"✅ Extracted Text: '{result}'")
            return result
        elif isinstance(data, dict) and "error" in data:
            print(f"❌ API Error: {data['error']}")
            return ""
        else:
            print(f"❌ Unexpected response format: {data}")
            return ""
            
    except Exception as e:
        print(f"❌ LLM API Error: {e}")
        return ""

def simple_extraction_fallback(text, section):
    """Fallback extraction if LLM fails."""
    print(f"🔄 Using fallback extraction for {section}")
    
    text_lower = text.lower()
    
    if section == "skills":
        # Look for common skill indicators
        skill_patterns = [
            r'python|java|javascript|react|angular|vue|node|django|flask|spring',
            r'sql|mysql|postgresql|mongodb|oracle|database',
            r'aws|azure|gcp|cloud|kubernetes|docker',
            r'machine learning|ml|ai|data science|analytics',
            r'git|github|version control|agile|scrum'
        ]
        found_skills = []
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower)
            found_skills.extend(matches)
        return ", ".join(set(found_skills)) if found_skills else ""
    
    elif section == "experience":
        # Look for experience indicators
        exp_patterns = [
            r'\d+\+?\s*(years?|yrs?)\s*of\s*experience',
            r'worked\s+as|experience\s+as|role\s+as',
            r'developed|built|created|implemented|managed|led'
        ]
        found_exp = []
        for pattern in exp_patterns:
            matches = re.findall(pattern, text_lower)
            found_exp.extend(matches)
        return "; ".join(found_exp[:3]) if found_exp else ""
    
    elif section == "education":
        # Look for education indicators
        edu_patterns = [
            r'bachelor|master|phd|degree|university|college',
            r'computer science|engineering|mathematics|statistics',
            r'certification|certified|certificate'
        ]
        found_edu = []
        for pattern in edu_patterns:
            matches = re.findall(pattern, text_lower)
            found_edu.extend(matches)
        return "; ".join(set(found_edu)) if found_edu else ""
    
    return text[:200] + "..." if len(text) > 200 else text

def extract_with_structured_prompt(text: str, section: str, context: str) -> str:
    """Extract with LLM or fallback to simple extraction."""
    print(f"\n🔍 Extracting {section} from {context}")
    print(f"📝 Input text length: {len(text)} characters")
    
    if not text or len(text.strip()) < 10:
        print("❌ Text too short or empty")
        return ""
    
    # Check if HF_API_TOKEN is set
    api_token = os.getenv('HF_API_TOKEN')
    if not api_token:
        print("⚠️ HF_API_TOKEN not found, using fallback extraction")
        return simple_extraction_fallback(text, section)
    
    # Simple prompts that work better with Flan-T5
    simple_prompts = {
        "skills": f"What technical skills are mentioned in this {context}?\n\n{text[:1000]}\n\nSkills:",
        "experience": f"What work experience is described in this {context}?\n\n{text[:1000]}\n\nExperience:",
        "education": f"What education or qualifications are mentioned in this {context}?\n\n{text[:1000]}\n\nEducation:",
        "general": f"Summarize the key qualifications from this {context}:\n\n{text[:1000]}\n\nSummary:"
    }
    
    prompt = simple_prompts.get(section, simple_prompts["general"])
    result = call_llm(prompt)
    
    # If LLM fails or returns empty, use fallback
    if not result or len(result.strip()) < 3:
        print("🔄 LLM extraction failed, using fallback")
        result = simple_extraction_fallback(text, section)
    
    print(f"✅ Final extracted {section}: '{result}'")
    return result.strip()

def calculate_simple_similarity(text1: str, text2: str) -> float:
    """Simplified similarity calculation with debug output."""
    print(f"\n📊 Calculating similarity:")
    print(f"   Text1: '{text1[:100]}...'")
    print(f"   Text2: '{text2[:100]}...'")
    
    if not text1 or not text2:
        print("❌ One or both texts are empty - returning 0.0")
        return 0.0
    
    if text1.strip() == text2.strip():
        print("✅ Texts are identical - returning 100.0")
        return 100.0
    
    try:
        # Use sentence transformers for similarity
        emb1 = embedding_model.encode(text1, convert_to_tensor=True)
        emb2 = embedding_model.encode(text2, convert_to_tensor=True)
        similarity = float(util.cos_sim(emb1, emb2).item())
        
        print(f"🎯 Raw cosine similarity: {similarity}")
        
        # Convert to percentage with realistic scaling
        percentage = similarity * 100
        
        # Apply some scaling to make scores more realistic
        if percentage > 90:
            percentage = min(95, percentage * 0.9)  # Cap high scores
        elif percentage < 10:
            percentage = max(5, percentage * 1.2)   # Boost very low scores slightly
            
        print(f"📈 Final similarity score: {percentage:.1f}%")
        return round(percentage, 1)
        
    except Exception as e:
        print(f"❌ Similarity calculation error: {e}")
        return 0.0

def match_resume_to_jd(resume_text: str, jd_text: str) -> Tuple[float, Dict[str, float]]:
    """Generate match scores with extensive debugging."""
    
    print("\n" + "="*50)
    print("🚀 STARTING RESUME MATCHING PROCESS")
    print("="*50)
    
    print(f"📄 Resume text length: {len(resume_text)}")
    print(f"💼 Job description length: {len(jd_text)}")
    print(f"📄 Resume preview: {resume_text[:200]}...")
    print(f"💼 JD preview: {jd_text[:200]}...")
    
    if not resume_text or not jd_text:
        print("❌ Empty input texts")
        return 0.0, {"skills": 0.0, "experience": 0.0, "education": 0.0}
    
    # Extract sections with debugging
    section_scores = {}
    sections = ["skills", "experience", "education"]
    
    all_scores = []
    
    for section in sections:
        print(f"\n{'='*30}")
        print(f"🔍 ANALYZING {section.upper()}")
        print(f"{'='*30}")
        
        # Extract from both resume and JD
        resume_section = extract_with_structured_prompt(resume_text, section, "resume")
        jd_section = extract_with_structured_prompt(jd_text, section, "job description")
        
        # Calculate similarity
        similarity = calculate_simple_similarity(resume_section, jd_section)
        section_scores[section] = similarity
        
        if similarity > 0:
            all_scores.append(similarity)
        
        print(f"🎯 {section.capitalize()} final score: {similarity}%")
    
    # Calculate overall score
    if all_scores:
        overall_score = sum(all_scores) / len(all_scores)
    else:
        overall_score = 0.0
    
    print(f"\n🏆 FINAL OVERALL SCORE: {overall_score:.1f}%")
    print(f"📊 SECTION SCORES: {section_scores}")
    
    return round(overall_score, 1), section_scores

# Test function
def test_basic_functionality():
    """Test basic functionality without API calls."""
    print("🧪 Testing basic functionality...")
    
    test_resume = "Python developer with 3 years experience in Django, Flask, machine learning, and data analysis. Bachelor's degree in Computer Science."
    test_jd = "Looking for Python developer with Flask experience, ML skills, and computer science background."
    
    score, sections = match_resume_to_jd(test_resume, test_jd)
    print(f"Test result - Overall: {score}%, Sections: {sections}")

if __name__ == "__main__":
    test_basic_functionality()
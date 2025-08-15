import streamlit as st
try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("📊 Plotly not installed. Radar chart will be skipped. Run: pip install plotly")

from matching import match_resume_to_jd
from resume_parser import extract_text

st.set_page_config(page_title="Recruitly - AI Resume Matcher", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    color: white;
    margin: 10px 0;
}
.section-score {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #667eea;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

st.title("🎯 Recruitly — AI Resume Matcher")
st.markdown("### Get precise AI-powered resume-to-job matching scores")

# Sidebar for settings
with st.sidebar:
    st.header("📊 Scoring Guide")
    st.markdown("""
    - **90-100%**: Excellent match
    - **75-89%**: Very good match
    - **60-74%**: Good match
    - **45-59%**: Fair match
    - **30-44%**: Poor match
    - **0-29%**: Very poor match
    """)

# Set defaults (no settings checkboxes)
show_debug = False
show_extractions = False

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 Resume Upload")
    resume_file = st.file_uploader(
        "Upload your resume (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
        help="Supports common resume formats"
    )

with col2:
    st.header("💼 Job Description")
    job_description = st.text_area(
        "Paste the job description here",
        height=200,
        placeholder="Paste the complete job description including requirements, responsibilities, and qualifications..."
    )

# Match button
st.markdown("---")
if st.button("🚀 Analyze Match", type="primary", use_container_width=True):
    if resume_file is None or not job_description.strip():
        st.error("⚠️ Please upload a resume and paste a job description.")
    else:
        with st.spinner("🔍 Analyzing resume and job description..."):
            # Extract text from resume
            resume_text = extract_text(resume_file)
            
            if not resume_text.strip():
                st.error("❌ Could not extract text from the resume. Please check the file format.")
                st.stop()
            
            st.info("📋 Check your terminal/console for detailed debug information!")
            
            # Perform matching
            total_score, section_scores = match_resume_to_jd(resume_text, job_description)

        # Display results
        st.markdown("## 📊 Match Results")
        
        # Overall score with color coding
        score_color = "#28a745" if total_score >= 75 else "#ffc107" if total_score >= 60 else "#dc3545"
        
        st.markdown(f"""
        <div class="metric-card">
            <h2 style="margin: 0; font-size: 3em; color: white;">{total_score:.1f}%</h2>
            <h4 style="margin: 10px 0 0 0; color: white;">Overall Match Score</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Interpretation
        if total_score >= 85:
            st.success("🎉 **Excellent Match!** This candidate appears to be very well-suited for this role.")
        elif total_score >= 70:
            st.success("✅ **Good Match!** This candidate has strong potential for this role.")
        elif total_score >= 55:
            st.warning("⚡ **Moderate Match.** Some alignment exists, but gaps may need to be addressed.")
        elif total_score >= 40:
            st.warning("⚠️ **Limited Match.** Significant skill or experience gaps present.")
        else:
            st.error("❌ **Poor Match.** Major misalignment between resume and job requirements.")

        # Section-wise scores with visual bars
        st.markdown("### 📋 Detailed Section Analysis")
        
        # Create columns for section scores
        score_cols = st.columns(3)
        
        section_names = {"skills": "🛠️ Skills", "experience": "💼 Experience", "education": "🎓 Education"}
        
        for i, (section, score) in enumerate(section_scores.items()):
            with score_cols[i]:
                # Progress bar color based on score
                bar_color = "#28a745" if score >= 70 else "#ffc107" if score >= 50 else "#dc3545"
                
                st.markdown(f"""
                <div class="section-score">
                    <h4 style="margin: 0 0 10px 0;">{section_names.get(section, section.title())}</h4>
                    <div style="background: #e9ecef; border-radius: 10px; overflow: hidden;">
                        <div style="background: {bar_color}; width: {score}%; height: 20px; border-radius: 10px; transition: width 0.3s;"></div>
                    </div>
                    <p style="margin: 10px 0 0 0; font-size: 1.2em; font-weight: bold;">{score:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)

        # Simple section scores summary (fallback if no plotly)
        if not PLOTLY_AVAILABLE:
            st.markdown("### 📊 Section Scores Summary")
            for section, score in section_scores.items():
                st.metric(label=section_names.get(section, section.title()), value=f"{score:.1f}%")

        # Show extracted sections if requested
        if show_extractions:
            st.markdown("---")
            st.markdown("## 📄 Raw Extracted Content")
            
            extract_cols = st.columns(2)
            
            with extract_cols[0]:
                with st.expander("Resume Text"):
                    st.text_area("Extracted Resume Content", value=resume_text, height=300, disabled=True)
            
            with extract_cols[1]:
                with st.expander("Job Description Text"):
                    st.text_area("Job Description Content", value=job_description, height=300, disabled=True)

        # Recommendations section
        st.markdown("---")
        st.markdown("## 💡 Recommendations")
        
        recommendations = []
        
        if section_scores.get("skills", 0) < 60:
            recommendations.append("🛠️ **Skills Gap**: Consider highlighting more relevant technical skills or acquiring missing skills through training.")
        
        if section_scores.get("experience", 0) < 60:
            recommendations.append("💼 **Experience Gap**: Emphasize transferable experience or consider how current experience applies to this role.")
        
        if section_scores.get("education", 0) < 60 and section_scores.get("education", 0) > 0:
            recommendations.append("🎓 **Education**: Consider highlighting relevant coursework, certifications, or continuing education.")
        
        if total_score < 70:
            recommendations.append("📝 **Resume Optimization**: Tailor your resume to better match the job requirements and use similar terminology.")
        
        if not recommendations:
            recommendations.append("🎉 **Great Match!** Your profile aligns well with the job requirements.")
        
        for rec in recommendations:
            st.markdown(f"- {rec}")

# Footer
st.markdown("---")
st.markdown("*Powered by AI • Built with ❤️ using Streamlit*")
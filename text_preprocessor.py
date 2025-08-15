import re
import nltk
from nltk.corpus import stopwords

# Download stopwords if not done yet (run once)
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

def clean_text(text):
    """
    Cleans the input text by:
    - Lowercasing
    - Removing punctuation and numbers
    - Removing stopwords
    """
    # Lowercase
    text = text.lower()

    # Remove punctuation and numbers (keep only alphabets and spaces)
    text = re.sub(r'[^a-z\s]', '', text)

    # Tokenize and remove stopwords
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]

    return ' '.join(filtered_words)

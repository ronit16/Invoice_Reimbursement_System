import re

def clean_extracted_text(text: str) -> str:
    # Remove excessive whitespace
    text = re.sub(r'\s{2,}', ' ', text)
    # Normalize newlines between logical sections
    text = re.sub(r'\n+', '\n', text)
    # Optional: replace newline with space to keep policy one-liners
    return text.strip()

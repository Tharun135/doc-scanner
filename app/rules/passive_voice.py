import re
import spacy
from bs4 import BeautifulSoup
import html

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    
    # Rule: Detect passive voice
    for sent in doc.sents:
        if any(token.dep_ == "auxpass" for token in sent):
            # Clean the sentence text to remove any remaining HTML tags or entities
            clean_sentence = BeautifulSoup(sent.text.strip(), "html.parser").get_text()
            clean_sentence = html.unescape(clean_sentence)
            suggestions.append(f"Issue: Passive voice detected\nOriginal sentence: {clean_sentence}\nAI suggestion: Consider revising to active voice for clearer, more direct communication.")
    
    return suggestions if suggestions else []
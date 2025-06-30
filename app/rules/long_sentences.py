import re
import spacy
from bs4 import BeautifulSoup
import html
from spacy.language import Language
from spacy.tokens import Span

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

# Custom sentence segmentation component
@Language.component("custom_sentencizer")
def custom_sentencizer(doc):
    for i, token in enumerate(doc[:-1]):
        if token.text in {".", ":", "-"}:
            doc[i + 1].is_sent_start = True
    return doc

# Add custom sentencizer to the pipeline
nlp.add_pipe("custom_sentencizer", before="parser")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    doc = nlp(text_content)
    
    # Rule 1: Keep sentences under 25 words
    for sent in doc.sents:
        word_count = len([token for token in sent if not token.is_punct])
        if word_count > 25:
            clean_sentence = BeautifulSoup(sent.text.strip(), "html.parser").get_text()
            clean_sentence = html.unescape(clean_sentence)
            suggestions.append(f"Issue: Long sentence detected ({word_count} words)\nOriginal sentence: {clean_sentence}\nAI suggestion: Consider breaking this into shorter sentences (aim for under 25 words) for better readability.")

    # Rule 2: Use short words instead of long words
    # Convert <br/> tags to newlines
    text_content = text_content.replace("<br/>", "\n")

    # Remove HTML tags and decode entities
    text_content = BeautifulSoup(text_content, "html.parser").get_text()
    text_content = html.unescape(text_content)

    # Split text into individual words while preserving spaces properly
    words = text_content.split()  # This ensures 'uoeuser' and 'Password' are separate words

    long_word_pattern = r'^\w{15,}$'  # Match single long words

    for word in words:
        if re.match(long_word_pattern, word):  # Check only standalone words
            suggestions.append(f"Consider using shorter words instead of '{word}'")

    # Rule 3: Keep titles under 65 characters
    title_pattern = r'<title>(.*?)</title>'
    title_match = re.search(title_pattern, content, flags=re.IGNORECASE)
    if title_match:
        title_text = title_match.group(1)
        if len(title_text) > 65:
            clean_title = BeautifulSoup(title_text, "html.parser").get_text()
            clean_title = html.unescape(clean_title)
            suggestions.append(f"Consider shortening the title to under 65 characters: '{clean_title}'")
    
    return suggestions if suggestions else []
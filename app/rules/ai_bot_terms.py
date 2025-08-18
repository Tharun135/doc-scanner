import re
import spacy
from bs4 import BeautifulSoup
import html

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    # Rule 1: Use 'artificial intelligence (AI)' on first mention
    ai_mentions = [match.start() for match in re.finditer(r'\bAI\b', content)]
    if ai_mentions:
        first_ai_index = ai_mentions[0]
        prior_content = content[:first_ai_index]
        if not re.search(r'artificial intelligence', prior_content, flags=re.IGNORECASE):
            suggestions.append("Spell out 'artificial intelligence (AI)' on first mention.")

    # Rule 2: Use 'bot' instead of 'chatbot' or 'chatterbot' unless necessary
    bot_terms = {
        r'\bchatbot(s)?\b': "Use 'bot' instead of 'chatbot' unless necessary for clarity.",
        r'\bchatterbot(s)?\b': "Use 'bot' instead of 'chatterbot' unless necessary."
    }
    for pattern, suggestion_text in bot_terms.items():
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append("{suggestion_text}")

    # Rule 3: Use 'machine learning' without hyphens
    ml_matches = re.finditer(r'\bmachine-learning\b', content, flags=re.IGNORECASE)
    for match in ml_matches:
        suggestions.append("Use 'machine learning' without a hyphen.")

    # Rule 4: Avoid anthropomorphizing AI and bots
    anthropomorphic_verbs = ['think', 'feel', 'want', 'believe', 'desire', 'understand']
    for sentence in doc.sents:
        for token in sentence:
            if token.lemma_.lower() in anthropomorphic_verbs:
                subjects = [child for child in token.children if child.dep_ in ('nsubj', 'nsubjpass')]
                for subj in subjects:
                    if subj.text.lower() in ['ai', 'bot', 'algorithm', 'machine', 'system']:
                        suggestions.append(f"Avoid anthropomorphizing AI: '{sentence.text.strip()}'")
                        break

    # Rule 5: Use 'deep learning' without hyphens
    dl_matches = re.finditer(r'\bdeep-learning\b', content, flags=re.IGNORECASE)
    for match in dl_matches:
        suggestions.append("Use 'deep learning' without a hyphen.")

    # Rule 6: Avoid terms like 'singularity', 'superintelligence', 'technological singularity' unless appropriate
    speculative_terms = [r'\bsingularity\b', r'\bsuperintelligence\b', r'\btechnological singularity\b']
    for pattern in speculative_terms:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append("Avoid using speculative terms like '{match.group()}' unless in appropriate context.")

    # Rule 7: Use 'machine learning model' instead of 'AI model' when referring to machine learning
    ai_model_matches = re.finditer(r'\bAI model(s)?\b', content, flags=re.IGNORECASE)
    for match in ai_model_matches:
        suggestions.append("Consider using 'machine learning model' instead of '{match.group()}' if appropriate.")

    # Rule 8: Ensure correct use of 'cognitive services' for Microsoft offerings
    cs_matches = re.finditer(r'\bcognitive services\b', content, flags=re.IGNORECASE)
    for match in cs_matches:
        suggestions.append("Ensure 'cognitive services' refers to the correct Microsoft offerings and is capitalized properly if it's a proper noun.")
        
    return suggestions if suggestions else []

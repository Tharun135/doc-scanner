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
    logging.warning(f"RAG helper not available for {__name__}")

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)

    # Rule 1: Don't use 'handicap' except in proper names
    matches = re.finditer(r'\bhandicap\b', content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append(f"Avoid using '{match.group()}'; use 'accessible' or specify the disability.")

    # Rule 2: Don't use 'see', 'watch', or 'look at' to mean 'interact with'
    # verbs_to_avoid = ['see', 'watch', 'look at']
    # for sentence in doc.sents:
    #     for token in sentence:
    #         if token.lemma_.lower() in verbs_to_avoid:
    #             suggestions.append(f"Consider replacing '{token.text}' with 'interact with' or a similar term in: '{sentence.text.strip()}'")

    # Rule 3: Avoid negative terms like 'defect', 'disease', 'abnormal' when talking about disabilities
    negative_terms = [r'\bdefect\b', r'\bdisease\b', r'\babnormal\b']
    for pattern in negative_terms:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Avoid using negative terms like '{match.group()}' when discussing disabilities.")

    # Rule 4: Don't use terms that suggest pity, such as 'victim' or 'suffer from'
    pity_terms = [r'\bvictim\b', r'\bsuffer from\b']
    for pattern in pity_terms:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Avoid terms that suggest pity like '{match.group()}'; use neutral language.")

    # Rule 5: Use 'wheelchair user' instead of 'confined to a wheelchair' or 'wheelchair-bound'
    wheelchair_phrases = [r'\bconfined to a wheelchair\b', r'\bwheelchair[- ]bound\b']
    for pattern in wheelchair_phrases:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Use 'wheelchair user' instead of '{match.group()}'.")

    # Rule 6: Use person-first language
    person_first_patterns = [
        r'\bthe disabled person\b',
        r'\bthe blind\b',
        r'\bthe deaf\b',
        r'\bthe autistic\b',
    ]
    for pattern in person_first_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Use person-first language instead of '{match.group()}'; for example, 'person who is blind'.")

    return suggestions if suggestions else []
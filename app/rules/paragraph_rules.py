import spacy
from typing import List, Dict, Any
import re

nlp = spacy.load("en_core_web_sm")

def paragraph_rules(paragraph_text: str, p_doc, glossary, acronym_map, rules_ctx) -> List[Dict]:
    findings = []
    # 1. Topic sentence check
    first_sent = list(p_doc.sents)[0]
    if not any(t.pos_ == 'NOUN' for t in first_sent) or first_sent.text.strip().endswith('?'):
        findings.append({"type": "missing_or_weak_topic_sentence", "text": paragraph_text})
    # 2. Pronoun/coreference clarity
    pronouns = {'it', 'this', 'they', 'he', 'she', 'these', 'those', 'that'}
    for token in p_doc:
        if token.text.lower() in pronouns:
            if not any(t.pos_ == 'NOUN' for t in p_doc[max(0, token.i-5):token.i]):
                findings.append({"type": "unclear_pronoun_reference", "text": token.text, "context": paragraph_text})
    # 3. Tense/person consistency
    tenses = set()
    for token in p_doc:
        if token.pos_ == 'VERB':
            tenses.add(token.tag_)
    if len(tenses) > 1:
        findings.append({"type": "tense_inconsistency", "text": paragraph_text})
    # 4. Acronym first-use
    acronyms = re.findall(r'\b([A-Z]{2,})\b', paragraph_text)
    for acro in acronyms:
        if acro not in acronym_map:
            findings.append({"type": "acronym_without_definition", "text": acro, "context": paragraph_text})
    # 5. Paragraph too short/long
    if len(paragraph_text.split()) < 8:
        findings.append({"type": "paragraph_too_short", "text": paragraph_text})
    if len(paragraph_text.split()) > 120:
        findings.append({"type": "paragraph_too_long", "text": paragraph_text})
    # 6. Repeated sentence in paragraph
    sentences = [sent.text.strip().lower() for sent in p_doc.sents]
    seen = set()
    for s in sentences:
        if s in seen:
            findings.append({"type": "repeated_sentence_in_paragraph", "text": s})
        seen.add(s)
    # 7. List without intro
    if re.search(r'\n\s*[-*]\s', paragraph_text) and not re.search(r'(following|below|as shown)', paragraph_text, re.I):
        findings.append({"type": "list_without_intro", "text": paragraph_text})
    return findings

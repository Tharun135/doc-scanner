"""
Verb tense rules for enforcing simple, direct language.
Flags modal verbs and perfect tenses to encourage simpler writing.
"""

import spacy
from typing import List, Dict, Any
from .title_utils import is_title_or_heading
import re


def check_verb_tense(content: str, text_content: str) -> List[Dict[str, Any]]:
    """
    Check for complex verb forms that should be simplified:
    - Modal verbs: will, would, should, could, might, may
    - Perfect tenses: have/has/had + past participle
    - Future forms with "going to"
    """
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        return []
    
    suggestions = []
    doc = nlp(text_content)
    
    # Modal verbs to flag
    modal_verbs = {
        "will": "Use present tense for current facts or imperative for instructions",
        "would": "Use present tense or past tense directly",
        "should": "Use imperative form or present tense",
        "could": "Use 'can' or present tense",
        "might": "Use 'may' or present tense",
        "may": "Use 'can' for ability/permission, or present tense for facts"
    }
    
    # Markdown admonition patterns to exclude
    admonition_pattern = r'^\s*!{3}\s+(note|tip|info|warning|danger|bug|example|quote|abstract|todo|success|question|failure|important|hint)'
    
    # Markdown table patterns to exclude
    table_pattern = r'^\s*\|.*\|.*$'
    
    for sent in doc.sents:
        sentence_text = sent.text.strip()
        
        # Skip empty sentences
        if not sentence_text:
            continue
            
        # Skip titles and headings
        if is_title_or_heading(sentence_text):
            continue
            
        # Skip markdown admonitions
        if re.match(admonition_pattern, sentence_text, re.IGNORECASE):
            continue
            
        # Skip markdown table syntax
        if re.match(table_pattern, sentence_text):
            continue
        
        # Check for modal verbs
        for token in sent:
            if token.text.lower() in modal_verbs and token.pos_ == "VERB":
                suggestions.append({
                    "text": token.text,
                    "start": token.idx,
                    "end": token.idx + len(token.text),
                    "message": f"Modal verb '{token.text}': {modal_verbs[token.text.lower()]}",
                    "context": sentence_text,
                    "sentence": sentence_text,
                    "type": "verb_tense"
                })
        
        # Check for perfect tenses (have/has/had + past participle)
        for i, token in enumerate(sent):
            if token.lemma_ in ["have", "has", "had"] and i < len(sent) - 1:
                next_token = sent[i + 1]
                # Check if followed by past participle (VBN)
                if next_token.tag_ == "VBN":
                    suggestions.append({
                        "text": f"{token.text} {next_token.text}",
                        "start": token.idx,
                        "end": next_token.idx + len(next_token.text),
                        "message": f"Perfect tense '{token.text} {next_token.text}': Consider using simple past or present tense",
                        "context": sentence_text,
                        "sentence": sentence_text,
                        "type": "verb_tense"
                    })
        
        # Check for "going to" future constructions
        tokens = [token.text.lower() for token in sent]
        for i in range(len(tokens) - 2):
            if tokens[i] == "going" and tokens[i + 1] == "to":
                verb_phrase = f"{sent[i].text} {sent[i + 1].text} {sent[i + 2].text}"
                suggestions.append({
                    "text": verb_phrase,
                    "start": sent[i].idx,
                    "end": sent[i + 2].idx + len(sent[i + 2].text),
                    "message": f"Future construction '{verb_phrase}': Consider using simple present or imperative",
                    "context": sentence_text,
                    "sentence": sentence_text,
                    "type": "verb_tense"
                })
    
    return suggestions

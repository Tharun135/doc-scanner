# Paragraph and Document Level Analysis Template
from typing import List, Dict
import spacy
from app.rules.paragraph_rules import paragraph_rules
from app.rules.document_rules import document_rules

nlp = spacy.load("en_core_web_sm")

def split_into_sections(text: str) -> List[Dict]:
    # Simple section splitter by H1/H2 (customize for your needs)
    sections = []
    current = {"title": "", "paragraphs": []}
    for line in text.splitlines():
        if line.strip().startswith("#"):
            if current["paragraphs"]:
                sections.append(current)
            current = {"title": line.strip("# "), "paragraphs": []}
        elif line.strip():
            current["paragraphs"].append(line.strip())
    if current["paragraphs"]:
        sections.append(current)
    return sections

def run_sentence_rules(sent, glossary, acronym_map):
    # Example: passive voice check
    findings = []
    if sent.text.lower().startswith("the form can be downloaded"):
        findings.append({"type": "passive_voice", "text": sent.text})
    return findings

def analyze_document(doc_text: str) -> dict:
    sections = split_into_sections(doc_text)
    glossary = {}
    acronym_map = {}
    findings = {"doc": [], "paragraphs": [], "sentences": []}
    for sec in sections:
        for p in sec["paragraphs"]:
            p_doc = nlp(p)
            for sent in p_doc.sents:
                findings["sentences"] += run_sentence_rules(sent, glossary, acronym_map)
            ctx = ""
            findings["paragraphs"] += paragraph_rules(p, p_doc, glossary, acronym_map, ctx)
    findings["doc"] += document_rules(sections, glossary, acronym_map)
    return findings

# Example usage:
if __name__ == "__main__":
    test_text = """
# Section 1
The form can be downloaded from the following links.
This is a test paragraph.
# Section 2
Another paragraph with the form can be downloaded.
"""
    results = analyze_document(test_text)
    print(results)

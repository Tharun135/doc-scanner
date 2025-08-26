import re
from typing import List, Dict, Any

def document_rules(sections, glossary, acronym_map) -> List[Dict]:
    findings = []
    # 1. Section numbering monotonicity
    section_numbers = []
    for sec in sections:
        m = re.match(r'Section (\d+)', sec['title'])
        if m:
            section_numbers.append(int(m.group(1)))
    if section_numbers and section_numbers != sorted(section_numbers):
        findings.append({"type": "section_numbering_non_monotonic", "numbers": section_numbers})
    # 2. Figure/table callouts present and ordered
    figures = []
    tables = []
    for sec in sections:
        for p in sec["paragraphs"]:
            figures += re.findall(r'Figure (\d+)', p)
            tables += re.findall(r'Table (\d+)', p)
    if figures and figures != sorted(figures, key=int):
        findings.append({"type": "figure_callout_order_issue", "figures": figures})
    if tables and tables != sorted(tables, key=int):
        findings.append({"type": "table_callout_order_issue", "tables": tables})
    # 3. Required sections
    required_sections = ["Introduction", "Prerequisites", "Procedure", "Result"]
    found_titles = [sec['title'] for sec in sections]
    missing = [s for s in required_sections if s not in found_titles]
    if missing:
        findings.append({"type": "missing_required_sections", "missing": missing})
    # 4. Duplicate paragraph detection
    seen = set()
    for sec in sections:
        for p in sec["paragraphs"]:
            norm = ' '.join(p.lower().split())
            if norm in seen:
                findings.append({"type": "duplicate_paragraph", "text": p})
            seen.add(norm)
    # 5. Terminology consistency
    terms = {'adapter', 'adaptor', 'setup', 'set up', 'login', 'log in'}
    found_terms = set()
    for sec in sections:
        for p in sec["paragraphs"]:
            for term in terms:
                if term in p.lower():
                    found_terms.add(term)
    if len(found_terms) > 1:
        findings.append({"type": "terminology_inconsistency", "terms": list(found_terms)})
    # 6. Acronym dictionary
    all_acronyms = set()
    for sec in sections:
        for p in sec["paragraphs"]:
            all_acronyms.update(re.findall(r'\b([A-Z]{2,})\b', p))
    for acro in all_acronyms:
        if not any(acro in p for sec in sections for p in sec["paragraphs"] if acro in p and re.search(rf'{acro}.*?\(', p)):
            findings.append({"type": "acronym_not_defined_in_doc", "acronym": acro})
    # 7. Section title style
    for sec in sections:
        if not sec['title'].istitle():
            findings.append({"type": "section_title_not_title_case", "title": sec['title']})
    # 8. Section length
    for sec in sections:
        para_count = len(sec['paragraphs'])
        if para_count < 1:
            findings.append({"type": "section_too_short", "title": sec['title']})
        if para_count > 10:
            findings.append({"type": "section_too_long", "title": sec['title'], "count": para_count})
    # 9. Section order logic
    expected_order = [s for s in required_sections if s in found_titles]
    if found_titles[:len(expected_order)] != expected_order:
        findings.append({"type": "section_order_issue", "expected": expected_order, "found": found_titles})
    return findings

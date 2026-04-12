"""
Document Quality Reviewer  Structured JSON Analysis

Analyzes a document against a style guide and returns a structured JSON report
covering 9 quality dimensions:
  1. Document Structure
  2. Writing Style
  3. Tone and Voice
  4. UI Interaction Formatting
  5. Lists and Tables
  6. Headings
  7. Notices (MkDocs admonitions)
  8. Documentation Principles
  9. Naming Conventions

All analysis is deterministic (regex + spaCy + BeautifulSoup).
"""

import re
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Lazy-load spaCy
_nlp = None

def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm", disable=["ner", "textcat"])
            _nlp.max_length = 3_000_000
        except Exception as e:
            logger.warning(f"spaCy not available for quality reviewer: {e}")
            _nlp = False
    return _nlp if _nlp is not False else None


# 
# Constants
# 

FILLER_WORDS = [
    "therefore", "furthermore", "according", "for that reason",
    "moreover", "consequently", "hence", "thus", "additionally",
    "nevertheless", "nonetheless", "accordingly",
]

WEAK_CONSTRUCTIONS = [
    r"\bit is\b", r"\bthere is\b", r"\bthere are\b",
    r"\bit was\b", r"\bthere was\b", r"\bthere were\b",
]

NEGATIVE_CONTRACTIONS = [
    "don't", "can't", "won't", "shouldn't", "wouldn't",
    "couldn't", "isn't", "aren't", "doesn't", "hasn't",
    "haven't", "hadn't", "didn't", "mustn't",
]

VALID_NOTICE_TYPES = {"danger", "warning", "tip", "info", "note", "caution", "example", "question", "abstract", "bug", "success", "failure", "quote"}


# 
# Helper: split into sentences
# 

def _split_sentences(text: str) -> List[str]:
    """Split text into sentences using spaCy or regex fallback."""
    nlp = _get_nlp()
    if nlp:
        doc = nlp(text[:100_000])  # cap to avoid memory issues
        return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    # Fallback
    raw = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in raw if s.strip()]


def _is_passive(sentence: str) -> bool:
    """Detect passive voice using spaCy dependency parse."""
    nlp = _get_nlp()
    if not nlp:
        # Regex fallback: was/were/is/are/been + past participle
        return bool(re.search(r'\b(?:is|are|was|were|been|be|being)\s+\w+ed\b', sentence, re.IGNORECASE))
    doc = nlp(sentence)
    for token in doc:
        if token.dep_ in ("nsubjpass", "auxpass"):
            return True
    return False


def _get_tense(sentence: str) -> Optional[str]:
    """Return dominant tense: 'past', 'present', or None."""
    nlp = _get_nlp()
    if not nlp:
        return None
    doc = nlp(sentence)
    past = sum(1 for t in doc if t.tag_ in ("VBD", "VBN"))
    present = sum(1 for t in doc if t.tag_ in ("VBP", "VBZ", "VBG", "VB"))
    if past > present and past > 0:
        return "past"
    if present > past and present > 0:
        return "present"
    return None


# 
# 1. Document Structure
# 

def _check_structure(soup: BeautifulSoup, text: str) -> List[Dict[str, str]]:
    issues = []
    headings = soup.find_all(re.compile(r'^h[1-6]$'))

    # No headings at all
    if not headings:
        issues.append({
            "issue": "Document has no headings",
            "location": "Entire document",
            "suggestion": "Add descriptive headings (h1h6) to create a clear hierarchy."
        })
        return issues

    # Check for h1
    h1s = [h for h in headings if h.name == "h1"]
    if len(h1s) == 0:
        issues.append({
            "issue": "Missing top-level heading (h1)",
            "location": "Document start",
            "suggestion": "Add a single h1 heading at the top of the document."
        })
    elif len(h1s) > 1:
        issues.append({
            "issue": f"Multiple h1 headings ({len(h1s)})",
            "location": "Multiple locations",
            "suggestion": "Use a single h1 per document. Use h2 for subsections."
        })

    # Check heading hierarchy (no skipping levels)
    prev_level = 0
    for h in headings:
        level = int(h.name[1])
        if level > prev_level + 1 and prev_level > 0:
            issues.append({
                "issue": f"Heading level skipped: h{prev_level}  h{level}",
                "location": f"Heading: \"{h.get_text().strip()[:60]}\"",
                "suggestion": f"Use h{prev_level + 1} instead of h{level} to maintain hierarchy."
            })
        prev_level = level

    # Check for imperative headings (should be descriptive)
    imperative_starts = ["configure", "set up", "install", "create", "delete", "run", "open", "click"]
    for h in headings:
        h_text = h.get_text().strip()
        first_word = h_text.split()[0].lower() if h_text.split() else ""
        if first_word in imperative_starts:
            issues.append({
                "issue": f"Imperative heading: \"{h_text}\"",
                "location": f"Heading: \"{h_text[:60]}\"",
                "suggestion": f"Use descriptive form, e.g. \"{first_word.capitalize()}ing ...\" or a noun phrase."
            })

    # Check for very long sections (>500 words without a sub-heading)
    all_elements = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'div'])
    current_word_count = 0
    current_heading = "Document start"
    for el in all_elements:
        if el.name and el.name.startswith('h'):
            if current_word_count > 500:
                issues.append({
                    "issue": f"Very long section ({current_word_count} words) without sub-headings",
                    "location": f"After: \"{current_heading[:60]}\"",
                    "suggestion": "Break this section into smaller subsections with descriptive headings."
                })
            current_word_count = 0
            current_heading = el.get_text().strip()
        else:
            current_word_count += len(el.get_text().split())

    # Check last section
    if current_word_count > 500:
        issues.append({
            "issue": f"Very long section ({current_word_count} words) without sub-headings",
            "location": f"After: \"{current_heading[:60]}\"",
            "suggestion": "Break this section into smaller subsections with descriptive headings."
        })

    return issues


# 
# 2. Writing Style
# 

def _check_writing_style(text: str) -> List[Dict[str, str]]:
    issues = []
    sentences = _split_sentences(text)

    for sent in sentences:
        words = sent.split()
        word_count = len(words)

        # Long sentence (>20 words)
        if word_count > 20:
            issues.append({
                "sentence": sent.strip()[:120],
                "problem": f"Sentence too long ({word_count} words). Target: 20 words.",
                "suggested_revision": "Split into shorter sentences or remove non-essential words."
            })

        # Filler words
        sent_lower = sent.lower()
        for filler in FILLER_WORDS:
            if re.search(r'\b' + re.escape(filler) + r'\b', sent_lower):
                issues.append({
                    "sentence": sent.strip()[:120],
                    "problem": f"Filler word \"{filler}\" detected.",
                    "suggested_revision": f"Remove \"{filler}\" or rephrase for direct wording."
                })

        # Weak constructions
        for pattern in WEAK_CONSTRUCTIONS:
            if re.search(pattern, sent, re.IGNORECASE):
                match = re.search(pattern, sent, re.IGNORECASE)
                matched_text = match.group(0) if match else ""
                issues.append({
                    "sentence": sent.strip()[:120],
                    "problem": f"Weak construction \"{matched_text}\" detected.",
                    "suggested_revision": f"Rephrase to remove \"{matched_text}\" and use a concrete subject."
                })

    return issues


# 
# 3. Tone and Voice
# 

def _check_tone_and_voice(text: str) -> List[Dict[str, str]]:
    issues = []
    sentences = _split_sentences(text)

    for sent in sentences:
        # Passive voice
        if _is_passive(sent):
            issues.append({
                "sentence": sent.strip()[:120],
                "problem": "Passive voice detected.",
                "suggested_revision": "Rewrite in active voice."
            })

        # Past tense
        tense = _get_tense(sent)
        if tense == "past":
            issues.append({
                "sentence": sent.strip()[:120],
                "problem": "Past tense detected. Use present tense for instructions.",
                "suggested_revision": "Rewrite in present tense."
            })

        # Negative contractions
        sent_lower = sent.lower()
        for contraction in NEGATIVE_CONTRACTIONS:
            if contraction in sent_lower:
                expanded = {
                    "don't": "do not", "can't": "cannot", "won't": "will not",
                    "shouldn't": "should not", "wouldn't": "would not",
                    "couldn't": "could not", "isn't": "is not", "aren't": "are not",
                    "doesn't": "does not", "hasn't": "has not", "haven't": "have not",
                    "hadn't": "had not", "didn't": "did not", "mustn't": "must not",
                }.get(contraction, contraction.replace("n't", " not"))
                issues.append({
                    "sentence": sent.strip()[:120],
                    "problem": f"Negative contraction \"{contraction}\" detected.",
                    "suggested_revision": f"Use \"{expanded}\" instead of \"{contraction}\"."
                })

        # "please" usage
        if re.search(r'\bplease\b', sent_lower):
            issues.append({
                "sentence": sent.strip()[:120],
                "problem": "\"please\" detected  unnecessary in technical documentation.",
                "suggested_revision": "Remove \"please\" and use direct imperative."
            })

    return issues


# 
# 4. UI Interaction Formatting
# 

def _check_ui_formatting(text: str) -> List[Dict[str, str]]:
    issues = []

    # Detect UI button references without quotes (e.g. click OK  click "OK")
    button_pattern = r'\b(?:click|press|select|tap|choose)\s+([A-Z][A-Za-z ]{0,20})\b'
    for match in re.finditer(button_pattern, text):
        button_text = match.group(1).strip()
        full_match = match.group(0)
        # Check if already quoted
        start = match.start()
        surrounding = text[max(0, start-1):match.end()+1]
        if '"' not in surrounding and '"' not in surrounding and '"' not in surrounding:
            issues.append({
                "text": full_match,
                "problem": f"UI button \"{button_text}\" not enclosed in quotation marks.",
                "correction": f"Use \"{button_text}\" in quotation marks."
            })

    # Detect filenames not in backticks
    filename_pattern = r'(?<![`])\b[\w-]+\.(yml|yaml|json|xml|py|js|ts|txt|md|conf|cfg|ini|sh|bat|ps1|env|toml|css|html)\b(?![`])'
    for match in re.finditer(filename_pattern, text):
        fname = match.group(0)
        issues.append({
            "text": fname,
            "problem": f"Filename \"{fname}\" not formatted as inline code.",
            "correction": f"Use `{fname}` with backticks."
        })

    # Detect keyboard shortcuts not in ++key++ format
    shortcut_pattern = r'\b(Ctrl|Alt|Shift|Enter|Escape|Tab|Delete|Backspace|Home|End|Page Up|Page Down)\s*\+\s*([A-Za-z])\b'
    for match in re.finditer(shortcut_pattern, text):
        full = match.group(0)
        if '++' not in text[max(0, match.start()-2):match.end()+2]:
            issues.append({
                "text": full,
                "problem": f"Keyboard shortcut \"{full}\" not in ++key++ format.",
                "correction": f"Use `++{full.lower().replace(' ', '')}++` format."
            })

    return issues


# 
# 5. Lists and Tables
# 

def _check_lists_and_tables(soup: BeautifulSoup) -> List[Dict[str, str]]:
    issues = []

    # Check each list
    for list_el in soup.find_all(['ul', 'ol']):
        items = list_el.find_all('li', recursive=False)
        if not items:
            continue

        # Check if list is introduced (previous sibling should be a <p> or heading)
        prev = list_el.find_previous_sibling()
        if prev and prev.name not in ('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div'):
            issues.append({
                "location": f"List starting with \"{items[0].get_text().strip()[:50]}\"",
                "problem": "List not preceded by an introductory sentence or heading.",
                "suggestion": "Add an introductory sentence before the list."
            })

        # Check parallel structure (first word capitalization and ending punctuation)
        endings = []
        starts_with_verb = []
        for li in items:
            li_text = li.get_text().strip()
            if not li_text:
                continue
            # Track ending punctuation
            if li_text[-1] in '.!?':
                endings.append("period")
            else:
                endings.append("none")
            # Track if starts with verb (simple heuristic: -ing, imperative)
            first_word = li_text.split()[0].lower() if li_text.split() else ""
            starts_with_verb.append(first_word.endswith("ing") or first_word.endswith("e"))

        # Check punctuation consistency
        if endings and len(set(endings)) > 1:
            issues.append({
                "location": f"List starting with \"{items[0].get_text().strip()[:50]}\"",
                "problem": "Inconsistent punctuation across list items.",
                "suggestion": "Use consistent ending punctuation: all with periods or all without."
            })

    return issues


# 
# 6. Headings
# 

def _check_headings(soup: BeautifulSoup) -> List[Dict[str, str]]:
    issues = []
    headings = soup.find_all(re.compile(r'^h[1-6]$'))

    for h in headings:
        h_text = h.get_text().strip()
        if not h_text:
            continue

        # Too long (>8 words)
        words = h_text.split()
        if len(words) > 8:
            issues.append({
                "heading": h_text,
                "problem": f"Heading too long ({len(words)} words). Keep headings short and scannable.",
                "suggested_heading": " ".join(words[:8]) + "..."
            })

        # Check for -ing form for workflow headings
        workflow_indicators = ["how to", "steps for", "guide to", "procedure for", "process for"]
        h_lower = h_text.lower()
        if any(ind in h_lower for ind in workflow_indicators):
            first_word = words[0] if words else ""
            if not first_word.endswith("ing") and first_word.lower() not in ("how",):
                issues.append({
                    "heading": h_text,
                    "problem": "Workflow heading should use -ing form.",
                    "suggested_heading": f"Consider rephrasing with gerund form (e.g. \"Configuring...\", \"Setting up...\")."
                })

        # Title case check: only first word and proper nouns should be capitalized
        if len(words) > 1:
            over_capitalized = []
            for w in words[1:]:
                # Skip acronyms (all caps), proper nouns (hard to detect, skip 3 char words)
                if w.isupper() and len(w) <= 4:
                    continue  # Likely acronym
                if w[0].isupper() and w.lower() not in ("api", "ui", "url", "html", "css", "json", "xml"):
                    over_capitalized.append(w)
            if len(over_capitalized) > len(words) // 2:
                issues.append({
                    "heading": h_text,
                    "problem": "Heading uses Title Case. Use sentence case (capitalize only the first word and proper nouns).",
                    "suggested_heading": words[0] + " " + " ".join(w.lower() for w in words[1:])
                })

    return issues


# 
# 7. Notices (MkDocs admonitions)
# 

def _check_notices(text: str) -> List[Dict[str, str]]:
    issues = []

    # Find MkDocs admonition blocks: !!! type "Title"
    admonition_pattern = re.compile(r'^(!!!)\s*(\w*)\s*(".*?")?\s*$', re.MULTILINE)
    for match in admonition_pattern.finditer(text):
        notice_type = match.group(2).lower().strip() if match.group(2) else ""
        title = match.group(3) if match.group(3) else ""
        line_num = text[:match.start()].count('\n') + 1

        if not notice_type:
            issues.append({
                "location": f"Line {line_num}",
                "problem": "Admonition missing type (e.g. !!! warning \"Title\").",
                "suggestion": "Add a type: danger, warning, tip, info, or note."
            })
        elif notice_type not in VALID_NOTICE_TYPES:
            issues.append({
                "location": f"Line {line_num}: !!! {notice_type}",
                "problem": f"Unknown admonition type \"{notice_type}\".",
                "suggestion": f"Use a valid type: {', '.join(sorted(VALID_NOTICE_TYPES))}."
            })

        # Check for missing title
        if notice_type and not title:
            issues.append({
                "location": f"Line {line_num}: !!! {notice_type}",
                "problem": "Admonition missing a title.",
                "suggestion": f"Add a quoted title: !!! {notice_type} \"TITLE\"."
            })

    # Check for indentation of content after admonition
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('!!!'):
            # Next non-empty line should be indented with 4 spaces
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                if next_line.strip() and not next_line.startswith('    '):
                    issues.append({
                        "location": f"Line {i + 2}",
                        "problem": "Admonition content not indented with 4 spaces.",
                        "suggestion": "Indent admonition content with exactly 4 spaces."
                    })

    return issues


# 
# 8. Documentation Principles
# 

def _check_documentation_principles(soup: BeautifulSoup, text: str) -> List[Dict[str, str]]:
    issues = []
    text_lower = text.lower()

    # Check: Goal of action explained first
    paragraphs = soup.find_all('p')
    if paragraphs:
        first_para = paragraphs[0].get_text().strip().lower()
        first_200 = ' '.join(text.split()[:200]).lower()
        purpose_indicators = [
            'this document', 'this guide', 'this procedure', 'this section',
            'you will learn', 'shows how', 'explains how', 'describes',
            'overview of', 'introduction to', 'the purpose', 'use this'
        ]
        if not any(ind in first_200 for ind in purpose_indicators):
            issues.append({
                "issue": "Document does not clearly state its goal or purpose in the opening.",
                "location": "First paragraph",
                "suggestion": "Start with a purpose statement: 'This document describes...', 'This guide shows you how to...', etc."
            })

    # Check: Conditions stated before actions
    # Look for patterns like "Click X. Note: You must first..."
    condition_after = re.findall(
        r'(?:click|select|open|run|execute)\b[^.]*\.\s*(?:Note|Important|Warning|Make sure|Ensure|You must)',
        text, re.IGNORECASE
    )
    for match_text in condition_after[:3]:  # limit to 3
        issues.append({
            "issue": "Condition stated after the action.",
            "location": f"Near: \"{match_text[:80]}\"",
            "suggestion": "State conditions and prerequisites before the instruction step."
        })

    # Check: Procedures should use numbered lists
    has_sequential_language = any(word in text_lower for word in ['step 1', 'step 2', 'first,', 'then,', 'next,', 'finally,'])
    has_ordered_list = bool(soup.find_all('ol'))
    if has_sequential_language and not has_ordered_list:
        issues.append({
            "issue": "Sequential instructions found but no numbered list used.",
            "location": "Multiple locations with sequential language",
            "suggestion": "Convert step-by-step instructions into a numbered (ordered) list."
        })

    # Check: Code examples
    code_refs = len(re.findall(r'`[^`]+`', text))
    code_blocks = len(re.findall(r'```', text)) // 2
    if code_refs > 5 and code_blocks == 0:
        issues.append({
            "issue": "Many inline code references but no complete code examples.",
            "location": "Entire document",
            "suggestion": "Add complete code examples in fenced code blocks (```) to illustrate usage."
        })

    return issues


# 
# 9. Naming Conventions
# 

def _check_naming_conventions(text: str) -> List[Dict[str, str]]:
    issues = []

    # Find filenames in the text
    filename_pattern = r'(?:`([^`]+\.[a-zA-Z0-9]+)`|(?:^|\s)([\w\-.]+\.[a-zA-Z0-9]{1,5})(?:\s|$|[,;:]))'
    for match in re.finditer(filename_pattern, text):
        fname = match.group(1) or match.group(2)
        if not fname:
            continue

        # Skip URLs
        if '/' in fname and not fname.startswith('.'):
            continue
        # Skip version numbers like v1.0
        if re.match(r'^v?\d+\.\d+', fname):
            continue

        name_part = fname.rsplit('.', 1)[0] if '.' in fname else fname

        # Check: contains spaces
        if ' ' in fname:
            issues.append({
                "issue": f"Filename \"{fname}\" contains spaces.",
                "location": f"Filename: {fname}",
                "suggestion": f"Replace spaces with hyphens: \"{fname.replace(' ', '-')}\"."
            })

        # Check: uppercase letters
        if name_part != name_part.lower():
            issues.append({
                "issue": f"Filename \"{fname}\" contains uppercase letters.",
                "location": f"Filename: {fname}",
                "suggestion": f"Use lowercase: \"{fname.lower()}\"."
            })

        # Check: dots in name (besides extension)
        if name_part.count('.') > 0:
            issues.append({
                "issue": f"Filename \"{fname}\" contains dots in the name (besides the extension).",
                "location": f"Filename: {fname}",
                "suggestion": f"Use hyphens instead of dots: \"{name_part.replace('.', '-')}.{fname.rsplit('.', 1)[-1]}\"."
            })

        # Check: too long (>30 chars)
        if len(name_part) > 30:
            issues.append({
                "issue": f"Filename \"{fname}\" is too long ({len(name_part)} chars).",
                "location": f"Filename: {fname}",
                "suggestion": "Shorten the filename to be more concise (30 characters)."
            })

    return issues


# 
# Score Calculation
# 

def _calculate_score(
    structure: list,
    style: list,
    tone: list,
    formatting: list,
    lists: list,
    headings: list,
    notices: list,
    principles: list,
    naming: list,
) -> int:
    """Calculate a weighted quality score out of 100."""
    # Weights for each category (higher = more impactful)
    weights = {
        "structure": 3,
        "style": 2,
        "tone": 2,
        "formatting": 1,
        "lists": 1,
        "headings": 1.5,
        "notices": 1,
        "principles": 2.5,
        "naming": 0.5,
    }

    total_weighted_issues = (
        len(structure) * weights["structure"]
        + len(style) * weights["style"]
        + len(tone) * weights["tone"]
        + len(formatting) * weights["formatting"]
        + len(lists) * weights["lists"]
        + len(headings) * weights["headings"]
        + len(notices) * weights["notices"]
        + len(principles) * weights["principles"]
        + len(naming) * weights["naming"]
    )

    # Score: 100 minus deductions, floored at 0
    deduction = min(total_weighted_issues * 2, 100)
    return max(0, round(100 - deduction))


# 
# Top Recommendations
# 

def _generate_recommendations(
    structure: list,
    style: list,
    tone: list,
    formatting: list,
    lists: list,
    headings: list,
    notices: list,
    principles: list,
    naming: list,
) -> List[str]:
    """Generate top 5 actionable recommendations based on detected issues."""
    recommendations = []

    # Priority order based on impact
    if structure:
        recommendations.append(
            f"Fix {len(structure)} structural issue(s)  improve heading hierarchy and section organization."
        )
    if principles:
        recommendations.append(
            f"Address {len(principles)} documentation principle violation(s)  ensure goal-first writing and proper step formatting."
        )
    if style:
        recommendations.append(
            f"Improve writing style  {len(style)} issue(s) found. Shorten sentences and remove filler words."
        )
    if tone:
        recommendations.append(
            f"Fix tone and voice  {len(tone)} issue(s). Use present tense, active voice, and avoid contractions."
        )
    if headings:
        recommendations.append(
            f"Improve {len(headings)} heading(s)  use sentence case and keep headings short."
        )
    if formatting:
        recommendations.append(
            f"Fix {len(formatting)} formatting issue(s)  apply correct formatting for UI elements, filenames, and commands."
        )
    if lists:
        recommendations.append(
            f"Fix {len(lists)} list issue(s)  ensure parallel structure and consistent punctuation."
        )
    if notices:
        recommendations.append(
            f"Fix {len(notices)} notice/admonition issue(s)  use correct MkDocs syntax."
        )
    if naming:
        recommendations.append(
            f"Fix {len(naming)} filename naming issue(s)  use lowercase, no spaces."
        )

    # Return top 5
    return recommendations[:5]


# 
# Main Entry Point
# 

def review_document_quality(document_text: str, style_guide_text: str = "") -> Dict[str, Any]:
    """
    Analyze a document against style guide rules and return structured JSON report.

    Args:
        document_text: The raw document text (may contain markdown/HTML)
        style_guide_text: The style guide content (for future custom rule parsing)

    Returns:
        Structured dict matching the JSON schema with all 9 review dimensions.
    """
    logger.info(" Starting structured document quality review...")

    # Parse HTML/Markdown content
    # If the text looks like markdown, convert heading markers
    html_text = document_text
    if not re.search(r'<[a-z]+', document_text):
        # Simple markdown-to-HTML for headings and lists
        lines = document_text.split('\n')
        html_lines = []
        in_list = False
        for line in lines:
            stripped = line.strip()
            # Headings
            heading_match = re.match(r'^(#{1,6})\s+(.*)', stripped)
            if heading_match:
                level = len(heading_match.group(1))
                title = heading_match.group(2)
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h{level}>{title}</h{level}>')
            elif stripped.startswith('- ') or stripped.startswith('* '):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                html_lines.append(f'<li>{stripped[2:]}</li>')
            elif re.match(r'^\d+\.\s+', stripped):
                if not in_list:
                    html_lines.append('<ol>')
                    in_list = True
                # Extract text after leading numbering (e.g. "1. foo"  "foo")
                numbered_prefix = re.compile(r'^\d+\.\s+')
                list_item_text = numbered_prefix.sub('', stripped)
                html_lines.append(f'<li>{list_item_text}</li>')
            elif stripped:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<p>{stripped}</p>')
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
        if in_list:
            html_lines.append('</ul>')
        html_text = '\n'.join(html_lines)

    soup = BeautifulSoup(html_text, "html.parser")
    plain_text = soup.get_text(separator='\n')

    # Run all 9 checks
    structure_issues = _check_structure(soup, plain_text)
    style_violations = _check_writing_style(plain_text)
    tone_issues = _check_tone_and_voice(plain_text)
    formatting_issues = _check_ui_formatting(document_text)  # Use original to preserve backticks
    list_issues = _check_lists_and_tables(soup)
    heading_issues = _check_headings(soup)
    notice_issues = _check_notices(document_text)  # Use original to preserve !!!
    principle_violations = _check_documentation_principles(soup, plain_text)
    naming_issues = _check_naming_conventions(document_text)

    # Calculate score
    score = _calculate_score(
        structure_issues, style_violations, tone_issues,
        formatting_issues, list_issues, heading_issues,
        notice_issues, principle_violations, naming_issues
    )

    # Generate recommendations
    recommendations = _generate_recommendations(
        structure_issues, style_violations, tone_issues,
        formatting_issues, list_issues, heading_issues,
        notice_issues, principle_violations, naming_issues
    )

    total_issues = (
        len(structure_issues) + len(style_violations) + len(tone_issues)
        + len(formatting_issues) + len(list_issues) + len(heading_issues)
        + len(notice_issues) + len(principle_violations) + len(naming_issues)
    )

    logger.info(f" Quality review complete: score={score}, issues={total_issues}")

    return {
        "document_score": score,
        "structure_issues": structure_issues,
        "style_violations": style_violations,
        "tone_and_voice_issues": tone_issues,
        "formatting_issues": formatting_issues,
        "list_or_table_issues": list_issues,
        "heading_issues": heading_issues,
        "notice_issues": notice_issues,
        "documentation_principle_violations": principle_violations,
        "naming_issues": naming_issues,
        "top_recommendations": recommendations,
    }


# 
# RAG Integration - Ingest quality issues as style constraints
# 

def ingest_quality_issues_to_rag(review_result, doc_id):
    """
    Ingest quality review violations into the RAG knowledge base as style constraints.

    Each violation is stored as a Golden Rule via ingest_correction(). When the AI
    suggestion engine later retrieves context for a sentence in this document, it finds
    these constraints and uses them to produce more targeted, compliant rewrites.

    Args:
        review_result: The dict returned by review_document_quality()
        doc_id: Stable identifier for the source document (e.g. filename)

    Returns:
        Number of constraint documents ingested
    """
    import logging as _log
    _logger = _log.getLogger(__name__)

    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.services.enrichment import ingest_correction
    except ImportError:
        try:
            from .services.enrichment import ingest_correction
        except ImportError:
            _logger.warning("RAG enrichment service unavailable - skipping quality ingestion")
            return 0

    ingested = 0
    score = review_result.get("document_score", 100)

    # (result_key, issue_type_label, field_with_problem_text)
    CATEGORY_MAP = [
        ("style_violations",                  "Style Violation",           "problem"),
        ("tone_and_voice_issues",             "Tone and Voice",            "problem"),
        ("formatting_issues",                 "UI Formatting",             "problem"),
        ("structure_issues",                  "Document Structure",        "issue"),
        ("heading_issues",                    "Heading Quality",           "problem"),
        ("notice_issues",                     "Admonition Syntax",         "problem"),
        ("documentation_principle_violations","Documentation Principle",   "issue"),
        ("list_or_table_issues",              "List Quality",              "problem"),
        ("naming_issues",                     "Naming Convention",         "issue"),
    ]

    for result_key, issue_type, text_field in CATEGORY_MAP:
        items = review_result.get(result_key, [])
        for item in items:
            if not isinstance(item, dict):
                continue
            problem_text = item.get(text_field, "")
            fix_text = (
                item.get("suggested_revision")
                or item.get("suggestion")
                or item.get("correction")
                or item.get("suggested_heading")
                or "Apply the relevant style guide rule."
            )
            sentence = (
                item.get("sentence")
                or item.get("text")
                or item.get("heading")
                or item.get("location", "")
            )
            if not problem_text:
                continue

            if sentence:
                original = (
                    "[" + issue_type + "] In '" + doc_id + "': "
                    + problem_text + " Example: " + str(sentence)[:120]
                )
            else:
                original = "[" + issue_type + "] " + problem_text

            try:
                success = ingest_correction(
                    original=original,
                    corrected=fix_text,
                    issue_type=issue_type,
                )
                if success:
                    ingested += 1
            except Exception as exc:
                _logger.warning("Failed to ingest quality constraint: %s", exc)

    # Document-level summary constraint
    if review_result.get("top_recommendations"):
        recs = "\n".join("- " + r for r in review_result["top_recommendations"])
        doc_summary = (
            "Document quality review for '" + doc_id + "' (score: "
            + str(score) + "/100).\nKey issues:\n" + recs
        )
        try:
            success = ingest_correction(
                original=doc_summary,
                corrected=(
                    "Quality score: " + str(score) + "/100. "
                    "Address the issues above to improve clarity and compliance."
                ),
                issue_type="Document Quality Summary",
            )
            if success:
                ingested += 1
        except Exception as exc:
            _logger.warning("Failed to ingest document quality summary: %s", exc)

    _logger.info("RAG: Ingested %d quality constraints for '%s'", ingested, doc_id)
    return ingested

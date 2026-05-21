"""
Document Parser — Section-Aware Structural Model Builder
=========================================================

Consumes parsed HTML and produces a DocumentModel: a section tree with
rich metadata. All downstream analyzers (section, cross-reference,
consistency, IA, flow) consume this model — never raw HTML.

Deterministic. No LLM.
"""

from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

# Keywords that suggest a section contains warnings / risky operations
_WARNING_KEYWORDS = re.compile(
    r'\b(warning|caution|danger|do not|do_not|must not|never|critical|important)\b',
    re.IGNORECASE,
)

# Keywords that suggest a section contains numbered steps
_STEP_KEYWORDS = re.compile(
    r'\b(step\s*\d|click|select|enter|type|press|enable|disable|configure|run|execute)\b',
    re.IGNORECASE,
)

# Weak/generic titles to flag
_WEAK_TITLES = frozenset({
    "introduction", "overview", "general", "misc", "miscellaneous",
    "other", "additional", "more", "information", "details", "notes",
    "summary", "background", "about",
})

# Abbreviation pattern: 2-8 uppercase letters, optionally with digits/spaces
_ABBREV_PATTERN = re.compile(r'\b([A-Z]{2,8}(?:\s[A-Z]{2,8})*)\b')

# Expansion pattern: "Full Name (ABBR)" or "ABBR (Full Name)"
_EXPANSION_PATTERN = re.compile(
    r'([A-Za-z][a-z]+(?:\s+[A-Za-z][a-z]+)+)\s*\(([A-Z]{2,8})\)'
    r'|([A-Z]{2,8})\s*\(([A-Za-z][a-z]+(?:\s+[A-Za-z][a-z]+)+)\)'
)


@dataclass
class Section:
    """A single section of the document, anchored to a heading."""
    id: str                              # Unique slug, e.g. "h2_installation"
    level: int                           # Heading depth: h1=1, h2=2, …
    title: str                           # Plain text of the heading
    parent_id: Optional[str]             # Parent section id, or None for top-level
    sentences: List[str] = field(default_factory=list)
    word_count: int = 0
    has_numbered_list: bool = False
    has_bullet_list: bool = False
    has_code_blocks: bool = False
    has_warnings: bool = False
    has_table: bool = False
    has_step_content: bool = False
    raw_text: str = ""                   # Full plain text of the section body


@dataclass
class DocumentModel:
    """
    Complete structural model of the document.

    Built once from parsed HTML; passed to every analyzer.
    """
    sections: List[Section] = field(default_factory=list)
    section_index: Dict[str, Section] = field(default_factory=dict)   # id → Section
    title_index: Dict[str, Section] = field(default_factory=dict)     # normalized_title → Section

    # Whole-document term frequency (lowercased)
    term_frequency: Dict[str, int] = field(default_factory=dict)

    # Abbreviation registry: abbr → (expansion_text, section_id_where_first_seen)
    abbreviations: Dict[str, Tuple[str, str]] = field(default_factory=dict)

    # Ordered list of heading titles (for IA ordering analysis)
    headings_in_order: List[str] = field(default_factory=list)

    # Document metadata
    doc_type: str = "unknown"            # from document_review_gate
    review_modes: List[str] = field(default_factory=list)
    filename: str = ""
    total_word_count: int = 0

    # All body sentences in document order (for flow analysis)
    all_sentences_flat: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_document(
    html_content: str,
    filename: str = "",
    doc_type: str = "unknown",
    review_modes: Optional[List[str]] = None,
) -> DocumentModel:
    """
    Parse HTML content into a DocumentModel.

    Args:
        html_content: Full HTML string from parse_file().
        filename: Original filename (for metadata).
        doc_type: Pre-detected doc type from document_review_gate.
        review_modes: List of user-selected review modes.

    Returns:
        DocumentModel populated with section tree and indexes.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    model = DocumentModel(
        doc_type=doc_type,
        review_modes=review_modes or [],
        filename=filename,
    )

    sections = _build_section_tree(soup)
    model.sections = sections

    # Build indexes
    for sec in sections:
        model.section_index[sec.id] = sec
        norm_title = _normalize_title(sec.title)
        model.title_index[norm_title] = sec
        model.headings_in_order.append(sec.title)

    # Build term frequency from all section text
    all_text_parts: List[str] = []
    for sec in sections:
        all_text_parts.append(sec.raw_text)
        model.all_sentences_flat.extend(sec.sentences)

    full_text = " ".join(all_text_parts)
    model.term_frequency = _build_term_frequency(full_text)
    model.total_word_count = len(full_text.split())

    # Build abbreviation registry
    model.abbreviations = _extract_abbreviations(sections)

    logger.info(
        f"DocumentParser: {len(sections)} sections, "
        f"{model.total_word_count} words, "
        f"{len(model.abbreviations)} abbreviations detected"
    )
    return model


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_section_tree(soup: BeautifulSoup) -> List[Section]:
    """
    Walk the HTML element tree and group content under heading anchors.

    Strategy:
    - When a heading (h1–h6) is encountered, start a new Section.
    - All subsequent non-heading elements belong to that section until
      a new heading of equal or higher level appears.
    - Headings with no body content get an empty section (for SEC-004).
    """
    sections: List[Section] = []
    current_section: Optional[Section] = None
    section_counter: Dict[int, int] = {}  # level → count for unique IDs
    parent_stack: List[Section] = []       # stack for tracking parent hierarchy

    all_elements = soup.find_all(
        ['h1', 'h2', 'h3', 'h4', 'h5', 'h6',
         'p', 'li', 'ol', 'ul', 'pre', 'code',
         'table', 'blockquote', 'div']
    )

    for el in all_elements:
        tag = el.name

        if tag in HEADING_TAGS:
            # Save previous section
            if current_section is not None:
                _finalize_section(current_section)
                sections.append(current_section)

            level = int(tag[1])
            section_counter[level] = section_counter.get(level, 0) + 1
            title = el.get_text(separator=" ").strip()
            sec_id = f"h{level}_{_slugify(title)}_{section_counter[level]}"

            # Determine parent
            # Pop stack until we find a parent with a lower level number
            while parent_stack and parent_stack[-1].level >= level:
                parent_stack.pop()
            parent_id = parent_stack[-1].id if parent_stack else None

            current_section = Section(
                id=sec_id,
                level=level,
                title=title,
                parent_id=parent_id,
            )
            parent_stack.append(current_section)

        elif current_section is not None:
            # Accumulate body content into current section
            text = el.get_text(separator=" ").strip()
            if not text:
                continue

            if tag == 'ol':
                current_section.has_numbered_list = True
            elif tag == 'ul':
                current_section.has_bullet_list = True
            elif tag in ('pre', 'code'):
                current_section.has_code_blocks = True
            elif tag == 'table':
                current_section.has_table = True

            # Avoid double-counting nested elements (only leaf text blocks)
            # We skip <li> text if the parent <ul>/<ol> will be processed
            # But since BeautifulSoup traversal may repeat, we deduplicate
            # by only collecting text from leaf-ish elements
            if tag in ('p', 'li', 'blockquote', 'td', 'th'):
                if text:
                    current_section.raw_text += " " + text
                    # Split into simple sentences for storage
                    sents = _split_sentences(text)
                    current_section.sentences.extend(sents)

    # Don't forget the last section
    if current_section is not None:
        _finalize_section(current_section)
        sections.append(current_section)

    # Handle documents with no headings — treat entire doc as one implicit section
    if not sections:
        body_text = soup.get_text(separator=" ").strip()
        if body_text:
            implicit = Section(
                id="implicit_body",
                level=0,
                title="[Document Body]",
                parent_id=None,
                raw_text=body_text,
                sentences=_split_sentences(body_text),
            )
            _finalize_section(implicit)
            sections.append(implicit)

    return sections


def _finalize_section(sec: Section) -> None:
    """Compute derived fields once the section body is complete."""
    sec.raw_text = sec.raw_text.strip()
    sec.word_count = len(sec.raw_text.split()) if sec.raw_text else 0

    if _WARNING_KEYWORDS.search(sec.raw_text):
        sec.has_warnings = True

    if _STEP_KEYWORDS.search(sec.raw_text):
        sec.has_step_content = True


def _build_term_frequency(text: str) -> Dict[str, int]:
    """Return lowercased word → count across the full document."""
    freq: Dict[str, int] = {}
    for word in re.findall(r'\b[a-zA-Z][a-zA-Z\-]{2,}\b', text):
        key = word.lower()
        freq[key] = freq.get(key, 0) + 1
    return freq


def _extract_abbreviations(sections: List[Section]) -> Dict[str, Tuple[str, str]]:
    """
    Build abbreviation → (expansion, section_id) map.

    Detects patterns like:
      "OPC Unified Architecture (OPC UA)"
      "OPC UA (OPC Unified Architecture)"
    """
    abbrevs: Dict[str, Tuple[str, str]] = {}
    for sec in sections:
        for match in _EXPANSION_PATTERN.finditer(sec.raw_text):
            if match.group(1) and match.group(2):
                full, abbr = match.group(1).strip(), match.group(2).strip()
            else:
                abbr, full = match.group(3).strip(), match.group(4).strip()
            if abbr not in abbrevs:
                abbrevs[abbr] = (full, sec.id)
    return abbrevs


def _split_sentences(text: str) -> List[str]:
    """Simple sentence splitter (regex-based fallback)."""
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [p.strip() for p in parts if p.strip()]


def _normalize_title(title: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    return re.sub(r'[^a-z0-9\s]', '', title.lower()).strip()


def _slugify(text: str) -> str:
    """Convert heading text to a safe slug for use as section ID."""
    slug = re.sub(r'[^a-z0-9]+', '_', text.lower())
    return slug[:40].strip('_') or "section"

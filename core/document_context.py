"""
Document-level context for whole-manual understanding.

This module provides the DocumentContext dataclass that captures document-wide signals
that individual sentences cannot see. Used in PASS 0 of the two-pass architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DocumentContext:
    """
    Document-wide understanding extracted before sentence analysis.
    
    This is NOT for rewriting. It's for:
    - Guiding sentence-level decisions
    - Enforcing document-level rules
    - Providing structural context
    - Detecting consistency issues
    """
    
    # Document classification
    doc_type: str  # manual | api | safety | ui | concept | procedure | reference
    primary_goal: str  # instruct | explain | reference | warn
    audience_level: str  # novice | intermediate | expert | mixed
    
    # Rewrite governance
    rewrite_sensitivity: str  # low | medium | high | critical
    forbidden_sections: List[str] = field(default_factory=list)  # Section names where rewrites are blocked
    forbidden_spans: List[tuple] = field(default_factory=list)  # (start_idx, end_idx) in document
    
    # Terminology and consistency
    terminology_map: Dict[str, str] = field(default_factory=dict)  # {variant: canonical_form}
    acronyms: Dict[str, str] = field(default_factory=dict)  # {acronym: definition}
    defined_terms: List[str] = field(default_factory=list)  # Terms explicitly defined in doc
    
    # Structure metadata
    headings: List[Dict[str, any]] = field(default_factory=list)  # [{text, level, position}]
    sections: List[Dict[str, any]] = field(default_factory=list)  # [{name, start, end, type}]
    has_toc: bool = False
    has_index: bool = False
    
    # Content characteristics
    total_sentences: int = 0
    total_words: int = 0
    avg_sentence_length: float = 0.0
    dominant_tense: Optional[str] = None  # present | past | future | mixed
    
    # Document-level issues (NOT rewrites)
    structure_issues: List[str] = field(default_factory=list)
    consistency_issues: List[str] = field(default_factory=list)
    missing_elements: List[str] = field(default_factory=list)
    
    def is_rewrite_allowed_in_section(self, section_name: str) -> bool:
        """Check if rewriting is allowed in the given section."""
        return section_name not in self.forbidden_sections
    
    def is_rewrite_allowed_at_position(self, position: int) -> bool:
        """Check if rewriting is allowed at the given document position."""
        for start, end in self.forbidden_spans:
            if start <= position <= end:
                return False
        return True
    
    def get_canonical_term(self, term: str) -> str:
        """Get the canonical form of a term, or return the original if not found."""
        return self.terminology_map.get(term.lower(), term)
    
    def is_high_sensitivity(self) -> bool:
        """Check if document requires high sensitivity for rewrites."""
        return self.rewrite_sensitivity in ['high', 'critical']
    
    def add_structure_issue(self, issue: str):
        """Add a document-level structure issue."""
        if issue not in self.structure_issues:
            self.structure_issues.append(issue)
    
    def add_consistency_issue(self, issue: str):
        """Add a document-level consistency issue."""
        if issue not in self.consistency_issues:
            self.consistency_issues.append(issue)
    
    def add_missing_element(self, element: str):
        """Add a missing document element."""
        if element not in self.missing_elements:
            self.missing_elements.append(element)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'doc_type': self.doc_type,
            'primary_goal': self.primary_goal,
            'audience_level': self.audience_level,
            'rewrite_sensitivity': self.rewrite_sensitivity,
            'forbidden_sections': self.forbidden_sections,
            'terminology_map': self.terminology_map,
            'acronyms': self.acronyms,
            'total_sentences': self.total_sentences,
            'total_words': self.total_words,
            'avg_sentence_length': self.avg_sentence_length,
            'dominant_tense': self.dominant_tense,
            'structure_issues': self.structure_issues,
            'consistency_issues': self.consistency_issues,
            'missing_elements': self.missing_elements,
            'has_toc': self.has_toc,
            'has_index': self.has_index,
        }
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the document context."""
        lines = [
            f"Document Type: {self.doc_type}",
            f"Goal: {self.primary_goal}",
            f"Audience: {self.audience_level}",
            f"Rewrite Sensitivity: {self.rewrite_sensitivity}",
            f"Total Sentences: {self.total_sentences}",
            f"Avg Sentence Length: {self.avg_sentence_length:.1f} words",
        ]
        
        if self.forbidden_sections:
            lines.append(f"Forbidden Sections: {', '.join(self.forbidden_sections)}")
        
        if self.structure_issues:
            lines.append(f"Structure Issues: {len(self.structure_issues)}")
        
        if self.consistency_issues:
            lines.append(f"Consistency Issues: {len(self.consistency_issues)}")
        
        return "\n".join(lines)

"""
Document Review Gate - Reviewer-First Analysis

⚠️ CRITICAL ARCHITECTURAL CONSTRAINT:
This module identifies document-level issues ONLY.
It must NOT generate solutions, phrasing, or fixes.
All remediation happens downstream.

This gate determines whether sentence-level analysis is warranted.
It is not a second reviewer - it is a gating function.

This module implements document-level understanding BEFORE sentence analysis.
It answers: "What would a human reviewer notice first?"

Philosophy:
- Stop early if document goal is unclear
- Identify structural problems before sentence problems  
- Gate sentence analysis behind document understanding
- Reduce noise by an order of magnitude

Flow:
1. Document goal clarity
2. Document type detection (procedure/concept/reference)
3. Structural completeness
4. Confusion zone identification

Only if these pass do we proceed to sentence-level analysis.
"""

from dataclasses import dataclass
from typing import List, Optional
from bs4 import BeautifulSoup
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class DocumentIssue:
    """A reviewer-style document-level issue."""
    id: str
    severity: str  # "blocking", "major", "minor"
    message: str
    reviewer_question: Optional[str] = None  # What a reviewer would ask
    section: Optional[str] = None  # Where in document


@dataclass
class DocumentReviewResult:
    """Result of document-level review gate."""
    blocking: bool
    document_type: str  # "procedure", "concept", "reference", "unknown"
    issues: List[DocumentIssue]
    flagged_sections: List[str]  # Sections that need deep analysis
    analysis_scope: str  # "full", "targeted", "minimal"
    
    def to_ui(self):
        """Convert to UI-friendly format."""
        return {
            "blocking": self.blocking,
            "document_type": self.document_type,
            "issues": [
                {
                    "id": issue.id,
                    "severity": issue.severity,
                    "message": issue.message,
                    "reviewer_question": issue.reviewer_question,
                    "section": issue.section
                }
                for issue in self.issues
            ],
            "analysis_scope": self.analysis_scope,
            "guidance": self._get_guidance()
        }
    
    def _get_guidance(self):
        """Provide reviewer-style guidance based on issues."""
        if self.blocking:
            return "As a reviewer, I need to understand the document's purpose before I can provide detailed feedback."
        elif len(self.issues) > 0:
            return "The document structure has some areas that may confuse readers. I'll focus my detailed review there."
        else:
            return "Document structure looks clear. I'll review for clarity and precision."


def run_document_review_gate(html_content: str, filename: str = "") -> DocumentReviewResult:
    """
    Primary document review gate.
    
    Answers the questions a human reviewer asks FIRST:
    1. What is this document trying to achieve?
    2. What type of document is this?
    3. Is the structure fundamentally sound?
    4. Where will users get confused?
    
    Args:
        html_content: Parsed HTML content
        filename: Original filename (helps with context)
    
    Returns:
        DocumentReviewResult with blocking flag and issues
    """
    issues = []
    soup = BeautifulSoup(html_content, "html.parser")
    text_content = soup.get_text()
    
    logger.info(f"🚧 Document Review Gate: Analyzing {filename}")
    
    # Question 1: Is the document goal clear?
    if not has_clear_goal(soup, text_content):
        issues.append(DocumentIssue(
            id="DOC_GOAL_UNCLEAR",
            severity="blocking",
            message="As a user, I'm not sure what this document helps me achieve.",
            reviewer_question="What am I supposed to learn or do after reading this?"
        ))
    
    # Question 2: What type of document is this?
    doc_type = detect_document_type(soup, text_content)
    logger.info(f"📋 Detected document type: {doc_type}")
    
    # Question 3: Type-specific structural checks
    if doc_type == "procedure":
        procedure_issues = check_procedure_structure(soup, text_content)
        issues.extend(procedure_issues)
    elif doc_type == "concept":
        concept_issues = check_concept_structure(soup, text_content)
        issues.extend(concept_issues)
    
    # Question 4: Identify confusion zones
    flagged_sections = identify_confusion_zones(soup, text_content)
    
    # Determine analysis scope
    analysis_scope = determine_analysis_scope(issues, flagged_sections)
    
    # Check if any issue is blocking
    blocking = any(issue.severity == "blocking" for issue in issues)
    
    result = DocumentReviewResult(
        blocking=blocking,
        document_type=doc_type,
        issues=issues,
        flagged_sections=flagged_sections,
        analysis_scope=analysis_scope
    )
    
    if blocking:
        logger.warning(f"🚫 Blocking issue found - stopping detailed analysis")
    else:
        logger.info(f"✅ Document gate passed - proceeding with {analysis_scope} analysis")
    
    return result


def has_clear_goal(soup: BeautifulSoup, text: str) -> bool:
    """
    Check if document goal is clear.
    
    A document has a clear goal if:
    - It has a meaningful title/heading
    - Early content indicates purpose
    - Not just a wall of text
    """
    # Check for title/heading
    headings = soup.find_all(['h1', 'h2'])
    if not headings or len(headings[0].get_text().strip()) < 3:
        return False
    
    # Check for purpose indicators in first 200 words
    first_200_words = ' '.join(text.split()[:200]).lower()
    
    purpose_indicators = [
        'this document', 'this guide', 'this procedure',
        'you will learn', 'shows how', 'explains how',
        'to configure', 'to set up', 'to use',
        'overview of', 'introduction to'
    ]
    
    if any(indicator in first_200_words for indicator in purpose_indicators):
        return True
    
    # Check if it's just a title followed by a wall of text (bad)
    paragraphs = soup.find_all('p')
    if len(paragraphs) > 0:
        first_para_words = len(paragraphs[0].get_text().split())
        # If first paragraph is very long with no clear intro, goal is unclear
        if first_para_words > 100 and not any(ind in paragraphs[0].get_text().lower() for ind in purpose_indicators):
            return False
    
    return True


def detect_document_type(soup: BeautifulSoup, text: str) -> str:
    """
    Detect document type: procedure, concept, or reference.
    
    Heuristics:
    - Procedure: numbered lists, imperative verbs, sequential structure
    - Concept: explanatory language, "what is", definitions
    - Reference: tables, bullet lists, catalog structure
    """
    text_lower = text.lower()
    
    # Procedure indicators
    procedure_indicators = 0
    
    # Check for numbered lists (strong indicator)
    if soup.find_all('ol') or re.search(r'^\d+\.', text, re.MULTILINE):
        procedure_indicators += 3
    
    # Check for imperative verbs at start of sentences
    imperative_patterns = [
        r'\b(click|open|select|choose|enter|type|press|configure|set|enable|disable)\b'
    ]
    if sum(len(re.findall(p, text_lower)) for p in imperative_patterns) > 5:
        procedure_indicators += 2
    
    # Check for sequential language
    if any(word in text_lower for word in ['step', 'first', 'then', 'next', 'finally']):
        procedure_indicators += 1
    
    # Concept indicators
    concept_indicators = 0
    
    if any(phrase in text_lower for phrase in ['what is', 'overview', 'introduction', 'understanding']):
        concept_indicators += 2
    
    if any(phrase in text_lower for phrase in ['for example', 'such as', 'in other words']):
        concept_indicators += 1
    
    # Reference indicators
    reference_indicators = 0
    
    if soup.find_all('table'):
        reference_indicators += 2
    
    if len(soup.find_all(['ul', 'li'])) > len(soup.find_all('p')):
        reference_indicators += 1
    
    # Determine type
    if procedure_indicators > concept_indicators and procedure_indicators > reference_indicators:
        return "procedure"
    elif concept_indicators > reference_indicators:
        return "concept"
    elif reference_indicators > 0:
        return "reference"
    else:
        return "unknown"


def check_procedure_structure(soup: BeautifulSoup, text: str) -> List[DocumentIssue]:
    """
    Check procedure-specific structure.
    
    A good procedure has:
    - Prerequisites section
    - Clear steps
    - Expected outcome
    """
    issues = []
    text_lower = text.lower()
    
    # Check for prerequisites
    has_prereqs = any(word in text_lower for word in ['prerequisite', 'before you', 'you need', 'required'])
    
    if not has_prereqs:
        issues.append(DocumentIssue(
            id="MISSING_PREREQUISITES",
            severity="major",
            message="As a user, I reach the steps without knowing what I need first.",
            reviewer_question="What should I have ready before starting?"
        ))
    
    # Check for outcome/result
    has_outcome = any(word in text_lower for word in ['result', 'outcome', 'you will see', 'should now'])
    
    if not has_outcome:
        issues.append(DocumentIssue(
            id="MISSING_OUTCOME",
            severity="minor",
            message="As a user, I don't know how to tell if I succeeded.",
            reviewer_question="How do I know this worked?"
        ))
    
    # Check for step structure
    numbered_lists = soup.find_all('ol')
    if not numbered_lists:
        issues.append(DocumentIssue(
            id="NO_NUMBERED_STEPS",
            severity="major",
            message="As a user, I can't follow a clear sequence of actions.",
            reviewer_question="What order should I do things in?"
        ))
    
    return issues


def check_concept_structure(soup: BeautifulSoup, text: str) -> List[DocumentIssue]:
    """
    Check concept document structure.
    
    A good concept document has:
    - Clear definition early
    - Examples or use cases
    - Context or related concepts
    """
    issues = []
    text_lower = text.lower()
    first_300_words = ' '.join(text.split()[:300]).lower()
    
    # Check for early definition
    has_definition = any(phrase in first_300_words for phrase in [
        'is a', 'refers to', 'means', 'definition', 'what is'
    ])
    
    if not has_definition:
        issues.append(DocumentIssue(
            id="NO_EARLY_DEFINITION",
            severity="major",
            message="As a user, I'm reading explanations before understanding what this is.",
            reviewer_question="Can you define this in the first paragraph?"
        ))
    
    # Check for examples
    has_examples = any(phrase in text_lower for phrase in [
        'for example', 'for instance', 'such as', 'like'
    ])
    
    if not has_examples:
        issues.append(DocumentIssue(
            id="NO_EXAMPLES",
            severity="minor",
            message="As a user, I'd understand this better with a concrete example.",
            reviewer_question="Can you show a real-world example?"
        ))
    
    return issues


def identify_confusion_zones(soup: BeautifulSoup, text: str) -> List[str]:
    """
    Identify sections where users are likely to get confused.
    
    Confusion indicators:
    - Dense paragraphs (>150 words)
    - Abstract concepts without examples
    - Sudden topic shifts
    - Technical jargon clusters
    """
    confusion_zones = []
    
    # Check each paragraph
    paragraphs = soup.find_all('p')
    for i, para in enumerate(paragraphs):
        para_text = para.get_text()
        word_count = len(para_text.split())
        
        # Dense paragraphs
        if word_count > 150:
            confusion_zones.append(f"paragraph_{i}_dense")
        
        # Check for jargon density (very simple heuristic)
        uppercase_ratio = sum(1 for c in para_text if c.isupper()) / max(len(para_text), 1)
        if uppercase_ratio > 0.05:  # More than 5% uppercase (acronyms)
            confusion_zones.append(f"paragraph_{i}_jargon")
    
    return confusion_zones


def determine_analysis_scope(issues: List[DocumentIssue], flagged_sections: List[str]) -> str:
    """
    Determine how deeply to analyze based on document quality.
    
    - minimal: Document is very clear, only spot-check
    - targeted: Focus on flagged sections
    - full: Document needs comprehensive review
    """
    blocking_count = sum(1 for issue in issues if issue.severity == "blocking")
    major_count = sum(1 for issue in issues if issue.severity == "major")
    
    if blocking_count > 0:
        return "minimal"  # Don't analyze deeply if fundamentals are broken
    elif major_count > 2 or len(flagged_sections) > 5:
        return "full"
    elif len(flagged_sections) > 0:
        return "full"
    else:
        return "full"  # Always do full analysis so custom rules (e.g. Siemens style) run on every sentence


def should_analyze_sentence(sentence_index: int, sentence_text: str, 
                           document_review: DocumentReviewResult) -> bool:
    """
    Gate function: Should this sentence be analyzed?

    Always returns True to ensure all rules (including custom rules like Siemens
    style guide) run on every sentence. The document-level gate still provides
    structural insights, but sentence-level analysis is never skipped.
    """
    return True


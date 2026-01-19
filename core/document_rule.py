"""
Document-level rules for structural and consistency checks.

These rules do NOT rewrite sentences. They provide document-level guidance
and identify structural issues that sentence-level analysis cannot see.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
from core.document_context import DocumentContext


@dataclass
class DocumentFinding:
    """
    A document-level finding (NOT a rewrite suggestion).
    
    These appear in a separate panel from sentence rewrites.
    """
    rule_id: str
    severity: str  # info | warning | error
    category: str  # structure | consistency | completeness | style
    title: str
    description: str
    guidance: Optional[str] = None  # How to fix it
    affected_sections: List[str] = None
    
    def to_dict(self) -> dict:
        return {
            'rule_id': self.rule_id,
            'severity': self.severity,
            'category': self.category,
            'title': self.title,
            'description': self.description,
            'guidance': self.guidance,
            'affected_sections': self.affected_sections or []
        }


class DocumentRule(ABC):
    """
    Base class for document-level rules.
    
    Unlike sentence rules, these:
    - Do NOT trigger rewrites
    - Check document structure
    - Detect consistency issues
    - Provide guidance only
    """
    
    def __init__(self):
        self.rule_id = self.__class__.__name__
        self.category = "structure"
        self.enabled = True
    
    @abstractmethod
    def evaluate(
        self, 
        context: DocumentContext, 
        text: str,
        sentences: Optional[List[Dict]] = None
    ) -> List[DocumentFinding]:
        """
        Evaluate the document and return findings.
        
        Args:
            context: Document-level context
            text: Full document text
            sentences: Optional list of sentence objects (if available)
            
        Returns:
            List of DocumentFinding objects
        """
        pass
    
    def is_applicable(self, context: DocumentContext) -> bool:
        """
        Check if this rule applies to the document type.
        Override to restrict rule application.
        """
        return self.enabled


class ProcedureStructureRule(DocumentRule):
    """
    Check that procedure documents have required structure.
    
    Requirements:
    - Must have Prerequisites section (or similar)
    - Must have numbered steps or procedure section
    - Should have clear goal statement
    """
    
    def __init__(self):
        super().__init__()
        self.category = "structure"
    
    def is_applicable(self, context: DocumentContext) -> bool:
        return context.doc_type in ['manual', 'procedure'] and self.enabled
    
    def evaluate(self, context: DocumentContext, text: str, sentences=None) -> List[DocumentFinding]:
        findings = []
        
        # Check for prerequisites
        has_prereq = any(
            'prerequisite' in s['name'].lower() or 
            'before you begin' in s['name'].lower() or
            'requirement' in s['name'].lower()
            for s in context.sections
        )
        
        if not has_prereq:
            findings.append(DocumentFinding(
                rule_id=self.rule_id,
                severity='warning',
                category=self.category,
                title='Missing Prerequisites Section',
                description='Procedure documents should include a prerequisites section',
                guidance='Add a "Prerequisites" or "Before You Begin" section listing requirements'
            ))
        
        # Check for procedure/steps section
        has_procedure = any(
            'procedure' in s['name'].lower() or 
            'steps' in s['name'].lower() or
            'instruction' in s['name'].lower()
            for s in context.sections
        )
        
        if not has_procedure:
            findings.append(DocumentFinding(
                rule_id=self.rule_id,
                severity='warning',
                category=self.category,
                title='Missing Procedure Section',
                description='Procedure documents should have a clear steps or procedure section',
                guidance='Add a "Procedure" or "Steps" section with numbered instructions'
            ))
        
        # Check for numbered steps in text
        numbered_steps = len([m for m in text.split('\n') if m.strip().startswith(('1.', '2.', '3.'))])
        if numbered_steps < 2:
            findings.append(DocumentFinding(
                rule_id=self.rule_id,
                severity='info',
                category=self.category,
                title='No Numbered Steps Found',
                description='Procedures are clearer with numbered steps',
                guidance='Consider using numbered lists for step-by-step instructions'
            ))
        
        return findings


class AcronymConsistencyRule(DocumentRule):
    """
    Check that acronyms are defined before first use.
    """
    
    def __init__(self):
        super().__init__()
        self.category = "consistency"
    
    def evaluate(self, context: DocumentContext, text: str, sentences=None) -> List[DocumentFinding]:
        findings = []
        
        # Find all acronyms in text (2+ capital letters)
        import re
        all_acronyms = set(re.findall(r'\b[A-Z]{2,}\b', text))
        
        # Remove common words that look like acronyms
        common_false_positives = {'OK', 'US', 'ID', 'IT', 'OR', 'AND', 'NOT', 'ALL', 'NEW'}
        all_acronyms -= common_false_positives
        
        # Check which acronyms are defined
        undefined_acronyms = all_acronyms - set(context.acronyms.keys())
        
        if undefined_acronyms:
            findings.append(DocumentFinding(
                rule_id=self.rule_id,
                severity='warning',
                category=self.category,
                title='Undefined Acronyms',
                description=f'Found {len(undefined_acronyms)} acronyms without definitions: {", ".join(sorted(list(undefined_acronyms))[:5])}',
                guidance='Define acronyms on first use: Full Term (ACRONYM)'
            ))
        
        return findings


class TerminologyConsistencyRule(DocumentRule):
    """
    Check for inconsistent terminology usage.
    """
    
    def __init__(self):
        super().__init__()
        self.category = "consistency"
    
    def evaluate(self, context: DocumentContext, text: str, sentences=None) -> List[DocumentFinding]:
        findings = []
        
        # Check if defined terms are used inconsistently
        if context.terminology_map:
            import re
            inconsistencies = []
            
            for variant, canonical in context.terminology_map.items():
                if variant != canonical.lower():
                    # Count usage of variant
                    variant_count = len(re.findall(r'\b' + re.escape(variant) + r'\b', text, re.IGNORECASE))
                    if variant_count > 0:
                        inconsistencies.append(f'{variant} (should be {canonical})')
            
            if inconsistencies:
                findings.append(DocumentFinding(
                    rule_id=self.rule_id,
                    severity='info',
                    category=self.category,
                    title='Inconsistent Terminology',
                    description=f'Found {len(inconsistencies)} terminology inconsistencies',
                    guidance='Use canonical terms consistently throughout the document'
                ))
        
        return findings


class TenseConsistencyRule(DocumentRule):
    """
    Check for consistent verb tense usage.
    """
    
    def __init__(self):
        super().__init__()
        self.category = "consistency"
    
    def evaluate(self, context: DocumentContext, text: str, sentences=None) -> List[DocumentFinding]:
        findings = []
        
        if context.dominant_tense == 'mixed':
            findings.append(DocumentFinding(
                rule_id=self.rule_id,
                severity='info',
                category=self.category,
                title='Mixed Verb Tenses',
                description='Document uses mixed verb tenses across sections',
                guidance='Consider using consistent tense (typically present for procedures, past for reports)'
            ))
        
        return findings


class DocumentCompletenessRule(DocumentRule):
    """
    Check for expected document elements.
    """
    
    def __init__(self):
        super().__init__()
        self.category = "completeness"
    
    def evaluate(self, context: DocumentContext, text: str, sentences=None) -> List[DocumentFinding]:
        findings = []
        
        # Check for introduction
        has_intro = any(
            'introduction' in s['name'].lower() or 
            'overview' in s['name'].lower()
            for s in context.sections
        )
        
        if not has_intro and context.doc_type not in ['reference', 'api']:
            findings.append(DocumentFinding(
                rule_id=self.rule_id,
                severity='info',
                category=self.category,
                title='Missing Introduction',
                description='Document lacks an introduction or overview section',
                guidance='Add an introduction to provide context and goals'
            ))
        
        # Check document length
        if context.total_sentences < 5:
            findings.append(DocumentFinding(
                rule_id=self.rule_id,
                severity='info',
                category=self.category,
                title='Very Short Document',
                description=f'Document has only {context.total_sentences} sentences',
                guidance='Consider if the document provides sufficient detail'
            ))
        
        # Check for very long sentences on average
        if context.avg_sentence_length > 30:
            findings.append(DocumentFinding(
                rule_id=self.rule_id,
                severity='info',
                category=self.category,
                title='Long Average Sentence Length',
                description=f'Average sentence length is {context.avg_sentence_length:.1f} words',
                guidance='Consider breaking down complex sentences for better readability'
            ))
        
        return findings


class SectionOrderRule(DocumentRule):
    """
    Check that sections appear in logical order.
    """
    
    def __init__(self):
        super().__init__()
        self.category = "structure"
    
    def is_applicable(self, context: DocumentContext) -> bool:
        return context.doc_type == 'manual' and self.enabled
    
    def evaluate(self, context: DocumentContext, text: str, sentences=None) -> List[DocumentFinding]:
        findings = []
        
        # Expected order for manuals
        expected_order = [
            'introduction', 'overview', 'prerequisites', 'requirement',
            'procedure', 'steps', 'instruction',
            'example', 'troubleshooting',
            'reference', 'appendix'
        ]
        
        # Get section order
        section_types = []
        for section in context.sections:
            name_lower = section['name'].lower()
            for expected in expected_order:
                if expected in name_lower:
                    section_types.append(expected)
                    break
        
        # Check if order matches
        expected_indices = []
        for st in section_types:
            if st in expected_order:
                expected_indices.append(expected_order.index(st))
        
        if expected_indices and expected_indices != sorted(expected_indices):
            findings.append(DocumentFinding(
                rule_id=self.rule_id,
                severity='info',
                category=self.category,
                title='Unusual Section Order',
                description='Sections appear in non-standard order',
                guidance='Consider standard order: Introduction → Prerequisites → Procedure → Examples → Reference'
            ))
        
        return findings


# Registry of all document rules
DOCUMENT_RULES = [
    ProcedureStructureRule(),
    AcronymConsistencyRule(),
    TerminologyConsistencyRule(),
    TenseConsistencyRule(),
    DocumentCompletenessRule(),
    SectionOrderRule(),
]


def evaluate_document_rules(
    context: DocumentContext,
    text: str,
    sentences: Optional[List[Dict]] = None
) -> List[DocumentFinding]:
    """
    Evaluate all applicable document rules.
    
    Args:
        context: Document context
        text: Full document text
        sentences: Optional sentence objects
        
    Returns:
        List of all document findings
    """
    all_findings = []
    
    for rule in DOCUMENT_RULES:
        if rule.is_applicable(context):
            findings = rule.evaluate(context, text, sentences)
            all_findings.extend(findings)
    
    return all_findings

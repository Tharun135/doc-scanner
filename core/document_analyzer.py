"""
Document-level analyzers for whole-manual understanding (PASS 0).

These analyzers extract document-wide signals before sentence-level processing.
They are LIGHTWEIGHT and HEURISTIC-BASED - no over-engineering.
"""

import re
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup
from core.document_context import DocumentContext


class DocumentAnalyzer:
    """
    Extracts document-level context from the full text.
    
    This runs BEFORE sentence splitting. It provides signals that guide
    sentence-level decisions without replacing them.
    """
    
    def __init__(self):
        self.safety_keywords = ['safety', 'warning', 'danger', 'caution', 'hazard', 'risk']
        self.legal_keywords = ['legal', 'copyright', 'trademark', 'license', 'disclaimer', 'terms']
        
        # Document type detection patterns
        self.procedure_keywords = ['procedure', 'steps', 'instructions', 'how to', 'guide']
        self.api_keywords = ['api', 'endpoint', 'parameter', 'return', 'function', 'method']
        self.concept_keywords = ['overview', 'introduction', 'concept', 'architecture', 'theory']
        self.reference_keywords = ['reference', 'glossary', 'index', 'appendix']
    
    def analyze(self, text: str, html_content: Optional[str] = None) -> DocumentContext:
        """
        Main analysis entry point. Extracts document-wide context.
        
        Args:
            text: Plain text of the document
            html_content: Optional HTML content for structure extraction
            
        Returns:
            DocumentContext with all document-level signals
        """
        # Initialize context
        context = DocumentContext(
            doc_type="unknown",
            primary_goal="unknown",
            audience_level="mixed",
            rewrite_sensitivity="medium"
        )
        
        # Extract headings and structure
        if html_content:
            context.headings = self._extract_headings(html_content)
            context.sections = self._identify_sections(context.headings, text)
        else:
            # Fallback to markdown-style headings
            context.headings = self._extract_markdown_headings(text)
            context.sections = self._identify_sections(context.headings, text)
        
        # Detect document type
        context.doc_type = self._detect_document_type(context.headings, text)
        
        # Detect primary goal
        context.primary_goal = self._detect_primary_goal(context.doc_type, context.headings)
        
        # Detect audience level
        context.audience_level = self._detect_audience_level(text)
        
        # Identify forbidden zones
        context.forbidden_sections, context.forbidden_spans = self._identify_forbidden_zones(
            context.headings, context.sections, text
        )
        
        # Set rewrite sensitivity based on doc type and forbidden zones
        context.rewrite_sensitivity = self._determine_sensitivity(
            context.doc_type, context.forbidden_sections
        )
        
        # Extract terminology
        context.acronyms = self._extract_acronyms(text)
        context.defined_terms = self._extract_defined_terms(text)
        context.terminology_map = self._build_terminology_map(text, context.defined_terms)
        
        # Calculate basic stats
        sentences = self._simple_sentence_split(text)
        context.total_sentences = len(sentences)
        context.total_words = len(text.split())
        if context.total_sentences > 0:
            context.avg_sentence_length = context.total_words / context.total_sentences
        
        # Detect dominant tense
        context.dominant_tense = self._detect_dominant_tense(text)
        
        # Check for TOC and index
        context.has_toc = self._has_table_of_contents(context.headings, text)
        context.has_index = self._has_index(context.headings, text)
        
        return context
    
    def _extract_headings(self, html_content: str) -> List[Dict]:
        """Extract headings from HTML content."""
        headings = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for i, tag in enumerate(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])):
            level = int(tag.name[1])
            text = tag.get_text().strip()
            headings.append({
                'text': text,
                'level': level,
                'position': i,
                'tag': tag.name
            })
        
        return headings
    
    def _extract_markdown_headings(self, text: str) -> List[Dict]:
        """Extract markdown-style headings from plain text."""
        headings = []
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headings.append({
                    'text': text,
                    'level': level,
                    'position': i,
                    'tag': f'h{level}'
                })
        
        return headings
    
    def _identify_sections(self, headings: List[Dict], text: str) -> List[Dict]:
        """Identify major sections based on headings."""
        sections = []
        
        for i, heading in enumerate(headings):
            # Only consider h1 and h2 as major sections
            if heading['level'] <= 2:
                start_pos = heading['position']
                
                # Find end position (next heading of same or higher level)
                end_pos = len(text)
                for next_heading in headings[i+1:]:
                    if next_heading['level'] <= heading['level']:
                        end_pos = next_heading['position']
                        break
                
                sections.append({
                    'name': heading['text'],
                    'start': start_pos,
                    'end': end_pos,
                    'level': heading['level'],
                    'type': self._classify_section_type(heading['text'])
                })
        
        return sections
    
    def _classify_section_type(self, section_name: str) -> str:
        """Classify section type based on heading text."""
        name_lower = section_name.lower()
        
        if any(kw in name_lower for kw in self.safety_keywords):
            return 'safety'
        elif any(kw in name_lower for kw in self.legal_keywords):
            return 'legal'
        elif any(kw in name_lower for kw in ['prerequisite', 'requirement', 'before you begin']):
            return 'prerequisites'
        elif any(kw in name_lower for kw in ['procedure', 'steps', 'instructions']):
            return 'procedure'
        elif any(kw in name_lower for kw in ['example', 'sample']):
            return 'example'
        elif any(kw in name_lower for kw in ['reference', 'appendix']):
            return 'reference'
        else:
            return 'content'
    
    def _detect_document_type(self, headings: List[Dict], text: str) -> str:
        """
        Detect document type using lightweight heuristics.
        
        Priority: safety > api > manual > concept > reference > ui
        """
        text_lower = text.lower()
        heading_texts = [h['text'].lower() for h in headings]
        
        # Safety documents are highest priority
        if any(kw in text_lower for kw in self.safety_keywords):
            return 'safety'
        
        # API documentation
        api_score = sum(1 for kw in self.api_keywords if kw in text_lower)
        if api_score >= 3:
            return 'api'
        
        # Procedure/Manual
        procedure_score = sum(1 for kw in self.procedure_keywords if any(kw in h for h in heading_texts))
        if procedure_score >= 2:
            return 'manual'
        
        # Concept documentation
        concept_score = sum(1 for kw in self.concept_keywords if any(kw in h for h in heading_texts))
        if concept_score >= 2:
            return 'concept'
        
        # Reference documentation
        if any(kw in heading_texts for kw in self.reference_keywords):
            return 'reference'
        
        # UI documentation
        if 'ui' in text_lower or 'user interface' in text_lower:
            return 'ui'
        
        return 'manual'  # default
    
    def _detect_primary_goal(self, doc_type: str, headings: List[Dict]) -> str:
        """Detect primary goal based on document type and structure."""
        goal_map = {
            'safety': 'warn',
            'api': 'reference',
            'manual': 'instruct',
            'procedure': 'instruct',
            'concept': 'explain',
            'reference': 'reference',
            'ui': 'instruct'
        }
        return goal_map.get(doc_type, 'explain')
    
    def _detect_audience_level(self, text: str) -> str:
        """
        Detect audience level based on content characteristics.
        
        Heuristics:
        - Novice: many definitions, simple words, step-by-step
        - Expert: technical jargon, assumes knowledge, no explanations
        - Intermediate: balanced
        """
        text_lower = text.lower()
        
        # Count novice indicators
        novice_indicators = [
            'for example', 'such as', 'this means', 'in other words',
            'step 1', 'step 2', 'first,', 'next,', 'then,', 'finally,'
        ]
        novice_score = sum(1 for indicator in novice_indicators if indicator in text_lower)
        
        # Count expert indicators (technical terms, no explanations)
        expert_patterns = [
            r'\b[A-Z]{3,}\b',  # Acronyms without definitions
            r'\b\w+\(\)',  # Function calls
            r'0x[0-9a-f]+',  # Hex numbers
        ]
        expert_score = sum(len(re.findall(pattern, text)) for pattern in expert_patterns)
        
        # Normalize scores
        text_length = len(text.split())
        novice_ratio = novice_score / (text_length / 100) if text_length > 0 else 0
        expert_ratio = expert_score / (text_length / 100) if text_length > 0 else 0
        
        if novice_ratio > 2:
            return 'novice'
        elif expert_ratio > 3:
            return 'expert'
        else:
            return 'intermediate'
    
    def _identify_forbidden_zones(
        self, 
        headings: List[Dict], 
        sections: List[Dict],
        text: str
    ) -> Tuple[List[str], List[Tuple]]:
        """
        Identify sections where rewrites should be forbidden.
        
        Returns: (forbidden_section_names, forbidden_spans)
        """
        forbidden_sections = []
        forbidden_spans = []
        
        for section in sections:
            section_type = section['type']
            section_name = section['name']
            
            # Block rewrites in safety and legal sections
            if section_type in ['safety', 'legal']:
                forbidden_sections.append(section_name)
                forbidden_spans.append((section['start'], section['end']))
        
        # Also check for explicit markers in text
        warning_patterns = [
            r'(?i)\*\*WARNING\*\*',
            r'(?i)⚠️',
            r'(?i)CAUTION:',
            r'(?i)DANGER:',
        ]
        
        for pattern in warning_patterns:
            for match in re.finditer(pattern, text):
                # Mark next 500 chars as forbidden
                start = match.start()
                end = min(start + 500, len(text))
                forbidden_spans.append((start, end))
        
        return forbidden_sections, forbidden_spans
    
    def _determine_sensitivity(self, doc_type: str, forbidden_sections: List[str]) -> str:
        """Determine rewrite sensitivity level."""
        if doc_type == 'safety' or len(forbidden_sections) > 0:
            return 'critical'
        elif doc_type in ['api', 'reference']:
            return 'high'
        elif doc_type in ['manual', 'procedure']:
            return 'medium'
        else:
            return 'low'
    
    def _extract_acronyms(self, text: str) -> Dict[str, str]:
        """
        Extract acronyms and their definitions.
        
        Pattern: Full Term (ACRONYM)
        """
        acronyms = {}
        
        # Pattern: words (ACRONYM)
        pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([A-Z]{2,})\)'
        
        for match in re.finditer(pattern, text):
            definition = match.group(1)
            acronym = match.group(2)
            acronyms[acronym] = definition
        
        return acronyms
    
    def _extract_defined_terms(self, text: str) -> List[str]:
        """
        Extract explicitly defined terms.
        
        Patterns:
        - "X is defined as..."
        - "X means..."
        - "X refers to..."
        """
        defined_terms = []
        
        patterns = [
            r'([A-Z][a-z]+(?:\s+[a-z]+)*)\s+is\s+defined\s+as',
            r'([A-Z][a-z]+(?:\s+[a-z]+)*)\s+means',
            r'([A-Z][a-z]+(?:\s+[a-z]+)*)\s+refers\s+to',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                term = match.group(1).strip()
                if term and len(term) > 2:
                    defined_terms.append(term)
        
        return list(set(defined_terms))
    
    def _build_terminology_map(self, text: str, defined_terms: List[str]) -> Dict[str, str]:
        """
        Build a map of term variants to canonical forms.
        
        This is lightweight - just handles simple plurals and case variants.
        """
        terminology_map = {}
        
        for term in defined_terms:
            term_lower = term.lower()
            
            # Map variants to canonical
            terminology_map[term_lower] = term
            terminology_map[term_lower + 's'] = term  # plural
            terminology_map[term.upper()] = term  # all caps
        
        return terminology_map
    
    def _detect_dominant_tense(self, text: str) -> str:
        """
        Detect dominant verb tense in the document.
        
        Simple heuristic based on verb patterns.
        """
        # Count present tense indicators
        present_patterns = [r'\b(is|are|has|have|does|do)\b']
        present_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in present_patterns)
        
        # Count past tense indicators
        past_patterns = [r'\b(was|were|had|did)\b', r'\w+ed\b']
        past_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in past_patterns)
        
        # Count future tense indicators
        future_patterns = [r'\b(will|shall)\b']
        future_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in future_patterns)
        
        total = present_count + past_count + future_count
        if total == 0:
            return 'mixed'
        
        if present_count / total > 0.6:
            return 'present'
        elif past_count / total > 0.6:
            return 'past'
        elif future_count / total > 0.3:
            return 'future'
        else:
            return 'mixed'
    
    def _has_table_of_contents(self, headings: List[Dict], text: str) -> bool:
        """Check if document has a table of contents."""
        text_lower = text.lower()
        toc_patterns = [
            'table of contents',
            'contents',
            'in this document',
            'in this guide',
        ]
        return any(pattern in text_lower for pattern in toc_patterns)
    
    def _has_index(self, headings: List[Dict], text: str) -> bool:
        """Check if document has an index."""
        return any(h['text'].lower() == 'index' for h in headings)
    
    def _simple_sentence_split(self, text: str) -> List[str]:
        """Simple sentence splitting for stats."""
        # Basic split on . ! ?
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]

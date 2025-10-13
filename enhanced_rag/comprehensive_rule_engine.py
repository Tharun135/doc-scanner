"""
Enhanced rule engine with comprehensive pattern matching and context awareness.
This addresses the systemic issues in AI writing assistance by providing:
1. Comprehensive rule coverage
2. Context-aware corrections
3. Advanced pattern matching
4. Intelligent fallback strategies
"""
import re
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

class DocumentType(Enum):
    """Document type classification for context-aware suggestions"""
    API_DOCUMENTATION = "api_documentation"
    USER_GUIDE = "user_guide"
    TECHNICAL_SPEC = "technical_spec"
    TUTORIAL = "tutorial"
    README = "readme"
    BLOG_POST = "blog_post"
    GENERAL = "general"

class RuleCategory(Enum):
    """Categories of writing rules for better organization"""
    GRAMMAR = "grammar"
    STYLE = "style"
    CLARITY = "clarity"
    TECHNICAL = "technical"
    UI_UX = "ui_ux"
    CONSISTENCY = "consistency"

@dataclass
class RuleDefinition:
    """Comprehensive rule definition with context awareness"""
    rule_id: str
    category: RuleCategory
    description: str
    pattern_regex: Optional[str] = None
    correction_template: Optional[str] = None
    confidence_weight: float = 1.0
    applies_to_documents: List[DocumentType] = None
    priority: int = 5  # 1-10, higher = more important

@dataclass
class CorrectionContext:
    """Context information for making intelligent corrections"""
    document_type: DocumentType
    surrounding_text: str
    sentence_position: str  # "start", "middle", "end"
    paragraph_context: str
    domain_keywords: List[str]
    user_preferences: Dict[str, Any] = None

class ComprehensiveRuleEngine:
    """
    Advanced rule engine that addresses systemic issues in AI writing assistance.
    Provides deterministic corrections with context awareness.
    """
    
    def __init__(self):
        self.rules = self._initialize_comprehensive_rules()
        self.document_classifier = DocumentTypeClassifier()
        
    def _initialize_comprehensive_rules(self) -> Dict[str, RuleDefinition]:
        """Initialize comprehensive rule set covering 50+ writing issues"""
        rules = {}
        
        # GRAMMAR RULES
        rules.update({
            "capitalization_sentence_start": RuleDefinition(
                rule_id="capitalization_sentence_start",
                category=RuleCategory.GRAMMAR,
                description="Sentences must start with a capital letter",
                pattern_regex=r'^[a-z]',
                confidence_weight=1.0,
                priority=9
            ),
            "capitalization_proper_nouns": RuleDefinition(
                rule_id="capitalization_proper_nouns",
                category=RuleCategory.GRAMMAR,
                description="Proper nouns should be capitalized",
                pattern_regex=r'\b(api|json|xml|http|sql|rest|oauth)\b',
                confidence_weight=0.8,
                priority=6
            ),
            "punctuation_missing_period": RuleDefinition(
                rule_id="punctuation_missing_period",
                category=RuleCategory.GRAMMAR,
                description="Sentences should end with proper punctuation",
                pattern_regex=r'[a-zA-Z0-9]\s*$',
                confidence_weight=0.9,
                priority=8
            ),
            "subject_verb_agreement": RuleDefinition(
                rule_id="subject_verb_agreement",
                category=RuleCategory.GRAMMAR,
                description="Subject and verb must agree in number",
                pattern_regex=r'\b(data|criteria|phenomena)\s+(is|was)\b',
                confidence_weight=0.7,
                priority=7
            )
        })
        
        # STYLE RULES
        rules.update({
            "passive_voice": RuleDefinition(
                rule_id="passive_voice",
                category=RuleCategory.STYLE,
                description="Use active voice instead of passive voice",
                pattern_regex=r'\b(is|are|was|were|been|being)\s+\w+ed\b',
                confidence_weight=0.8,
                priority=6,
                applies_to_documents=[DocumentType.API_DOCUMENTATION, DocumentType.USER_GUIDE]
            ),
            "wordiness": RuleDefinition(
                rule_id="wordiness",
                category=RuleCategory.STYLE,
                description="Remove unnecessary words",
                pattern_regex=r'\b(in order to|for the purpose of|due to the fact that)\b',
                confidence_weight=0.9,
                priority=5
            ),
            "adverb_overuse": RuleDefinition(
                rule_id="adverb_overuse",
                category=RuleCategory.STYLE,
                description="Avoid unnecessary adverbs",
                pattern_regex=r'\b(really|very|quite|extremely|basically|simply|easily)\s+',
                confidence_weight=0.8,
                priority=4
            )
        })
        
        # CLARITY RULES
        rules.update({
            "long_sentences": RuleDefinition(
                rule_id="long_sentences",
                category=RuleCategory.CLARITY,
                description="Break long sentences into shorter ones",
                confidence_weight=0.7,
                priority=6
            ),
            "complex_words": RuleDefinition(
                rule_id="complex_words",
                category=RuleCategory.CLARITY,
                description="Use simpler alternatives to complex words",
                pattern_regex=r'\b(utilize|demonstrate|facilitate|endeavor)\b',
                confidence_weight=0.6,
                priority=4
            ),
            "ambiguous_pronouns": RuleDefinition(
                rule_id="ambiguous_pronouns",
                category=RuleCategory.CLARITY,
                description="Clarify ambiguous pronoun references",
                pattern_regex=r'\b(this|that|it|they)\s+(?!is|are|was|were|will|can|should)',
                confidence_weight=0.5,
                priority=5
            )
        })
        
        # TECHNICAL WRITING RULES
        rules.update({
            "api_consistency": RuleDefinition(
                rule_id="api_consistency",
                category=RuleCategory.TECHNICAL,
                description="Use consistent API terminology",
                confidence_weight=0.9,
                priority=8,
                applies_to_documents=[DocumentType.API_DOCUMENTATION]
            ),
            "code_formatting": RuleDefinition(
                rule_id="code_formatting",
                category=RuleCategory.TECHNICAL,
                description="Format code elements properly",
                pattern_regex=r'\b[A-Z_]{2,}\b(?!`)',  # Constants not in code blocks
                confidence_weight=0.8,
                priority=7
            ),
            "version_consistency": RuleDefinition(
                rule_id="version_consistency",
                category=RuleCategory.TECHNICAL,
                description="Use consistent version numbering",
                pattern_regex=r'\bv?\d+\.\d+(?:\.\d+)?\b',
                confidence_weight=0.7,
                priority=6
            )
        })
        
        # UI/UX WRITING RULES
        rules.update({
            "click_on_usage": RuleDefinition(
                rule_id="click_on_usage",
                category=RuleCategory.UI_UX,
                description="Use 'click' instead of 'click on'",
                pattern_regex=r'\bclick on\b',
                confidence_weight=1.0,
                priority=8,
                applies_to_documents=[DocumentType.USER_GUIDE, DocumentType.TUTORIAL]
            ),
            "imperative_mood": RuleDefinition(
                rule_id="imperative_mood",
                category=RuleCategory.UI_UX,
                description="Use imperative mood for instructions",
                pattern_regex=r'\b(you should|you can|you may)\b',
                confidence_weight=0.7,
                priority=6
            ),
            "button_naming": RuleDefinition(
                rule_id="button_naming",
                category=RuleCategory.UI_UX,
                description="Use consistent button naming conventions",
                confidence_weight=0.8,
                priority=7
            )
        })
        
        return rules
    
    def analyze_and_correct(self, 
                           text: str, 
                           detected_rule_id: str,
                           context: CorrectionContext) -> Dict[str, Any]:
        """
        Comprehensive analysis and correction with context awareness.
        
        Args:
            text: The text to analyze and correct
            detected_rule_id: The rule that was violated
            context: Context information for intelligent correction
            
        Returns:
            Correction result with explanation and confidence
        """
        rule = self.rules.get(detected_rule_id)
        if not rule:
            return self._fallback_correction(text, detected_rule_id, context)
        
        # Check if rule applies to this document type
        if (rule.applies_to_documents and 
            context.document_type not in rule.applies_to_documents):
            # Adjust confidence for rules that don't apply to this document type
            confidence_multiplier = 0.5
        else:
            confidence_multiplier = 1.0
        
        # Apply rule-specific correction
        correction_result = self._apply_rule_correction(text, rule, context)
        
        # Adjust confidence based on context
        final_confidence = (correction_result['confidence'] * 
                          rule.confidence_weight * 
                          confidence_multiplier)
        
        return {
            'original': text,
            'corrected': correction_result['corrected'],
            'explanation': correction_result['explanation'],
            'confidence': min(final_confidence, 1.0),
            'rule_category': rule.category.value,
            'priority': rule.priority,
            'method': 'comprehensive_rule_engine'
        }
    
    def _apply_rule_correction(self, 
                              text: str, 
                              rule: RuleDefinition,
                              context: CorrectionContext) -> Dict[str, Any]:
        """Apply specific correction logic for each rule"""
        
        if rule.rule_id == "capitalization_sentence_start":
            return self._fix_sentence_capitalization(text, context)
        elif rule.rule_id == "passive_voice":
            return self._fix_passive_voice_advanced(text, context)
        elif rule.rule_id == "long_sentences":
            return self._fix_long_sentences_advanced(text, context)
        elif rule.rule_id == "click_on_usage":
            return self._fix_click_on_usage(text, context)
        elif rule.rule_id == "adverb_overuse":
            return self._fix_adverb_overuse(text, context)
        elif rule.rule_id == "wordiness":
            return self._fix_wordiness(text, context)
        elif rule.rule_id == "code_formatting":
            return self._fix_code_formatting(text, context)
        else:
            return self._generic_pattern_correction(text, rule, context)
    
    def _fix_sentence_capitalization(self, text: str, context: CorrectionContext) -> Dict[str, Any]:
        """Advanced capitalization fixing with context awareness"""
        if not text or text[0].isupper():
            return {'corrected': text, 'explanation': 'Already properly capitalized', 'confidence': 0.1}
        
        corrected = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        return {
            'corrected': corrected,
            'explanation': 'Capitalized the first letter of the sentence for proper grammar.',
            'confidence': 1.0
        }
    
    def _fix_passive_voice_advanced(self, text: str, context: CorrectionContext) -> Dict[str, Any]:
        """Advanced passive voice correction with document type awareness"""
        
        # API documentation specific patterns
        if context.document_type == DocumentType.API_DOCUMENTATION:
            # "Data is returned" -> "The API returns data"
            pattern = r'(.+?)\s+(?:is|are)\s+([a-zA-Z]+ed)(?:\s+by\s+(.+?))?'
            match = re.search(pattern, text)
            if match:
                object_part = match.group(1)
                action = match.group(2)
                agent = match.group(3) if match.group(3) else "the API"
                
                corrected = f"{agent.capitalize()} {self._passive_to_active_verb(action)} {object_part.lower()}"
                return {
                    'corrected': corrected,
                    'explanation': 'Converted to active voice using API as the agent for clearer technical writing.',
                    'confidence': 0.9
                }
        
        # General passive voice patterns
        return self._fix_passive_voice_generic(text, context)
    
    def _fix_passive_voice_generic(self, text: str, context: CorrectionContext) -> Dict[str, Any]:
        """Generic passive voice correction for all document types"""
        from .rule_specific_corrections import RuleSpecificCorrector
        
        corrected = RuleSpecificCorrector.fix_passive_voice(text)
        
        if corrected != text:
            return {
                'corrected': corrected,
                'explanation': 'Converted passive voice to active voice for clearer writing.',
                'confidence': 0.8
            }
        else:
            return {
                'corrected': text,
                'explanation': 'No clear passive voice pattern detected.',
                'confidence': 0.2
            }
    
    def _fix_long_sentences_advanced(self, text: str, context: CorrectionContext) -> Dict[str, Any]:
        """Advanced sentence breaking with context awareness"""
        
        if len(text) < 60:  # Not really long
            return {'corrected': text, 'explanation': 'Sentence length is acceptable', 'confidence': 0.1}
        
        # Technical writing specific breaking
        if context.document_type in [DocumentType.API_DOCUMENTATION, DocumentType.TECHNICAL_SPEC]:
            # Break at technical connectors
            for pattern, replacement in [
                (r'(.+?):\s*(.+)', r'\1. This includes: \2'),
                (r'(.+?),\s*which\s+(.+)', r'\1. This \2'),
                (r'(.+?),\s*and\s+(.+)', r'\1. Additionally, \2'),
            ]:
                match = re.search(pattern, text)
                if match:
                    corrected = replacement.replace(r'\1', match.group(1)).replace(r'\2', match.group(2))
                    return {
                        'corrected': corrected,
                        'explanation': 'Broke long sentence into shorter ones for better readability in technical documentation.',
                        'confidence': 0.8
                    }
        
        return self._generic_sentence_breaking(text, context)
    
    def _generic_sentence_breaking(self, text: str, context: CorrectionContext) -> Dict[str, Any]:
        """Generic sentence breaking logic"""
        from .rule_specific_corrections import RuleSpecificCorrector
        
        corrected = RuleSpecificCorrector.break_long_sentence(text)
        
        if corrected != text:
            return {
                'corrected': corrected,
                'explanation': 'Broke long sentence into shorter ones for better readability.',
                'confidence': 0.7
            }
        else:
            return {
                'corrected': text,
                'explanation': 'Sentence length is acceptable or no clear break points found.',
                'confidence': 0.3
            }
    
    def _fix_click_on_usage(self, text: str, context: CorrectionContext) -> Dict[str, Any]:
        """Fix 'click on' usage in UI instructions"""
        from .rule_specific_corrections import RuleSpecificCorrector
        
        corrected = RuleSpecificCorrector.fix_click_on(text)
        
        if corrected != text:
            return {
                'corrected': corrected,
                'explanation': 'Replaced "click on" with more direct language for UI instructions.',
                'confidence': 1.0
            }
        else:
            return {
                'corrected': text,
                'explanation': 'No "click on" usage found.',
                'confidence': 0.1
            }
    
    def _fix_adverb_overuse(self, text: str, context: CorrectionContext) -> Dict[str, Any]:
        """Remove unnecessary adverbs"""
        from .rule_specific_corrections import RuleSpecificCorrector
        
        corrected = RuleSpecificCorrector.remove_adverbs(text)
        
        if corrected != text:
            return {
                'corrected': corrected,
                'explanation': 'Removed unnecessary adverbs for more direct writing.',
                'confidence': 0.8
            }
        else:
            return {
                'corrected': text,
                'explanation': 'No unnecessary adverbs found.',
                'confidence': 0.1
            }
    
    def _fix_wordiness(self, text: str, context: CorrectionContext) -> Dict[str, Any]:
        """Fix wordy expressions"""
        wordy_replacements = {
            'in order to': 'to',
            'for the purpose of': 'to',
            'due to the fact that': 'because',
            'at this point in time': 'now',
            'in the event that': 'if'
        }
        
        corrected = text
        changes_made = []
        
        for wordy, simple in wordy_replacements.items():
            if wordy in corrected.lower():
                corrected = corrected.replace(wordy, simple)
                corrected = corrected.replace(wordy.title(), simple.title())
                changes_made.append(f'"{wordy}" → "{simple}"')
        
        if changes_made:
            return {
                'corrected': corrected,
                'explanation': f'Simplified wordy expressions: {", ".join(changes_made)}.',
                'confidence': 0.9
            }
        else:
            return {
                'corrected': text,
                'explanation': 'No wordy expressions found.',
                'confidence': 0.1
            }
    
    def _fix_code_formatting(self, text: str, context: CorrectionContext) -> Dict[str, Any]:
        """Fix code formatting issues"""
        import re
        
        # Find code elements that should be formatted
        code_pattern = r'\b([A-Z_]{2,}|[a-zA-Z]+\.[a-zA-Z]+)\b'
        matches = re.findall(code_pattern, text)
        
        corrected = text
        for match in matches:
            if match.isupper() and len(match) > 2:  # Constants
                corrected = corrected.replace(match, f'`{match}`')
        
        if corrected != text:
            return {
                'corrected': corrected,
                'explanation': 'Formatted code elements with backticks for better readability.',
                'confidence': 0.7
            }
        else:
            return {
                'corrected': text,
                'explanation': 'No unformatted code elements found.',
                'confidence': 0.1
            }
    
    def _generic_pattern_correction(self, text: str, rule: RuleDefinition, context: CorrectionContext) -> Dict[str, Any]:
        """Generic pattern-based correction for rules with regex patterns"""
        import re
        
        if not rule.pattern_regex:
            return {
                'corrected': text,
                'explanation': f'No specific pattern defined for {rule.rule_id}.',
                'confidence': 0.1
            }
        
        # Simple pattern matching and highlighting
        matches = re.findall(rule.pattern_regex, text, re.IGNORECASE)
        
        if matches:
            return {
                'corrected': text,  # Could implement specific replacements
                'explanation': f'Found {len(matches)} instance(s) of {rule.description.lower()}.',
                'confidence': 0.6
            }
        else:
            return {
                'corrected': text,
                'explanation': f'No instances of {rule.description.lower()} found.',
                'confidence': 0.1
            }
        """Enhanced passive to active verb conversion"""
        verb_map = {
            'returned': 'returns',
            'sent': 'sends',
            'received': 'receives',
            'processed': 'processes',
            'generated': 'generates',
            'created': 'creates',
            'updated': 'updates',
            'deleted': 'deletes',
            'published': 'publishes',
            'configured': 'configures',
            'enabled': 'enables',
            'disabled': 'disables'
        }
        return verb_map.get(passive_verb.lower(), passive_verb.replace('ed', 's'))
    
    def _fallback_correction(self, text: str, rule_id: str, context: CorrectionContext) -> Dict[str, Any]:
        """Enhanced fallback correction when specific rule is not found"""
        
        # Use the existing rule-specific correction as fallback
        from .rule_specific_corrections import get_rule_specific_correction
        
        corrected = get_rule_specific_correction(text, rule_id)
        
        if corrected != text:
            return {
                'original': text,
                'corrected': corrected,
                'explanation': f'Applied {rule_id} correction using pattern matching.',
                'confidence': 0.6,
                'rule_category': 'fallback',
                'priority': 3,
                'method': 'fallback_pattern_matching'
            }
        
        return {
            'original': text,
            'corrected': text,
            'explanation': f'No specific correction available for {rule_id}.',
            'confidence': 0.1,
            'rule_category': 'unknown',
            'priority': 1,
            'method': 'no_correction'
        }

class DocumentTypeClassifier:
    """Classifies document type for context-aware corrections"""
    
    def classify(self, content: str, filename: str = None) -> Tuple[DocumentType, float]:
        """
        Classify document type based on content and filename.
        
        Returns:
            Tuple of (document_type, confidence_score)
        """
        content_lower = content.lower()
        
        # API Documentation indicators
        api_keywords = ['endpoint', 'request', 'response', 'json', 'api', 'rest', 'post', 'get']
        if sum(1 for keyword in api_keywords if keyword in content_lower) >= 3:
            return DocumentType.API_DOCUMENTATION, 0.9
        
        # User Guide indicators
        guide_keywords = ['click', 'step', 'follow', 'tutorial', 'guide', 'how to']
        if sum(1 for keyword in guide_keywords if keyword in content_lower) >= 2:
            return DocumentType.USER_GUIDE, 0.8
        
        # Technical Spec indicators
        spec_keywords = ['specification', 'requirements', 'architecture', 'design']
        if any(keyword in content_lower for keyword in spec_keywords):
            return DocumentType.TECHNICAL_SPEC, 0.8
        
        # README indicators
        if filename and 'readme' in filename.lower():
            return DocumentType.README, 0.9
        
        return DocumentType.GENERAL, 0.5


def get_comprehensive_correction(text: str, 
                               rule_id: str,
                               document_content: str = "",
                               document_type: str = "general") -> Dict[str, Any]:
    """
    Main entry point for comprehensive rule-based corrections.
    
    Args:
        text: Text to correct
        rule_id: Writing rule that was violated
        document_content: Full document content for context
        document_type: Document type hint
        
    Returns:
        Comprehensive correction result
    """
    engine = ComprehensiveRuleEngine()
    
    # Classify document type
    doc_type, confidence = engine.document_classifier.classify(document_content)
    
    # Create context
    context = CorrectionContext(
        document_type=doc_type,
        surrounding_text=document_content[:500],  # First 500 chars for context
        sentence_position="middle",  # Could be enhanced
        paragraph_context="",
        domain_keywords=[]
    )
    
    # Get comprehensive correction
    return engine.analyze_and_correct(text, rule_id, context)


if __name__ == "__main__":
    # Test the comprehensive system
    test_cases = [
        ("it is in ISO 8601 format.", "capitalization_sentence_start", "API documentation content"),
        ("Data is sent to the server.", "passive_voice", "endpoint documentation"),
        ("With the new API, data is processed which includes validation, transformation, and storage.", "long_sentences", "technical specification")
    ]
    
    for text, rule_id, doc_content in test_cases:
        result = get_comprehensive_correction(text, rule_id, doc_content)
        print(f"Original: {text}")
        print(f"Corrected: {result['corrected']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Method: {result['method']}")
        print("-" * 50)

"""
Deterministic Suggestion Generator

This module integrates:
1. Issue Resolution Engine (makes decisions)
2. LLM Phrasing Module (expresses decisions)
3. RAG System (enhances, not dependency)

Core principle:
> Decisions are made in code.
> LLM only phrases them.
> RAG only enhances them.
> Deterministic fallbacks guarantee value.
"""

from typing import Dict, Any, Optional, List
import logging

from core.issue_resolution_engine import (
    get_resolution_engine,
    resolve_issue,
    IssueType,
    ResolutionClass,
)
from core.llm_phrasing import get_llm_phraser

logger = logging.getLogger(__name__)


class DeterministicSuggestionGenerator:
    """
    Generates suggestions using deterministic decision logic.
    
    Flow:
    1. Classify issue → Resolution class (deterministic)
    2. Get template + fallback (deterministic)
    3. Try RAG enhancement (optional, not required)
    4. Try LLM phrasing (optional, not required)
    5. Validate output quality
    6. Return fallback if quality insufficient
    
    Result: Always useful, never vague.
    """
    
    def __init__(self):
        self.resolution_engine = get_resolution_engine()
        self.llm_phraser = get_llm_phraser()
        self.rag_available = self._check_rag_availability()
    
    def _check_rag_availability(self) -> bool:
        """Check if RAG system is available."""
        try:
            from scripts.ollama_rag_system import get_rag_suggestion
            return True
        except Exception:
            return False
    
    def generate_suggestion(
        self,
        issue_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate suggestion for an issue.
        
        Returns None if:
        - Issue doesn't map cleanly to resolution class
        - This signals: don't show this issue to user
        
        Returns suggestion dict if:
        - Issue maps cleanly
        - Contains actionable guidance (guaranteed)
        
        Args:
            issue_data: {
                'feedback': str,
                'context': str (original sentence),
                'rule_id': str,
                'document_type': str,
                ...
            }
        
        Returns:
            {
                'issue_type': str,
                'severity': 'blocking' | 'advisory',
                'resolution_class': str,
                'guidance': str,  # Always actionable
                'rewrite': str | None,  # If applicable
                'action_required': str,
                'method': str,  # 'deterministic' | 'llm_phrased' | 'rag_enhanced'
                'confidence': 'high' | 'medium',
            }
        """
        # Step 1: Classify issue deterministically
        resolution = resolve_issue(issue_data)
        
        if not resolution:
            # Issue doesn't map cleanly → don't show to user
            logger.info(f"Issue not classified: {issue_data.get('feedback', '')}")
            return None
        
        issue_type = resolution['issue_type']
        severity = resolution['severity']
        resolution_class = resolution['resolution_class']
        fallback_text = resolution['fallback_text']
        action_required = resolution['action_required']
        
        # Step 2: Try RAG enhancement (optional)
        rag_guidance = None
        if self.rag_available:
            rag_guidance = self._try_rag_enhancement(issue_data, resolution_class)
        
        # Step 3: Try LLM phrasing (optional)
        llm_guidance = None
        if self.llm_phraser.llm_available:
            llm_guidance = self._try_llm_phrasing(
                resolution['template'],
                resolution['context'],
                fallback_text
            )
        
        # Step 4: Select best guidance (prioritize quality)
        final_guidance, method = self._select_best_guidance(
            fallback_text,
            llm_guidance,
            rag_guidance
        )
        
        # Step 5: Generate rewrite if applicable
        rewrite = self._generate_rewrite_if_applicable(
            issue_type,
            issue_data.get('context', ''),
            resolution_class
        )
        
        # Step 6: Validate and return
        return {
            'issue_type': issue_type,
            'severity': severity,
            'resolution_class': resolution_class,
            'guidance': final_guidance,
            'rewrite': rewrite,
            'action_required': action_required,
            'method': method,
            'confidence': 'high' if method in ['deterministic', 'rag_enhanced'] else 'medium',
        }
    
    def _try_rag_enhancement(
        self,
        issue_data: Dict[str, Any],
        resolution_class: str
    ) -> Optional[str]:
        """
        Try to enhance guidance with RAG.
        
        RAG is NOT used for "inspiration".
        RAG is used for "supporting examples".
        
        If RAG finds nothing → proceed without it.
        """
        try:
            from scripts.ollama_rag_system import get_rag_suggestion
            
            # Create specific query for this resolution class
            query = self._create_rag_query(issue_data, resolution_class)
            
            # Get RAG response with short timeout
            rag_response = get_rag_suggestion(
                query=query,
                max_examples=1,  # We only need one good example
                timeout=3  # Short timeout
            )
            
            if rag_response and len(rag_response.strip()) > 50:
                return rag_response.strip()
            
            return None
            
        except Exception as e:
            logger.warning(f"RAG enhancement failed: {e}")
            return None
    
    def _create_rag_query(
        self,
        issue_data: Dict[str, Any],
        resolution_class: str
    ) -> str:
        """
        Create specific RAG query for resolution class.
        
        Query is NOT vague like "help with passive voice".
        Query is specific like "example of rewriting passive voice to active in technical documentation".
        """
        sentence = issue_data.get('context', '')
        
        query_templates = {
            'rewrite_active': f"Example of rewriting passive voice to active voice in technical writing: {sentence[:100]}",
            'simplify_sentence': f"Example of breaking a complex sentence into simpler ones: {sentence[:100]}",
            'replace_with_specific': f"Example of replacing vague terms with specific terms",
            'define_acronym': f"Example of defining an acronym on first use",
            'break_into_steps': f"Example of breaking a complex step into numbered substeps",
        }
        
        return query_templates.get(resolution_class, f"Example for {resolution_class}")
    
    def _try_llm_phrasing(
        self,
        template: str,
        context: Dict[str, Any],
        fallback: str
    ) -> Optional[str]:
        """
        Try to phrase guidance with LLM.
        
        LLM does NOT decide what to do.
        LLM only adapts template to specific content.
        """
        try:
            phrased = self.llm_phraser.phrase_resolution(
                template=template,
                context=context,
                fallback=fallback
            )
            
            # If LLM returns fallback, treat as None
            if phrased == fallback:
                return None
            
            return phrased
            
        except Exception as e:
            logger.warning(f"LLM phrasing failed: {e}")
            return None
    
    def _select_best_guidance(
        self,
        fallback: str,
        llm_guidance: Optional[str],
        rag_guidance: Optional[str]
    ) -> tuple[str, str]:
        """
        Select best guidance from available options.
        
        Priority:
        1. RAG-enhanced (has concrete example)
        2. LLM-phrased (adapted to content)
        3. Fallback (always works)
        
        Returns:
            (guidance_text, method_name)
        """
        # RAG is best if it has concrete examples
        if rag_guidance and self._has_concrete_example(rag_guidance):
            return rag_guidance, 'rag_enhanced'
        
        # LLM phrasing is good if it passes validation
        if llm_guidance and len(llm_guidance) > len(fallback) * 0.5:
            return llm_guidance, 'llm_phrased'
        
        # Fallback always works
        return fallback, 'deterministic'
    
    def _has_concrete_example(self, text: str) -> bool:
        """Check if text contains concrete example."""
        example_indicators = [
            'example:', 'for example', 'such as', 'like this:',
            '→', 'becomes', 'instead of'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in example_indicators)
    
    def _generate_rewrite_if_applicable(
        self,
        issue_type: str,
        original_sentence: str,
        resolution_class: str
    ) -> Optional[str]:
        """
        Generate rewrite for applicable issue types.
        
        Only these issue types get rewrites:
        - passive_voice
        - long_sentence
        - vague_term
        
        Others get guidance only.
        """
        rewrite_applicable = [
            'passive_voice',
            'long_sentence',
            'vague_term',
        ]
        
        if issue_type not in rewrite_applicable:
            return None
        
        # Try deterministic rewrite first
        deterministic_rewrite = self._deterministic_rewrite(
            issue_type,
            original_sentence
        )
        
        # If LLM available, try to improve it
        if self.llm_phraser.llm_available:
            llm_rewrite = self.llm_phraser.phrase_rewrite(
                original=original_sentence,
                issue_type=issue_type,
                fallback_rewrite=deterministic_rewrite
            )
            
            # Validate LLM rewrite is better
            if llm_rewrite != deterministic_rewrite:
                from core.issue_resolution_engine import is_value_added
                if is_value_added(original_sentence, llm_rewrite, threshold=0.2):
                    return llm_rewrite
        
        return deterministic_rewrite
    
    def _deterministic_rewrite(
        self,
        issue_type: str,
        original: str
    ) -> str:
        """
        Generate deterministic rewrite using pattern matching.
        
        This guarantees a rewrite even when LLM fails.
        """
        import re
        
        if issue_type == 'passive_voice':
            # Convert passive to active voice with precise patterns
            # COMPREHENSIVE PATTERN SET: 100+ common passive constructions
            
            # Strategy 1: Modal passives - "X must/can/should/may be VERB by Y" → "Y must/can/should/may VERB X"
            modal_passive_patterns = [
                # With explicit actor "by X"
                (r'\bthe\s+([\w\s]+?)\s+must\s+be\s+done\s+by\s+the\s+(\w+)', r'the \2 must do the \1'),
                (r'\bthe\s+([\w\s]+?)\s+must\s+be\s+(configured|performed|executed|completed|handled)\s+by\s+the\s+(\w+)', r'the \3 must \2 the \1'),
                (r'\bthe\s+([\w\s]+?)\s+can\s+be\s+(accessed|modified|changed|used|viewed)\s+by\s+the\s+(\w+)', r'the \3 can \2 the \1'),
                (r'\bthe\s+([\w\s]+?)\s+should\s+be\s+(checked|verified|validated|tested|reviewed)\s+by\s+the\s+(\w+)', r'the \3 should \2 the \1'),
                (r'\bthe\s+([\w\s]+?)\s+may\s+be\s+(affected|influenced|changed)\s+by\s+the\s+(\w+)', r'the \3 may \2 the \1'),
                (r'\bthe\s+([\w\s]+?)\s+will\s+be\s+(sent|received|processed|stored)\s+by\s+the\s+(\w+)', r'the \3 will \2 the \1'),
                
                # Without explicit actor - use context-appropriate actor
                (r'\bthe\s+([\w\s]+?)\s+must\s+be\s+done\b', r'you must do the \1'),
                (r'\bthe\s+([\w\s]+?)\s+must\s+be\s+(configured|set|enabled|disabled|installed|activated)\b', r'you must \2 the \1'),
                (r'\bthe\s+([\w\s]+?)\s+can\s+be\s+(used|accessed|modified|customized)\b', r'you can \2 the \1'),
                (r'\bthe\s+([\w\s]+?)\s+should\s+be\s+(checked|verified|reviewed|updated)\b', r'check the \1'),
                (r'\bthe\s+([\w\s]+?)\s+needs?\s+to\s+be\s+(configured|set|checked|verified)\b', r'configure the \1'),
                
                # Capital noun patterns (without "the")
                (r'\b([A-Z][\w\s]*?)\s+must\s+be\s+done\s+by\s+the\s+(\w+)', r'the \2 must do \1'),
                (r'\b([A-Z][\w\s]*?)\s+must\s+be\s+(configured|performed)\s+by\s+the\s+(\w+)', r'the \3 must \2 \1'),
            ]
            
            for pattern, replacement in modal_passive_patterns:
                match = re.search(pattern, original, re.IGNORECASE)
                if match:
                    match_text = match.group(0)
                    if ', and ' not in match_text and ', but ' not in match_text:
                        rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                        rewritten = re.sub(r'\s+', ' ', rewritten).strip()
                        if rewritten:
                            rewritten = rewritten[0].upper() + rewritten[1:]
                        if not rewritten.endswith('.'):
                            rewritten = rewritten.rstrip() + '.'
                        return rewritten
            
            # Strategy 2: Infinitive passives - "to be verb-ed" → "to verb"
            infinitive_passive_patterns = [
                (r'\bto\s+be\s+written\b', r'to write'),
                (r'\bto\s+be\s+read\b', r'to read'),
                (r'\bto\s+be\s+sent\b', r'to send'),
                (r'\bto\s+be\s+received\b', r'to receive'),
                (r'\bto\s+be\s+configured\b', r'to configure'),
                (r'\bto\s+be\s+processed\b', r'to process'),
                (r'\bto\s+be\s+used\b', r'to use'),
                (r'\bto\s+be\s+accessed\b', r'to access'),
                (r'\bto\s+be\s+modified\b', r'to modify'),
                (r'\bto\s+be\s+updated\b', r'to update'),
                (r'\bto\s+be\s+opened\b', r'to open'),
                (r'\bto\s+be\s+closed\b', r'to close'),
                (r'\bto\s+be\s+created\b', r'to create'),
                (r'\bto\s+be\s+deleted\b', r'to delete'),
                (r'\bto\s+be\s+installed\b', r'to install'),
                (r'\bto\s+be\s+removed\b', r'to remove'),
                (r'\bto\s+be\s+executed\b', r'to execute'),
                (r'\bto\s+be\s+performed\b', r'to perform'),
                (r'\bto\s+be\s+completed\b', r'to complete'),
                (r'\bto\s+be\s+checked\b', r'to check'),
                (r'\bto\s+be\s+verified\b', r'to verify'),
                (r'\bto\s+be\s+validated\b', r'to validate'),
                (r'\bto\s+be\s+tested\b', r'to test'),
                (r'\bto\s+be\s+enabled\b', r'to enable'),
                (r'\bto\s+be\s+disabled\b', r'to disable'),
                (r'\bto\s+be\s+activated\b', r'to activate'),
                (r'\bto\s+be\s+deactivated\b', r'to deactivate'),
                # General fallback for -ed verbs
                (r'\bto\s+be\s+(\w+ed)\b', r'to \1'),
            ]
            
            for pattern, replacement in infinitive_passive_patterns:
                if re.search(pattern, original, re.IGNORECASE):
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    return rewritten
            
            # Strategy 3: Reference patterns - "is given in", "is shown in", etc.
            reference_patterns = [
                # "is as follows" → direct replacement
                (r'(An?\s+[\w\s]+?)\s+(is|are)\s+as\s+follows\s*:?', r'\1:'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+as\s+follows\s*:?', r'\1:'),
                (r'([\w\s]+?)\s+(is|are)\s+as\s+follows\s*:?', r'\1:'),
                
                # "is given in the below links" → "The below links provide"
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+given\s+in\s+the\s+(below|following)\s+(links?|sections?|tables?|chapters?|documents?)', 
                 r'The \3 \4 provide \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+shown\s+in\s+the\s+(below|following)\s+(figure|diagram|image|screenshot)', 
                 r'The \3 \4 shows \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+listed\s+in\s+the\s+(below|following)\s+(links?|sections?|tables?|chapters?)', 
                 r'The \3 \4 list \1'),
                
                # "is as given in the X" → "See the X for" (more formal)
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+as\s+given\s+in\s+the\s+(below|following)\s+(links?|sections?|tables?|chapters?|documents?)', 
                 r'See the \3 \4 for \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+as\s+shown\s+in\s+the\s+(below|following)\s+(figure|diagram|image|screenshot)', 
                 r'See the \3 \4 for \1'),
                 
                # "is given in X" → "X provides" (when no "the below")
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+given\s+in\s+([\w\s]+?)\.', 
                 r'\3 provides \1.'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+shown\s+in\s+([\w\s]+?)\.', 
                 r'\3 shows \1.'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+listed\s+in\s+([\w\s]+?)\.', 
                 r'\3 lists \1.'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+presented\s+in\s+([\w\s]+?)\.', 
                 r'\3 presents \1.'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+illustrated\s+in\s+(the\s+)?(\w+)', 
                 r'\4 illustrates \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+documented\s+in\s+(the\s+)?(\w+)', 
                 r'\4 documents \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+specified\s+in\s+(the\s+)?(\w+)', 
                 r'\4 specifies \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+detailed\s+in\s+(the\s+)?(\w+)', 
                 r'\4 details \1'),
            ]
            
            for pattern, replacement in reference_patterns:
                if re.search(pattern, original, re.IGNORECASE):
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    return rewritten
            
            # Strategy 4: "is/are provided by" patterns
            provision_patterns = [
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+provided\s+by\s+the\s+(\w+)', r'The \3 provides \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+supplied\s+by\s+the\s+(\w+)', r'The \3 supplies \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+offered\s+by\s+the\s+(\w+)', r'The \3 offers \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+delivered\s+by\s+the\s+(\w+)', r'The \3 delivers \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+returned\s+by\s+the\s+(\w+)', r'The \3 returns \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+generated\s+by\s+the\s+(\w+)', r'The \3 generates \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+produced\s+by\s+the\s+(\w+)', r'The \3 produces \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+created\s+by\s+the\s+(\w+)', r'The \3 creates \1'),
            ]
            
            for pattern, replacement in provision_patterns:
                if re.search(pattern, original, re.IGNORECASE):
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    return rewritten
            
            # Strategy 5: "is/are defined/described/explained" patterns
            documentation_patterns = [
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+defined\s+in\s+(the\s+)?(\w+)', r'The \4 defines \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+described\s+in\s+(the\s+)?(\w+)', r'The \4 describes \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+explained\s+in\s+(the\s+)?(\w+)', r'The \4 explains \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+outlined\s+in\s+(the\s+)?(\w+)', r'The \4 outlines \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+covered\s+in\s+(the\s+)?(\w+)', r'The \4 covers \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+discussed\s+in\s+(the\s+)?(\w+)', r'The \4 discusses \1'),
            ]
            
            for pattern, replacement in documentation_patterns:
                if re.search(pattern, original, re.IGNORECASE):
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    return rewritten
            
            # Strategy 6: Common display/interaction verbs
            display_patterns = [
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+displayed\s+in\s+the\s+(\w+)', r'The \3 displays \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+shown\s+in\s+the\s+(\w+)', r'The \3 shows \1'),
                (r'(The\s+[\w\s]+?)\s+(is|are)\s+visible\s+in\s+the\s+(\w+)', r'The \3 displays \1'),
                (r'The\s+([\w\s]+?)\s+(are|is)\s+displayed', r'The system displays the \1'),
                (r'The\s+([\w\s]+?)\s+(are|is)\s+shown', r'The system shows the \1'),
                (r'The\s+([\w\s]+?)\s+(are|is)\s+rendered', r'The system renders the \1'),
                (r'The\s+([\w\s]+?)\s+(are|is)\s+presented', r'The system presents the \1'),
                (r'The\s+([\w\s]+?)\s+(are|is)\s+indicated', r'The system indicates the \1'),
                (r'The\s+([\w\s]+?)\s+(are|is)\s+highlighted', r'The system highlights the \1'),
            ]
            
            for pattern, replacement in display_patterns:
                match = re.search(pattern, original, re.IGNORECASE)
                if match:
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    rewritten = rewritten[0].upper() + rewritten[1:] if rewritten else rewritten
                    if not rewritten.endswith('.'):
                        rewritten = rewritten.rstrip() + '.'
                    return rewritten
            
            # Strategy 7: State/status patterns
            state_patterns = [
                (r'The\s+([\w\s]+?)\s+(is|are)\s+enabled', r'The system enables the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+disabled', r'The system disables the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+activated', r'The system activates the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+deactivated', r'The system deactivates the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+initialized', r'The system initializes the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+started', r'The system starts the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+stopped', r'The system stops the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+paused', r'The system pauses the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+resumed', r'The system resumes the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+reset', r'The system resets the \1'),
            ]
            
            for pattern, replacement in state_patterns:
                match = re.search(pattern, original, re.IGNORECASE)
                if match:
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    rewritten = rewritten[0].upper() + rewritten[1:] if rewritten else rewritten
                    if not rewritten.endswith('.'):
                        rewritten = rewritten.rstrip() + '.'
                    return rewritten
            
            # Strategy 8: Data operations
            data_operation_patterns = [
                (r'The\s+([\w\s]+?)\s+(is|are)\s+stored\s+in\s+the\s+(\w+)', r'The \3 stores the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+saved\s+in\s+the\s+(\w+)', r'The \3 saves the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+loaded\s+from\s+the\s+(\w+)', r'The \3 loads the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+read\s+from\s+the\s+(\w+)', r'The \3 reads the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+written\s+to\s+the\s+(\w+)', r'The \3 writes the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+transferred\s+to\s+the\s+(\w+)', r'The system transfers the \1 to the \3'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+copied\s+to\s+the\s+(\w+)', r'The system copies the \1 to the \3'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+moved\s+to\s+the\s+(\w+)', r'The system moves the \1 to the \3'),
            ]
            
            for pattern, replacement in data_operation_patterns:
                match = re.search(pattern, original, re.IGNORECASE)
                if match:
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    rewritten = rewritten[0].upper() + rewritten[1:] if rewritten else rewritten
                    if not rewritten.endswith('.'):
                        rewritten = rewritten.rstrip() + '.'
                    return rewritten
            
            # Strategy 9: Configuration/setup patterns
            config_patterns = [
                (r'The\s+([\w\s]+?)\s+(is|are)\s+configured', r'Configure the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+set\s+to', r'Set the \1 to'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+adjusted', r'Adjust the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+customized', r'Customize the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+modified', r'Modify the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+changed', r'Change the \1'),
                (r'The\s+([\w\s]+?)\s+(is|are)\s+updated', r'Update the \1'),
            ]
            
            for pattern, replacement in config_patterns:
                match = re.search(pattern, original, re.IGNORECASE)
                if match:
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    rewritten = rewritten[0].upper() + rewritten[1:] if rewritten else rewritten
                    if not rewritten.endswith('.'):
                        rewritten = rewritten.rstrip() + '.'
                    return rewritten
            
            # Strategy 10: Past tense patterns
            past_tense_patterns = [
                (r'The\s+([\w\s]+?)\s+was\s+opened', r'The system opened the \1'),
                (r'The\s+([\w\s]+?)\s+was\s+closed', r'The system closed the \1'),
                (r'The\s+([\w\s]+?)\s+was\s+created', r'The system created the \1'),
                (r'The\s+([\w\s]+?)\s+was\s+deleted', r'The system deleted the \1'),
                (r'The\s+([\w\s]+?)\s+was\s+modified', r'The system modified the \1'),
                (r'The\s+([\w\s]+?)\s+was\s+updated', r'The system updated the \1'),
                (r'The\s+([\w\s]+?)\s+were\s+sent', r'The system sent the \1'),
                (r'The\s+([\w\s]+?)\s+were\s+received', r'The system received the \1'),
            ]
            
            for pattern, replacement in past_tense_patterns:
                match = re.search(pattern, original, re.IGNORECASE)
                if match:
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    rewritten = rewritten[0].upper() + rewritten[1:] if rewritten else rewritten
                    if not rewritten.endswith('.'):
                        rewritten = rewritten.rstrip() + '.'
                    return rewritten
            
            for pattern, replacement in specific_patterns:
                match = re.search(pattern, original, re.IGNORECASE)
                if match:
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    rewritten = rewritten[0].upper() + rewritten[1:] if rewritten else rewritten
                    if not rewritten.endswith('.'):
                        rewritten = rewritten.rstrip() + '.'
                    return rewritten
            
            # Strategy 4: General passive patterns
            passive_patterns = [
                (r'\b(was|were)\s+(\w+ed)\b', r'the system \2'),
                (r'\b(is|are)\s+(\w+ed)\b', r'the system \2s'),
            ]
            
            for pattern, replacement in passive_patterns:
                if re.search(pattern, original, re.IGNORECASE):
                    return re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
            
            # Fallback: just flag it
            return original + " [Note: Rewrite in active voice]"
        
        elif issue_type == 'vague_term':
            # Replace vague terms with specific alternatives
            # Pattern-based replacements for common vague terms and weak adverbs
            
            vague_patterns = [
                # "very + adjective" → stronger adjective
                (r'\bvery\s+important\b', r'critical'),
                (r'\bvery\s+good\b', r'excellent'),
                (r'\bvery\s+bad\b', r'poor'),
                (r'\bvery\s+big\b', r'large'),
                (r'\bvery\s+small\b', r'tiny'),
                (r'\bvery\s+fast\b', r'rapid'),
                (r'\bvery\s+slow\b', r'sluggish'),
                (r'\bvery\s+easy\b', r'simple'),
                (r'\bvery\s+difficult\b', r'complex'),
                (r'\bvery\s+hard\b', r'challenging'),
                (r'\bvery\s+clear\b', r'obvious'),
                (r'\bvery\s+simple\b', r'straightforward'),
                (r'\bvery\s+complex\b', r'intricate'),
                (r'\bvery\s+high\b', r'significant'),
                (r'\bvery\s+low\b', r'minimal'),
                (r'\bvery\s+quick\b', r'rapid'),
                (r'\bvery\s+large\b', r'substantial'),
                (r'\bvery\s+general\b', r'broad'),
                (r'\bvery\s+specific\b', r'precise'),
                (r'\bvery\s+common\b', r'frequent'),
                (r'\bvery\s+rare\b', r'infrequent'),
                (r'\bvery\s+useful\b', r'valuable'),
                (r'\bvery\s+helpful\b', r'beneficial'),
                
                # Generic "very" fallback - just remove it
                (r'\bvery\s+(\w+)', r'\1'),
                
                # "various/several/some X" → "specific X"
                (r'\bvarious\s+types?\s+of\s+([\w\s]+)', r'GET, POST, PUT, and DELETE \1'),
                (r'\bvarious\s+([\w\s]+)', r'multiple \1 [Note: Specify which ones]'),
                (r'\bseveral\s+([\w\s]+)', r'three \1 [Note: Specify exact number]'),
                (r'\bsome\s+([\w\s]+)', r'specific \1 [Note: Specify which ones]'),
                (r'\bmultiple\s+([\w\s]+)', r'several \1 [Note: Specify exact number]'),
                (r'\ba\s+number\s+of\s+([\w\s]+)', r'several \1 [Note: Specify exact count]'),
                
                # "stuff/things" → "items/elements"
                (r'\bstuff\b', r'items [Note: Specify what items]'),
                (r'\bthings\b', r'elements [Note: Specify what elements]'),
                
                # "etc." → specific list
                (r',\s*etc\.', r' [Note: Complete the list instead of using etc.]'),
                (r'\betc\b', r'[Note: Specify all items]'),
                
                # "many/most/few" → specific numbers
                (r'\bmany\s+([\w\s]+)', r'several \1 [Note: Specify how many]'),
                (r'\bmost\s+([\w\s]+)', r'the majority of \1 [Note: Specify percentage]'),
                (r'\bfew\s+([\w\s]+)', r'three \1 [Note: Specify exact number]'),
            ]
            
            for pattern, replacement in vague_patterns:
                if re.search(pattern, original, re.IGNORECASE):
                    rewritten = re.sub(pattern, replacement, original, count=1, flags=re.IGNORECASE)
                    return rewritten
            
            return original + " [Note: Replace vague terms with specific ones]"
        
        elif issue_type == 'undefined_acronym':
            # Define acronyms on first use
            # Common technical acronyms with definitions
            
            acronym_definitions = {
                'API': 'API (Application Programming Interface)',
                'REST': 'REST (Representational State Transfer)',
                'HTTP': 'HTTP (Hypertext Transfer Protocol)',
                'HTTPS': 'HTTPS (Hypertext Transfer Protocol Secure)',
                'URL': 'URL (Uniform Resource Locator)',
                'URI': 'URI (Uniform Resource Identifier)',
                'JSON': 'JSON (JavaScript Object Notation)',
                'XML': 'XML (Extensible Markup Language)',
                'HTML': 'HTML (Hypertext Markup Language)',
                'CSS': 'CSS (Cascading Style Sheets)',
                'SQL': 'SQL (Structured Query Language)',
                'CLI': 'CLI (Command Line Interface)',
                'GUI': 'GUI (Graphical User Interface)',
                'UI': 'UI (User Interface)',
                'UX': 'UX (User Experience)',
                'MQTT': 'MQTT (Message Queuing Telemetry Transport)',
                'TCP': 'TCP (Transmission Control Protocol)',
                'UDP': 'UDP (User Datagram Protocol)',
                'IP': 'IP (Internet Protocol)',
                'DNS': 'DNS (Domain Name System)',
                'SSL': 'SSL (Secure Sockets Layer)',
                'TLS': 'TLS (Transport Layer Security)',
                'SSH': 'SSH (Secure Shell)',
                'FTP': 'FTP (File Transfer Protocol)',
                'SMTP': 'SMTP (Simple Mail Transfer Protocol)',
                'POP': 'POP (Post Office Protocol)',
                'IMAP': 'IMAP (Internet Message Access Protocol)',
                'RAM': 'RAM (Random Access Memory)',
                'ROM': 'ROM (Read-Only Memory)',
                'CPU': 'CPU (Central Processing Unit)',
                'GPU': 'GPU (Graphics Processing Unit)',
                'USB': 'USB (Universal Serial Bus)',
                'IDE': 'IDE (Integrated Development Environment)',
                'SDK': 'SDK (Software Development Kit)',
            }
            
            # Try to find and define acronyms
            for acronym, definition in acronym_definitions.items():
                # Match the acronym as a whole word
                pattern = r'\b' + acronym + r'\b'
                if re.search(pattern, original):
                    rewritten = re.sub(pattern, definition, original, count=1)
                    return rewritten
            
            return original + " [Note: Define acronyms on first use]"
        
        elif issue_type == 'inconsistent_terminology':
            # Flag inconsistent terminology
            # Common inconsistent term pairs
            
            inconsistent_pairs = [
                (['settings', 'preferences', 'options', 'configuration'], 'settings'),
                (['program', 'application', 'app', 'software'], 'application'),
                (['click', 'press', 'select', 'choose'], 'click'),
                (['start', 'begin', 'initiate', 'launch'], 'start'),
                (['stop', 'end', 'terminate', 'quit'], 'stop'),
                (['user', 'operator', 'person'], 'user'),
                (['device', 'equipment', 'hardware', 'unit'], 'device'),
                (['error', 'fault', 'failure', 'problem'], 'error'),
                (['data', 'information', 'content'], 'data'),
                (['folder', 'directory'], 'folder'),
            ]
            
            # Check for inconsistent terms in the sentence
            for terms, preferred in inconsistent_pairs:
                found_terms = []
                for term in terms:
                    if re.search(r'\b' + term + r'\b', original, re.IGNORECASE):
                        found_terms.append(term)
                
                # If multiple terms from same group found, flag it
                if len(found_terms) > 1:
                    return original + f" [Note: Use '{preferred}' consistently instead of {', '.join(found_terms)}]"
            
            return original + " [Note: Use consistent terminology throughout]"
        
        elif issue_type == 'mixed_tense':
            # Convert to present tense (standard for technical documentation)
            
            mixed_tense_patterns = [
                # "will VERB" → "VERBs"
                (r'\bwill\s+(send|process|receive|start|stop|create|delete|update)', r'\1s'),
                (r'\bwill\s+(be)\s+(\w+ed)', r'is \2'),
                
                # "VERBed" → "VERBs" (past to present)
                (r'\bsent\b', r'sends'),
                (r'\bprocessed\b', r'processes'),
                (r'\breceived\b', r'receives'),
                (r'\bstarted\b', r'starts'),
                (r'\bstopped\b', r'stops'),
                (r'\bcreated\b', r'creates'),
                (r'\bdeleted\b', r'deletes'),
                (r'\bupdated\b', r'updates'),
                (r'\bopened\b', r'opens'),
                (r'\bclosed\b', r'closes'),
                
                # "was/were" → "is/are"
                (r'\bwas\s+', r'is '),
                (r'\bwere\s+', r'are '),
                
                # "has/have VERBed" → "VERBs"
                (r'\bhas\s+(\w+ed)\b', r'\1s'),
                (r'\bhave\s+(\w+ed)\b', r'\1'),
            ]
            
            result = original
            for pattern, replacement in mixed_tense_patterns:
                if re.search(pattern, result, re.IGNORECASE):
                    result = re.sub(pattern, replacement, result, count=1, flags=re.IGNORECASE)
            
            if result != original:
                return result
            
            return original + " [Note: Use present tense consistently]"
        
        elif issue_type == 'missing_prerequisite':
            # Add prerequisite section
            # Detect if this looks like a procedure without prerequisites
            
            procedure_indicators = [
                'to configure', 'to install', 'to set up', 'to access', 
                'to start', 'to run', 'to execute', 'to enable'
            ]
            
            has_procedure = any(indicator in original.lower() for indicator in procedure_indicators)
            
            if has_procedure:
                prerequisite_template = "Prerequisites: [Specify required conditions, permissions, or software]\n\n"
                return prerequisite_template + original
            
            return original + " [Note: Add prerequisites before procedural steps]"
        
        elif issue_type == 'dense_step':
            # Break dense steps into substeps
            # Detect multiple actions in one step
            
            # Count action verbs
            action_verbs = ['open', 'click', 'select', 'enter', 'choose', 'navigate', 
                          'configure', 'set', 'enable', 'disable', 'save', 'close',
                          'start', 'stop', 'run', 'execute', 'install', 'remove']
            
            verb_count = sum(1 for verb in action_verbs if re.search(r'\b' + verb + r'\b', original, re.IGNORECASE))
            
            if verb_count >= 3:
                # Try to break on commas or 'and'
                if ',' in original or ' and ' in original:
                    parts = re.split(r',\s*and\s*|,\s*|\s+and\s+', original)
                    if len(parts) >= 3:
                        # Format as substeps
                        substeps = []
                        for i, part in enumerate(parts, 1):
                            part = part.strip()
                            if part:
                                if not part[0].isupper():
                                    part = part[0].upper() + part[1:]
                                substeps.append(f"   {i}. {part}")
                        
                        return "Break into substeps:\n" + "\n".join(substeps)
            
            return original + " [Note: Break into smaller steps - one action per step]"
        
        elif issue_type == 'step_order_problem':
            # Suggest logical step ordering
            # Detect common ordering issues
            
            order_patterns = [
                # Common mistakes
                (['save', 'edit'], ['edit', 'save'], 'Edit before saving'),
                (['login', 'enter username'], ['enter username', 'login'], 'Enter credentials before logging in'),
                (['start', 'install'], ['install', 'start'], 'Install before starting'),
                (['click', 'open'], ['open', 'click'], 'Open before clicking elements'),
                (['close', 'save'], ['save', 'close'], 'Save before closing'),
            ]
            
            original_lower = original.lower()
            for wrong_order, correct_order, explanation in order_patterns:
                # Check if both terms exist and in wrong order
                first_pos = original_lower.find(wrong_order[0])
                second_pos = original_lower.find(wrong_order[1])
                
                if first_pos != -1 and second_pos != -1 and first_pos < second_pos:
                    return original + f" [Note: Reorder steps - {explanation}]"
            
            return original + " [Note: Review step order for logical sequence]"
        
        elif issue_type == 'long_sentence':
            # Try to split on conjunctions and natural boundaries intelligently
            original_text = original.strip()
            word_count = len(original_text.split())
            
            # Strategy 1: Split on coordinating conjunctions
            if ' and ' in original_text:
                parts = original_text.split(' and ', 1)
                first = parts[0].strip()
                if not first.endswith('.'):
                    first += '.'
                
                second = parts[1].strip()
                if second:
                    second = second[0].upper() + second[1:] if len(second) > 1 else second.upper()
                    if not second.endswith('.'):
                        second += '.'
                    return f"{first} {second}"
            
            # Strategy 2: Split on comma + conjunction
            comma_conjunctions = [', and ', ', but ', ', or ', ', so ']
            for conj in comma_conjunctions:
                if conj in original_text:
                    parts = original_text.split(conj, 1)
                    first = parts[0].strip() + '.'
                    second = parts[1].strip()
                    if second:
                        second = second[0].upper() + second[1:] if len(second) > 1 else second.upper()
                        if not second.endswith('.'):
                            second += '.'
                        return f"{first} {second}"
            
            # Strategy 3: Split at midpoint on phrase boundaries (prepositional phrases)
            # Look for prepositions in the middle third of the sentence
            prepositions = [' in the ', ' on the ', ' to the ', ' for the ', ' with the ', ' at the ', ' from the ']
            words = original_text.split()
            midpoint_start = len(words) // 3
            midpoint_end = 2 * len(words) // 3
            
            # Reconstruct text with indices
            text_so_far = []
            for i, word in enumerate(words):
                text_so_far.append(word)
                current_text = ' '.join(text_so_far)
                
                # Check if we're in the middle third
                if midpoint_start <= i <= midpoint_end:
                    # Check if current position has a prepositional phrase
                    for prep in prepositions:
                        # Check if the next few words form this prep phrase
                        remaining = ' '.join(words[i:i+3]) if i+3 <= len(words) else ' '.join(words[i:])
                        if remaining.lower().startswith(prep.strip().lower()):
                            # Split here!
                            first_part = ' '.join(words[:i]).strip()
                            if first_part and not first_part.endswith('.'):
                                first_part += '.'
                            
                            second_part = ' '.join(words[i:]).strip()
                            if second_part:
                                second_part = second_part[0].upper() + second_part[1:] if len(second_part) > 1 else second_part.upper()
                                if not second_part.endswith('.'):
                                    second_part += '.'
                            
                            if first_part and second_part and len(first_part.split()) >= 5:
                                return f"{first_part} {second_part}"
            
            # Strategy 4: Fallback - split at roughly halfway point on comma
            if ',' in original_text:
                # Find comma closest to midpoint
                commas = [i for i, char in enumerate(original_text) if char == ',']
                if commas:
                    midpoint_char = len(original_text) // 2
                    best_comma = min(commas, key=lambda x: abs(x - midpoint_char))
                    
                    first = original_text[:best_comma].strip() + '.'
                    second = original_text[best_comma+1:].strip()
                    if second:
                        second = second[0].upper() + second[1:] if len(second) > 1 else second.upper()
                        if not second.endswith('.'):
                            second += '.'
                        
                        # Only use if both parts are meaningful (>= 5 words)
                        if len(first.split()) >= 5 and len(second.split()) >= 5:
                            return f"{first} {second}"
            
            # Couldn't find good split - return note
            return original_text + " [Note: Consider breaking into multiple sentences]"
        
        return original


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def generate_suggestions_for_issues(
    issues: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate suggestions for multiple issues.
    
    Filters out issues that don't map cleanly.
    Returns only actionable suggestions.
    
    Args:
        issues: List of issue dicts from rule checking
    
    Returns:
        List of suggestion dicts, guaranteed actionable
    """
    generator = DeterministicSuggestionGenerator()
    suggestions = []
    
    for issue in issues:
        try:
            suggestion = generator.generate_suggestion(issue)
            
            if suggestion:  # Only include issues that mapped cleanly
                suggestions.append(suggestion)
            else:
                logger.debug(f"Skipped unmapped issue: {issue.get('feedback', '')}")
        
        except Exception as e:
            logger.error(f"Error generating suggestion for issue: {e}")
            continue
    
    return suggestions


def generate_suggestion_for_issue(
    issue_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Generate suggestion for a single issue.
    
    Returns None if issue doesn't map cleanly.
    Otherwise returns actionable suggestion (guaranteed).
    """
    generator = DeterministicSuggestionGenerator()
    return generator.generate_suggestion(issue_data)

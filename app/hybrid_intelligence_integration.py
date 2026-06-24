"""
Hybrid Intelligence Integration for DocScanner
============================================

This file adds hybrid intelligence capabilities to your existing DocScanner app
without changing your original UI. It provides the backend functionality to 
integrate phi3:mini and llama3:8b models with your RAG system.
"""

import sys
import os
import re
import logging
import time

logger = logging.getLogger(__name__)

# Add the parent directory and tools directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))

try:
    from hybrid_intelligence_rag_system import HybridIntelligenceRAGSystem, FlaggedIssue
    HYBRID_SYSTEM_AVAILABLE = True
except ImportError as e:
    HYBRID_SYSTEM_AVAILABLE = False
    print(f"Hybrid intelligence RAG system not available: {e}")
    # Define dummy classes to prevent errors
    class HybridIntelligenceRAGSystem:
        pass
    class FlaggedIssue:
        pass

# Global system instance
_hybrid_system = None

def get_hybrid_system():
    """Get or create the hybrid intelligence system"""
    global _hybrid_system
    if not HYBRID_SYSTEM_AVAILABLE:
        return None
    if _hybrid_system is None:
        try:
            _hybrid_system = HybridIntelligenceRAGSystem()
        except Exception as e:
            print(f"Failed to initialize hybrid system: {e}")
            return None
    return _hybrid_system

def enhance_ai_suggestion_with_hybrid_intelligence(
    feedback_text, 
    sentence_context, 
    document_type='general', 
    complexity='default',
    adjacent_context=None,  # NEW: adjacent sentences
    multiple_feedback=None,  # NEW: list of all feedback messages for Master Fix
    document_metadata=None,   # NEW: global document metadata (title, etc)
    rule_metadata=None       # NEW: direct data from the rule engine
):
    """
    Enhance AI suggestions using hybrid intelligence (phi3:mini + llama3:8b)
    
    This function integrates with your existing ai_suggestion endpoint
    to provide smarter, context-aware suggestions.
    
    Args:
        adjacent_context: Dict with 'previous_sentence' and/or 'next_sentence' keys
        multiple_feedback: List of all feedback strings for this sentence
        document_metadata: Dict with 'title', 'version', etc.
        rule_metadata: Dict containing 'category', 'rule_id', etc.
    """
    if not HYBRID_SYSTEM_AVAILABLE:
        return {
            'success': False,
            'error': 'Hybrid intelligence system not available - module not found',
            'suggestion': sentence_context,
            'ai_answer': 'Hybrid intelligence system is not configured.',
            'confidence': 'low',
            'method': 'unavailable'
        }
    
    try:
        # Get the hybrid system
        hybrid_system = get_hybrid_system()
        
        # 🟢 SELF-EVOLVING RAG: Check for high-confidence learned patterns first
        # This allows the system to recall your previous successful fixes instantly
        try:
            if hybrid_system and hasattr(hybrid_system, 'knowledge_collection'):
                # Search for near-exact matches of this sentence + feedback
                search_query = f"Issue: {feedback_text} | Original: {sentence_context}"
                results = hybrid_system.knowledge_collection.query(
                    query_texts=[search_query],
                    n_results=1,
                    where={"type": "learned_correction"}
                )
                
                if (results and results['metadatas'] and results['metadatas'][0] and 
                    results['distances'] and results['distances'][0][0] < 0.1):
                    
                    match = results['metadatas'][0][0]
                    logger.info(f"🧠 RAG RECALL: Found high-confidence match (dist: {results['distances'][0][0]:.4f})")
                    
                    return {
                        'success': True,
                        'suggestion': match.get('corrected'),
                        'ai_answer': f"Recalled your previous successful fix for this pattern. (Matched '{match.get('feedback')}')",
                        'confidence': 'high',
                        'method': 'learned_rag_recall',
                        'model_used': 'rag_memory',
                        'intelligence_mode': 'instant',
                        'processing_time': 0,
                        'sources': ['Self-Evolved RAG Memory'],
                        'context_used': {
                            'document_type': document_type,
                            'issue_type': 'Learned Pattern',
                            'original_match': match.get('original')
                        }
                    }
        except Exception as rag_e:
            logger.warning(f"⚠️ Learned RAG recall check failed: {rag_e}")

        # Special handling for requirement sentences to use "you" instead of "developer"
        if ("passive" in feedback_text.lower() and 
            "requirement must be met" in sentence_context.lower()):
            return {
                'success': True,
                'suggestion': sentence_context.replace("The following requirement must be met", "You must meet this requirement").replace("requirement must be met", "you must meet this requirement"),
                'ai_answer': "Converted passive voice to active voice using 'you' for direct, personal communication instead of referring to specific roles like 'developer'.",
                'confidence': 'high',
                'method': 'hybrid_requirement_override',
                'model_used': 'pattern_match',
                'intelligence_mode': 'fast',
                'processing_time': 0,
                'sources': ['Direct pattern matching for requirement sentences'],
                'context_used': {
                    'document_type': document_type,
                    'issue_type': 'Passive voice',
                    'complexity': complexity,
                    'primary_ai': 'hybrid_intelligence'
                }
            }
        
        # Determine issue type - STRATEGY: Prefer Metadata > Keyword Match > Default
        issue_type = "General"
        
        # 0. Check Rule Authority to prevent overriding intentional no_change rules
        if rule_metadata and isinstance(rule_metadata, dict):
            decision_type = rule_metadata.get('decision_type')
            if decision_type in ['no_change', 'guide', 'explain']:
                logger.info(f"🛑 Hybrid AI skipping rewrite due to rule authority decision: {decision_type}")
                return {
                    'success': False,
                    'error': f'Rule authority requested {decision_type}',
                    'fallback_available': True
                }
        # 1. Use metadata from the rule engine if available (Universal mapping)
        if rule_metadata and isinstance(rule_metadata, dict):
            category = rule_metadata.get('category', '').lower()
            category_mapping = {
                'voice': 'Passive voice',
                'adverb': 'Adverb overuse',
                'consistency': 'Consistency',
                'procedural': 'Procedural clarity',
                'tone': 'Inappropriate tone',
                'grammar': 'Grammar and usage',
                'style': 'Technical style',
                'structural': 'Document structure'
            }
            if category in category_mapping:
                issue_type = category_mapping[category]
                logger.info(f"📍 Mapped issue to '{issue_type}' using rule metadata")
        
        # 2. Fallback to keyword matching if metadata didn't resolve it
        if issue_type == "General":
            feedback_lower = feedback_text.lower()
            if "passive" in feedback_lower:
                issue_type = "Passive voice"
            elif "adverb" in feedback_lower:
                issue_type = "Adverb overuse"  
            elif "long sentence" in feedback_lower:
                issue_type = "Long sentences"
            elif "consistency" in feedback_lower or "consistent" in feedback_lower:
                issue_type = "Consistency"
            elif "vague" in feedback_lower:
                issue_type = "Vague terms"
            elif "imperative" in feedback_lower:
                issue_type = "Procedural steps"
            elif "complex" in feedback_lower:
                issue_type = "Complex sentences"
            elif "redundant" in feedback_lower:
                issue_type = "Redundant phrases"
            elif "click on" in feedback_lower or "modal" in feedback_lower:
                issue_type = "Modal fluff"
            elif "unclear" in feedback_lower:
                issue_type = "Unclear antecedents"
            elif "tone" in feedback_lower:
                issue_type = "Inappropriate tone"
        
        # Create flagged issue object
        flagged_issue = FlaggedIssue(
            sentence=sentence_context,
            issue=issue_type,
            context=document_type,
            complexity=complexity,
            severity='medium'
        )
        
        # Generate hybrid intelligence solution
        # Pass multiple feedback items if available (Master Fix)
        # Pass document metadata for global context
        result = hybrid_system.generate_hybrid_solution(
            flagged_issue, 
            multiple_issues=multiple_feedback,
            document_metadata=document_metadata,
            adjacent_context=adjacent_context  # NEW: Surrounding sentences
        )
        
        if result.get('success'):
            # Post-process suggestion to fix common generation artifacts
            raw_suggestion = result.get('corrected', '') or ''

            def _sanitize_suggestion(suggestion_text, original_sentence):
                s = suggestion_text
                # Fix stray punctuation and duplicated periods
                s = s.replace(' .', '.').replace('..', '.').replace('. .', '.')
                # Fix broken 'and. displayed' type splits
                s = s.replace('and. displayed', 'and displayed')
                s = s.replace('and. shown', 'and shown')
                s = re.sub(r'\s+', ' ', s).strip()

                # Heuristic: convert simple 'is <verb>ed [and <verb>ed]*' to active voice
                try:
                    lower = s.lower()
                    m = re.search(r"\bis ((?:\w+ed)(?: (?:and|, ) (?:\w+ed))*)", lower)
                    if m:
                        verbs = re.findall(r"\w+ed", m.group(1))
                        active_verbs = []
                        for v in verbs:
                            stem = v[:-2]
                            if stem.endswith('y'):
                                active = stem[:-1] + 'ies'
                            elif stem.endswith(('s', 'x', 'z', 'ch', 'sh', 'o')):
                                active = stem + 'es'
                            else:
                                active = stem + 's'
                            active_verbs.append(active)

                        active_phrase = ' and '.join(active_verbs)

                        # Try to extract a sensible subject from the original sentence
                        subj = original_sentence.split(' is ')[0].strip()
                        tail_match = re.search(r'(in the .*table.*)$', original_sentence, re.IGNORECASE)
                        tail = (' ' + tail_match.group(1)) if tail_match else ''
                        if subj:
                            s = f"{subj} {active_phrase}{tail}"

                except Exception:
                    # Best-effort only; fall back to sanitized string
                    pass

                # Capitalize first character
                if s:
                    s = s[0].upper() + s[1:]
                return s

            # Prefer a model-generated active-voice rewrite when possible
            try:
                hybrid_system = get_hybrid_system()
                mode = getattr(hybrid_system, 'determine_intelligence_mode')(flagged_issue)
                active_rewrite = None
                try:
                    active_rewrite = hybrid_system.rewrite_in_active_voice(sentence_context, mode)
                except Exception:
                    active_rewrite = None

                if active_rewrite:
                    cleaned = _sanitize_suggestion(active_rewrite, sentence_context)
                else:
                    cleaned = _sanitize_suggestion(raw_suggestion, sentence_context)
            except Exception:
                cleaned = _sanitize_suggestion(raw_suggestion, sentence_context)

            # 🛡️ VALIDATION: Ensure the suggestion actually improves the sentence
            try:
                # 1. Structural value validation
                from .intelligent_ai_improvement import is_value_added
                is_valid, reason = is_value_added(sentence_context, cleaned, feedback_text)
                
                if not is_valid:
                    logger.warning(f"❌ Hybrid AI validation failed: {reason}")
                    return {
                        'success': False,
                        'error': f'Hybrid intelligence validation failed: {reason}',
                        'fallback_available': True
                    }
                    
                # 2. Strict tense validation if the issue is tense-related
                if 'tense' in feedback_text.lower() or 'non_simple_present' in feedback_text.lower():
                    try:
                        from .rules.simple_present_normalization import validate_simple_present_rewrite
                        valid_tense, tense_reason = validate_simple_present_rewrite(sentence_context, cleaned)
                        if not valid_tense:
                            logger.warning(f"❌ Hybrid AI tense validation failed: {tense_reason}")
                            return {
                                'success': False,
                                'error': f'Tense validation failed: {tense_reason}',
                                'fallback_available': True
                            }
                    except ImportError:
                        pass
                        
            except Exception as val_e:
                logger.warning(f"Validation check failed, continuing anyway: {val_e}")

            return {
                'success': True,
                'suggestion': cleaned,
                'ai_answer': result.get('reasoning', ''),
                'confidence': 'high',
                'method': f"hybrid_{result.get('model_used', 'unknown')}",
                'model_used': result.get('model_used'),
                'intelligence_mode': result.get('intelligence_mode'),
                'processing_time': result.get('processing_time', 0),
                'sources': result.get('sources', []),
                'context_used': {
                    'document_type': document_type,
                    'issue_type': issue_type,
                    'complexity': complexity,
                    'primary_ai': 'hybrid_intelligence'
                }
            }
        else:
            # Return error but maintain compatibility
            return {
                'success': False,
                'error': result.get('error', 'Hybrid intelligence unavailable'),
                'fallback_available': True
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Hybrid intelligence error: {str(e)}',
            'fallback_available': True
        }

def get_hybrid_system_status():
    """Get the status of the hybrid intelligence system"""
    # Check if module is available first
    if not HYBRID_SYSTEM_AVAILABLE:
        return {
            'ollama_running': False,
            'hybrid_ready': False,
            'phi3_available': False,
            'llama3_available': False,
            'error': 'Hybrid intelligence RAG system module not found in tools directory',
            'available_models': [],
            'rag_loaded': False,
            'system_available': False
        }
    
    try:
        import requests
        from urllib.parse import urljoin
        # Allow configuring Ollama URL via env var (useful when running in Docker Compose)
        ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        tags_url = urljoin(ollama_url, '/api/tags')

        try:
            response = requests.get(tags_url, timeout=5)
        except requests.exceptions.ConnectionError:
            return {
                'ollama_running': False,
                'hybrid_ready': False,
                'phi3_available': False,
                'llama3_available': False,
                'error': f'Ollama not running at {ollama_url}. Start Ollama to enable hybrid intelligence.',
                'available_models': [],
                'rag_loaded': False,
                'system_available': True,
                'ollama_url': ollama_url
            }
        except Exception as e:
            return {
                'ollama_running': False,
                'hybrid_ready': False,
                'phi3_available': False,
                'llama3_available': False,
                'error': str(e),
                'available_models': [],
                'rag_loaded': False,
                'system_available': True,
                'ollama_url': ollama_url
            }

        if response.status_code != 200:
            return {
                'ollama_running': False,
                'hybrid_ready': False,
                'phi3_available': False,
                'llama3_available': False,
                'error': f'Ollama returned status {response.status_code}',
                'available_models': [],
                'rag_loaded': False,
                'system_available': True,
                'ollama_url': ollama_url
            }

        try:
            models_data = response.json()
            available_models = [m.get('name', '') for m in models_data.get('models', []) if isinstance(m, dict)]

            # Normalize model names for tolerant checks
            lowered = [m.lower() for m in available_models]
            phi3_available = any('phi3' in m or m.startswith('phi3-') for m in lowered)
            llama3_available = any('llama3' in m or m.startswith('llama3-') for m in lowered)

            hybrid_ready = phi3_available and llama3_available

            return {
                'ollama_running': True,
                'ollama_url': ollama_url,
                'phi3_available': phi3_available,
                'llama3_available': llama3_available,
                'hybrid_ready': hybrid_ready,
                'available_models': available_models,
                'rag_loaded': True,
                'system_available': True
            }
        except Exception as e:
            return {'ollama_running': True, 'error': f'Failed to parse Ollama response: {str(e)}'}

    except Exception as e:
        return {'error': f'System check failed: {str(e)}'}

def batch_hybrid_suggestions(issues_list):
    """
    Process multiple issues with hybrid intelligence
    
    Expected format for issues_list:
    [
        {
            'sentence': 'sentence text',
            'issue_type': 'issue type', 
            'context': 'context info',
            'complexity': 'fast/deep/default'
        },
        ...
    ]
    """
    try:
        hybrid_system = get_hybrid_system()
        results = []
        
        for issue_data in issues_list:
            try:
                flagged_issue = FlaggedIssue(
                    sentence=issue_data.get('sentence', ''),
                    issue=issue_data.get('issue_type', 'General'),
                    context=issue_data.get('context', ''),
                    complexity=issue_data.get('complexity', 'default'),
                    severity=issue_data.get('severity', 'medium')
                )
                
                result = hybrid_system.generate_hybrid_solution(flagged_issue)
                results.append(result)
                
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'original_sentence': issue_data.get('sentence', '')
                })
        
        return {
            'success': True,
            'total_processed': len(issues_list),
            'successful': len([r for r in results if r.get('success')]),
            'failed': len([r for r in results if not r.get('success')]),
            'results': results
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Batch processing failed: {str(e)}'
        }

def record_golden_correction(original_sentence: str, corrected_sentence: str, feedback_text: str):
    """Bridge function to record a high-quality human-approved correction into RAG memory"""
    try:
        hybrid_system = get_hybrid_system()
        if hybrid_system and hasattr(hybrid_system, 'add_learned_pattern'):
            return hybrid_system.add_learned_pattern(original_sentence, corrected_sentence, feedback_text)
        return False
    except Exception as e:
        logger.warning(f"Failed to record golden correction: {e}")
        return False
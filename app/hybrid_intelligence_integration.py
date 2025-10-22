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

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hybrid_intelligence_rag_system import HybridIntelligenceRAGSystem, FlaggedIssue

# Global system instance
_hybrid_system = None

def get_hybrid_system():
    """Get or create the hybrid intelligence system"""
    global _hybrid_system
    if _hybrid_system is None:
        _hybrid_system = HybridIntelligenceRAGSystem()
    return _hybrid_system

def enhance_ai_suggestion_with_hybrid_intelligence(feedback_text, sentence_context, document_type='general', complexity='default'):
    """
    Enhance AI suggestions using hybrid intelligence (phi3:mini + llama3:8b)
    
    This function integrates with your existing ai_suggestion endpoint
    to provide smarter, context-aware suggestions.
    """
    try:
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
        
        # Get the hybrid system
        hybrid_system = get_hybrid_system()
        
        # Determine issue type from feedback
        issue_type = "General"
        feedback_lower = feedback_text.lower()
        
        if "passive" in feedback_lower:
            issue_type = "Passive voice"
        elif "adverb" in feedback_lower:
            issue_type = "Adverb overuse"  
        elif "long sentence" in feedback_lower:
            issue_type = "Long sentences"
        elif "vague" in feedback_lower:
            issue_type = "Vague terms"
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
        result = hybrid_system.generate_hybrid_solution(flagged_issue)
        
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
    try:
        import requests
        from urllib.parse import urljoin
        # Allow configuring Ollama URL via env var (useful when running in Docker Compose)
        ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        tags_url = urljoin(ollama_url, '/api/tags')

        try:
            response = requests.get(tags_url, timeout=5)
        except requests.exceptions.ConnectionError:
            return {'ollama_running': False, 'error': f'Ollama not running at {ollama_url}'}
        except Exception as e:
            return {'ollama_running': False, 'error': str(e)}

        if response.status_code != 200:
            return {'ollama_running': False, 'error': f'Ollama returned status {response.status_code}'}

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
                'rag_loaded': True
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
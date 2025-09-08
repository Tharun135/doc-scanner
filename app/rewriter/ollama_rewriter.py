"""
Ollama-based intelligent document rewriter
Integrates the rewriting capabilities from doc-scanner-ai into doc-scanner
"""

import requests
import json
import logging
import textstat
from typing import Dict, Optional
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class OllamaRewriter:
    def __init__(self, config_path: str = None):
        """Initialize the Ollama rewriter with configuration."""
        self.config = self._load_config(config_path)
        self.api_url = self.config.get("api_url", "http://localhost:11434/api/generate")
        self.models = self.config.get("models", {
            "fast": "tinyllama:latest",
            "balanced": "phi3:mini", 
            "quality": "llama3:8b"
        })
        self.timeouts = self.config.get("timeouts", {
            "quick": 15,
            "standard": 30,
            "high": 45
        })
        
    def _load_config(self, config_path: str = None) -> Dict:
        """Load configuration from JSON file."""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ollama_config.json")
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                return config_data.get("ollama_config", {})
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in config file: {config_path}, using defaults")
            return {}

    def calculate_readability(self, text: str) -> Dict:
        """Calculate comprehensive readability scores for the given text."""
        if not text or not text.strip():
            logger.warning("Empty text provided for readability calculation")
            return {
                "flesch_reading_ease": 0,
                "flesch_kincaid_grade": 0,
                "smog_index": 0,
                "gunning_fog": 0,
                "automated_readability_index": 0,
                "difficulty_level": "unknown"
            }
        
        try:
            scores = {
                "flesch_reading_ease": round(textstat.flesch_reading_ease(text), 2),
                "flesch_kincaid_grade": round(textstat.flesch_kincaid_grade(text), 2),
                "smog_index": round(textstat.smog_index(text), 2),
                "gunning_fog": round(textstat.gunning_fog(text), 2),
                "automated_readability_index": round(textstat.automated_readability_index(text), 2)
            }
            
            # Determine difficulty level based on Flesch Reading Ease
            flesch_score = scores["flesch_reading_ease"]
            if flesch_score >= 90:
                difficulty = "very easy"
            elif flesch_score >= 80:
                difficulty = "easy"
            elif flesch_score >= 70:
                difficulty = "fairly easy"
            elif flesch_score >= 60:
                difficulty = "standard"
            elif flesch_score >= 50:
                difficulty = "fairly difficult"
            elif flesch_score >= 30:
                difficulty = "difficult"
            else:
                difficulty = "very difficult"
                
            scores["difficulty_level"] = difficulty
            
            logger.debug(f"Readability scores calculated: Flesch={scores['flesch_reading_ease']}, Grade={scores['flesch_kincaid_grade']}")
            
            return scores
            
        except Exception as e:
            logger.error(f"Error calculating readability: {e}")
            return {
                "flesch_reading_ease": 0,
                "flesch_kincaid_grade": 0,
                "smog_index": 0,
                "gunning_fog": 0,
                "automated_readability_index": 0,
                "difficulty_level": "error"
            }

    def _ollama_generate(self, text_to_rewrite: str, mode: str = "balanced") -> str:
        """Call Ollama API to generate rewritten text with smart analysis."""
        
        # First, analyze the text to create targeted instructions
        analysis = self._analyze_text_complexity(text_to_rewrite)
        
        # Create targeted prompt based on analysis
        system_prompt = self._create_smart_prompt(mode, analysis)
        model = self.models.get(mode, self.models.get("balanced", "phi3:mini"))
        timeout = self.timeouts.get(mode, self.timeouts.get("standard", 30))
        
        logger.info(f"Calling Ollama with model: {model}, mode: {mode}, timeout: {timeout}s")
        logger.info(f"Analysis: {analysis['avg_words']} avg words/sentence, {len(analysis['issues'])} issues found")
        
        try:
            # Use the smart, targeted prompt
            full_prompt = f"{system_prompt}\n\nOriginal text:\n{text_to_rewrite}\n\nRewritten text:"
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower for more consistent results
                    "top_p": 0.9,
                    "num_predict": min(len(text_to_rewrite) * 1.5, 400),  # More reasonable length
                    "num_ctx": 4096,  # Larger context
                    "repeat_penalty": 1.1
                }
            }
            
            logger.debug(f"Using smart prompt with {len(analysis['issues'])} specific improvements")
            
            response = requests.post(self.api_url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            logger.info(f"Ollama response received. Length: {len(generated_text)} chars")
            
            if not generated_text:
                logger.warning(f"Empty response from Ollama for mode: {mode}")
                return self._fallback_rewrite(text_to_rewrite)
            
            # Check if the response is just repeating the original
            if generated_text.lower().strip() == text_to_rewrite.lower().strip():
                logger.warning(f"Ollama returned identical text for mode: {mode}. Using fallback.")
                return self._fallback_rewrite(text_to_rewrite)
            
            return generated_text
            
        except requests.RequestException as e:
            logger.error(f"Ollama API error for mode {mode}: {e}")
            return self._fallback_rewrite(text_to_rewrite)
        except Exception as e:
            logger.error(f"Unexpected error in Ollama generation: {e}")
            return self._fallback_rewrite(text_to_rewrite)
    
    def _analyze_text_complexity(self, text: str) -> Dict:
        """Analyze text to identify specific areas for improvement"""
        import re
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return {'avg_words': 0, 'issues': []}
        
        # Calculate metrics
        word_counts = [len(s.split()) for s in sentences]
        avg_words = sum(word_counts) / len(word_counts)
        
        issues = []
        
        # Check for long sentences
        if avg_words > 20:
            issues.append("long_sentences")
        
        # Check for technical terms
        technical_patterns = [
            r'\b(implementation|methodology|functionality|configuration|utilization)\b',
            r'\b\w+tion\b', r'\b\w+ment\b'  # Nominalizations
        ]
        
        technical_count = 0
        for pattern in technical_patterns:
            technical_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        if technical_count > 3:
            issues.append("technical_jargon")
        
        # Check for passive voice
        passive_patterns = [r'\b(is|are|was|were)\s+\w+ed\b', r'\bwill be\s+\w+ed\b']
        passive_count = 0
        for pattern in passive_patterns:
            passive_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        if passive_count > len(sentences) * 0.3:
            issues.append("passive_voice")
        
        return {
            'avg_words': avg_words,
            'issues': issues,
            'sentence_count': len(sentences)
        }
    
    def _create_smart_prompt(self, mode: str, analysis: Dict) -> str:
        """Create a targeted prompt based on text analysis"""
        
        # More aggressive prompts for technical content
        if "technical_jargon" in analysis['issues']:
            base_prompt = """REWRITE this technical documentation in PLAIN ENGLISH that anyone can understand. 
            
RULES:
- Use simple, everyday words (not technical terms)
- Write short sentences (under 20 words each)  
- Explain what things DO, not what they ARE
- Replace all jargon with simple language

EXAMPLES:
- "payload" → "data package" or "information"
- "indicates" → "shows" or "tells you"
- "structure" → "layout" or "organization"  
- "schema" → "format" or "template"
- "configuration" → "settings" or "setup"
- "This section describes..." → "Here's how to..."
- "The recommended structure..." → "The best way to organize..."

Transform this technical content into simple, clear instructions:"""
        
        else:
            base_prompts = {
                "clarity": "Rewrite this text to be crystal clear and easy to understand.",
                "simplicity": "Rewrite this text using simple, everyday language that anyone can understand.",
                "balanced": "Rewrite this text to be clearer and more professional while keeping the original meaning."
            }
            base_prompt = base_prompts.get(mode, base_prompts["balanced"])
        
        instructions = [base_prompt]
        
        # Add specific instructions based on analysis
        if "long_sentences" in analysis['issues']:
            instructions.append("Break every long sentence into 2-3 shorter sentences (maximum 15 words each).")
        
        if "passive_voice" in analysis['issues']:
            instructions.append("Use active voice - say WHO does WHAT clearly.")
        
        # For technical content, add more specific guidance
        if analysis.get('avg_words', 0) > 25:
            instructions.append("Make this sound like you're explaining it to a friend, not writing a manual.")
        
        return '\n'.join(instructions)
    
    def _fallback_rewrite(self, text: str) -> str:
        """Enhanced rule-based rewriting when AI fails"""
        import re
        
        # If text is very short, try simple AI prompt as fallback
        if len(text) < 200:
            try:
                simple_payload = {
                    "model": "phi3:mini",
                    "prompt": f"Rewrite in simple words: {text}",
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 100}
                }
                response = requests.post(self.api_url, json=simple_payload, timeout=15)
                if response.status_code == 200:
                    result = response.json().get("response", "").strip()
                    if result and result != text:
                        return result
            except:
                pass  # Fall back to rule-based
        
        # Apply rule-based transformations
        rewritten = text
        
        # Replace technical terms with simple alternatives
        technical_replacements = {
            r'\bpayloadType\b': 'data type',
            r'\bencoding\b': 'format',
            r'\bmsgStructureScheme\b': 'message format',
            r'\bmsgStructureSchemeVersion\b': 'format version',
            r'\bprovideAppInstanceId\b': 'app ID',
            r'\bpayloadMsgType\b': 'message type',
            r'\baccessmode\b': 'access method',
            r'\bconnectionname\b': 'connection name',
            r'\bcollectionname\b': 'group name',
            r'\bimplementation\b': 'setup',
            r'\bmethodology\b': 'method',
            r'\bfunctionality\b': 'features',
            r'\bconfiguration\b': 'settings',
            r'\butilization\b': 'use',
            r'\bfacilitates?\b': 'helps',
            r'\bindicates?\b': 'shows',
            r'\bcontains?\b': 'has'
        }
        
        for pattern, replacement in technical_replacements.items():
            rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
        
        # Simplify complex phrases
        phrase_replacements = {
            r'\bThis section describes\b': 'Here is how',
            r'\bThe recommended structure\b': 'The best way to structure',
            r'\bis as follows\b': 'is',
            r'\bthe above elements\b': 'these parts',
            r'\bThis indicates\b': 'This shows',
            r'\bPossible Values\b': 'Options',
            r'\bin bulk mode\b': 'all together'
        }
        
        for pattern, replacement in phrase_replacements.items():
            rewritten = re.sub(pattern, replacement, rewritten, flags=re.IGNORECASE)
        
        # Break up very long sentences (basic)
        sentences = re.split(r'([.!?]+)', rewritten)
        improved_sentences = []
        
        for i in range(0, len(sentences), 2):
            if i < len(sentences):
                sentence = sentences[i].strip()
                punct = sentences[i+1] if i+1 < len(sentences) else ''
                
                # If sentence is very long (>30 words), try to break it
                if len(sentence.split()) > 30 and ' and ' in sentence:
                    parts = sentence.split(' and ', 1)
                    improved_sentences.append(parts[0] + '.')
                    improved_sentences.append(' ' + parts[1] + punct)
                else:
                    improved_sentences.append(sentence + punct)
        
        return ''.join(improved_sentences)

    def rewrite_document(self, content: str, mode: str = "balanced") -> Dict:
        """
        Rewrite document content with emphasis on readability and clarity.
        
        Args:
            content: The text content to rewrite
            mode: Rewriting mode - 'clarity', 'simplicity', or 'balanced'
            
        Returns:
            Dictionary with rewritten text, readability scores, and metadata
        """
        if not content or not content.strip():
            return {
                "success": False,
                "error": "No content provided",
                "original_text": content,
                "rewritten_text": content,
                "scores": {"original": {}, "rewritten": {}}
            }
        
        try:
            # Calculate original readability scores
            original_scores = self.calculate_readability(content)
            
            logger.info(f"Starting document rewrite in {mode} mode. Original length: {len(content)} characters")
            
            # Two-pass rewriting for better results
            if mode == "balanced":
                # Pass 1: Clarity improvement
                logger.info("Pass 1: Improving clarity...")
                draft = self._ollama_generate(content, "clarity")
                
                # Pass 2: Final polish for balance
                logger.info("Pass 2: Final balancing...")
                final_text = self._ollama_generate(draft, "balanced")
            else:
                # Single pass for specific modes
                logger.info(f"Single pass: {mode} rewriting...")
                final_text = self._ollama_generate(content, mode)
            
            # Calculate rewritten text readability scores
            rewritten_scores = self.calculate_readability(final_text)
            
            # Safety checks for score validity
            def safe_score(score, default=0):
                return score if isinstance(score, (int, float)) and not (score != score) else default  # Check for NaN
            
            original_flesch = safe_score(original_scores.get("flesch_reading_ease", 0))
            rewritten_flesch = safe_score(rewritten_scores.get("flesch_reading_ease", 0))
            original_grade = safe_score(original_scores.get("flesch_kincaid_grade", 0))
            rewritten_grade = safe_score(rewritten_scores.get("flesch_kincaid_grade", 0))
            
            # Calculate improvement metrics
            readability_improvement = rewritten_flesch - original_flesch
            grade_improvement = original_grade - rewritten_grade  # Lower grade is better
            length_change = len(final_text) - len(content)
            
            # Check if text was actually changed
            text_was_changed = final_text.strip() != content.strip()
            
            logger.info(f"Rewriting complete. New length: {len(final_text)} characters. "
                       f"Readability improvement: {readability_improvement:.1f} points. "
                       f"Text changed: {text_was_changed}")
            
            # Format improvements for frontend display
            improvements = {
                "readability_change": {
                    "before": round(original_flesch, 1),
                    "after": round(rewritten_flesch, 1),
                    "improvement": round(readability_improvement, 1)
                },
                "grade_level_change": {
                    "before": round(original_grade, 1),
                    "after": round(rewritten_grade, 1),
                    "improvement": round(grade_improvement, 1)
                },
                "length_change": {
                    "before": len(content),
                    "after": len(final_text),
                    "improvement": round(((len(final_text) - len(content)) / len(content)) * 100 if len(content) > 0 else 0, 1)
                },
                "improved": {
                    "before": "Original",
                    "after": "Improved" if text_was_changed else "Unchanged",
                    "improvement": round(readability_improvement, 1) if text_was_changed else 0
                }
            }
            
            return {
                "success": True,
                "original_text": content,
                "rewritten_text": final_text,
                "mode": mode,
                "scores": {
                    "original": original_scores,
                    "rewritten": rewritten_scores
                },
                "improvements": improvements,
                "metadata": {
                    "model_used": self.models.get(mode, "phi3:mini"),
                    "processing_mode": mode,
                    "timestamp": __import__('datetime').datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in document rewriting: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_text": content,
                "rewritten_text": content,
                "scores": {
                    "original": self.calculate_readability(content),
                    "rewritten": {}
                }
            }

    def rewrite_sentence(self, sentence: str, mode: str = "clarity") -> Dict:
        """
        Rewrite a single sentence for improved clarity.
        
        Args:
            sentence: The sentence to rewrite
            mode: Rewriting mode
            
        Returns:
            Dictionary with rewritten sentence and scores
        """
        if not sentence or not sentence.strip():
            return {
                "success": False,
                "error": "No sentence provided",
                "original": sentence,
                "rewritten": sentence
            }
        
        try:
            # Use single pass for sentences
            rewritten = self._ollama_generate(sentence, mode)
            
            return {
                "success": True,
                "original": sentence,
                "rewritten": rewritten,
                "mode": mode,
                "scores": {
                    "original": self.calculate_readability(sentence),
                    "rewritten": self.calculate_readability(rewritten)
                }
            }
            
        except Exception as e:
            logger.error(f"Error rewriting sentence: {e}")
            return {
                "success": False,
                "error": str(e),
                "original": sentence,
                "rewritten": sentence
            }

# Singleton instance
_rewriter_instance = None

def get_rewriter() -> OllamaRewriter:
    """Get the global rewriter instance."""
    global _rewriter_instance
    if _rewriter_instance is None:
        _rewriter_instance = OllamaRewriter()
    return _rewriter_instance

# Convenience functions for backward compatibility
def rewrite_document(content: str, mode: str = "balanced") -> Dict:
    """Rewrite document content."""
    return get_rewriter().rewrite_document(content, mode)

def calculate_readability(text: str) -> Dict:
    """Calculate readability scores."""
    return get_rewriter().calculate_readability(text)

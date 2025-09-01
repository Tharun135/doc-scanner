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
            "quick": 5,
            "standard": 10,
            "high": 15
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

    def _ollama_generate(self, prompt: str, mode: str = "balanced") -> str:
        """Call Ollama API to generate rewritten text."""
        system_prompts = {
            "clarity": """You are an expert technical writer. Rewrite the provided text for maximum clarity while preserving all original meaning and intent. Focus on:
- Clear, direct language
- Proper sentence structure  
- Logical flow and organization
- Removing ambiguity
- Maintaining technical accuracy

Return only the improved text without explanations.""",

            "simplicity": """You are an expert editor specializing in plain language. Rewrite the provided text using simpler, more accessible language suitable for a general audience (grade 9-11 reading level). Focus on:
- Shorter, clearer sentences
- Common vocabulary instead of jargon
- Active voice where appropriate
- Concrete rather than abstract language
- Maintaining all original information

Return only the simplified text without explanations.""",

            "balanced": """You are an expert technical writer. Improve this text for better readability while maintaining professionalism and accuracy. Focus on:
- Clear, concise language
- Proper sentence structure
- Logical organization
- Professional tone
- Accessibility for the target audience

Return only the improved text without explanations."""
        }
        
        system_prompt = system_prompts.get(mode, system_prompts["balanced"])
        model = self.models.get(mode, self.models.get("balanced", "phi3:mini"))
        timeout = self.timeouts.get(mode, self.timeouts.get("standard", 10))
        
        try:
            payload = {
                "model": model,
                "prompt": f"{system_prompt}\n\nText to improve:\n{prompt}",
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.9,
                    "num_predict": len(prompt) + 100,  # Dynamic length based on input
                    "num_ctx": min(4096, len(prompt) * 3)  # Dynamic context
                }
            }
            
            response = requests.post(self.api_url, json=payload, timeout=timeout)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            if not generated_text:
                logger.warning(f"Empty response from Ollama for mode: {mode}")
                return prompt  # Return original if no response
                
            return generated_text
            
        except requests.RequestException as e:
            logger.error(f"Ollama API error for mode {mode}: {e}")
            return prompt  # Return original text if API fails
        except Exception as e:
            logger.error(f"Unexpected error in Ollama generation: {e}")
            return prompt

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
            
            # Calculate improvement metrics
            readability_improvement = rewritten_scores["flesch_reading_ease"] - original_scores["flesch_reading_ease"]
            grade_improvement = original_scores["flesch_kincaid_grade"] - rewritten_scores["flesch_kincaid_grade"]
            
            logger.info(f"Rewriting complete. New length: {len(final_text)} characters. "
                       f"Readability improvement: {readability_improvement:.1f} points")
            
            return {
                "success": True,
                "original_text": content,
                "rewritten_text": final_text,
                "mode": mode,
                "scores": {
                    "original": original_scores,
                    "rewritten": rewritten_scores
                },
                "improvements": {
                    "readability_change": round(readability_improvement, 2),
                    "grade_level_change": round(grade_improvement, 2),
                    "length_change": len(final_text) - len(content),
                    "improved": readability_improvement > 0
                },
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

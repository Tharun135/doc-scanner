"""
Enhanced Document Rewriter with Smart Analysis
This rewriter analyzes content structure and applies targeted improvements
"""

import re
import logging
from typing import Dict, List, Tuple
import requests
import json

logger = logging.getLogger(__name__)

class SmartDocumentRewriter:
    def __init__(self, config=None):
        """Initialize with enhanced rewriting capabilities"""
        self.config = config or {}
        self.api_url = "http://localhost:11434/api/generate"
        self.model = "phi3:mini"
        
    def analyze_document_structure(self, text: str) -> Dict:
        """Analyze document to understand its structure and complexity"""
        
        # Split into sentences for analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        analysis = {
            'sentence_count': len(sentences),
            'avg_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
            'complex_sentences': [],
            'technical_terms': [],
            'passive_voice': [],
            'long_paragraphs': [],
            'improvement_areas': []
        }
        
        # Identify complex sentences (>25 words)
        for i, sentence in enumerate(sentences):
            words = sentence.split()
            if len(words) > 25:
                analysis['complex_sentences'].append({
                    'sentence': sentence,
                    'word_count': len(words),
                    'index': i
                })
        
        # Identify technical jargon
        technical_patterns = [
            r'\b\w+tion\b', r'\b\w+ment\b', r'\b\w+ness\b',  # Nominalizations
            r'\b(implementation|methodology|functionality|configuration)\b',  # Common technical terms
            r'\b\w{12,}\b'  # Very long words
        ]
        
        for pattern in technical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            analysis['technical_terms'].extend(matches)
        
        # Identify passive voice patterns
        passive_patterns = [
            r'\b(is|are|was|were|been|being)\s+\w+ed\b',
            r'\bwill be\s+\w+ed\b'
        ]
        
        for sentence in sentences:
            for pattern in passive_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    analysis['passive_voice'].append(sentence)
                    break
        
        # Determine improvement priorities
        if analysis['avg_sentence_length'] > 20:
            analysis['improvement_areas'].append('sentence_length')
        if len(analysis['technical_terms']) > 10:
            analysis['improvement_areas'].append('technical_simplification')
        if len(analysis['passive_voice']) > len(sentences) * 0.3:
            analysis['improvement_areas'].append('active_voice')
        
        return analysis
    
    def create_targeted_prompt(self, text: str, analysis: Dict, mode: str) -> str:
        """Create a specific prompt based on document analysis"""
        
        base_prompts = {
            'clarity': "Rewrite this text to be crystal clear and easy to understand.",
            'simplicity': "Rewrite this text using simple, everyday language.",
            'technical': "Rewrite this technical content for a general audience."
        }
        
        # Build targeted instructions based on analysis
        instructions = [base_prompts.get(mode, base_prompts['clarity'])]
        
        if 'sentence_length' in analysis['improvement_areas']:
            instructions.append("Break long sentences into shorter ones (under 20 words each).")
        
        if 'technical_simplification' in analysis['improvement_areas']:
            instructions.append("Replace technical jargon with simple, everyday words.")
            instructions.append("Explain technical concepts in plain language.")
        
        if 'active_voice' in analysis['improvement_areas']:
            instructions.append("Use active voice instead of passive voice.")
            instructions.append("Make it clear who is doing what.")
        
        # Add specific examples for better results
        examples = """
Example transformations:
- "The implementation of the system was conducted" → "We set up the system"
- "Configuration of the parameters should be performed" → "Set up the parameters" 
- "It is recommended that users ensure" → "Users should make sure"
"""
        
        full_prompt = f"""
{' '.join(instructions)}

{examples}

Original text:
{text}

Rewritten text:"""
        
        return full_prompt
    
    def rewrite_in_chunks(self, text: str, analysis: Dict, mode: str) -> str:
        """Rewrite large documents in strategic chunks for better results"""
        
        # Split into logical chunks (paragraphs or sentence groups)
        if len(text) < 500:
            # Small text - rewrite as one piece
            return self._ollama_rewrite(text, analysis, mode)
        
        # Large text - split into paragraphs
        paragraphs = text.split('\n\n')
        if len(paragraphs) == 1:
            # No paragraph breaks - split by sentences
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() + '.' for s in sentences if s.strip()]
            
            # Group sentences into chunks of 3-4
            chunks = []
            for i in range(0, len(sentences), 3):
                chunk = ' '.join(sentences[i:i+3])
                chunks.append(chunk)
        else:
            chunks = paragraphs
        
        # Rewrite each chunk
        rewritten_chunks = []
        for chunk in chunks:
            if chunk.strip():
                rewritten = self._ollama_rewrite(chunk.strip(), analysis, mode)
                rewritten_chunks.append(rewritten)
        
        return '\n\n'.join(rewritten_chunks)
    
    def _ollama_rewrite(self, text: str, analysis: Dict, mode: str) -> str:
        """Call Ollama with targeted prompt"""
        
        prompt = self.create_targeted_prompt(text, analysis, mode)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower for more consistent results
                "top_p": 0.9,
                "num_predict": min(len(text) * 2, 500),
                "num_ctx": 4096,  # Larger context for better understanding
                "repeat_penalty": 1.1
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=45)
            response.raise_for_status()
            
            result = response.json()
            rewritten = result.get("response", "").strip()
            
            # Fallback if no response
            if not rewritten or rewritten.lower() == text.lower():
                logger.warning("AI returned empty or identical text, using fallback")
                return self._simple_fallback_rewrite(text)
            
            return rewritten
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return self._simple_fallback_rewrite(text)
    
    def _simple_fallback_rewrite(self, text: str) -> str:
        """Simple rule-based rewriting as fallback"""
        
        # Basic transformations when AI fails
        rewritten = text
        
        # Replace common complex phrases
        replacements = {
            "implementation of": "setting up",
            "methodology": "method",
            "functionality": "features",
            "configuration": "setup",
            "utilization": "use",
            "optimization": "improvement",
            "in order to": "to",
            "due to the fact that": "because",
            "it is recommended that": "you should"
        }
        
        for old, new in replacements.items():
            rewritten = re.sub(old, new, rewritten, flags=re.IGNORECASE)
        
        return rewritten
    
    def smart_rewrite_document(self, content: str, mode: str = "clarity") -> Dict:
        """Main method - analyzes and rewrites document strategically"""
        
        if not content or not content.strip():
            return {
                "success": False,
                "error": "No content provided"
            }
        
        try:
            # Step 1: Analyze document structure
            logger.info("Analyzing document structure...")
            analysis = self.analyze_document_structure(content)
            
            logger.info(f"Analysis: {len(analysis['complex_sentences'])} complex sentences, "
                       f"{len(analysis['technical_terms'])} technical terms, "
                       f"avg sentence length: {analysis['avg_sentence_length']:.1f} words")
            
            # Step 2: Strategic rewriting based on analysis
            logger.info("Performing strategic rewrite...")
            rewritten_text = self.rewrite_in_chunks(content, analysis, mode)
            
            # Step 3: Validate results
            if rewritten_text.strip() == content.strip():
                logger.warning("Rewrite produced identical text - using enhanced fallback")
                rewritten_text = self._simple_fallback_rewrite(content)
            
            return {
                "success": True,
                "original_text": content,
                "rewritten_text": rewritten_text,
                "analysis": analysis,
                "strategy_used": "smart_analysis"
            }
            
        except Exception as e:
            logger.error(f"Smart rewrite failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_text": content,
                "rewritten_text": content
            }

def get_smart_rewriter():
    """Factory function to create smart rewriter"""
    return SmartDocumentRewriter()

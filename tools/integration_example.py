"""
integration_example.py

Example of how to integrate the style guide retrieval system 
into your existing DocScanner writing improvement pipeline.

This shows how to use the whitelist-based knowledge base as a fallback
when your custom rules fail, providing authoritative writing standards.
"""

import logging
from style_guide_retriever import StyleGuideRetriever
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedWritingPipeline:
    """
    Enhanced writing improvement pipeline with style guide fallback.
    
    Pipeline priority:
    1. Custom rules (your existing logic)
    2. Style guide retrieval (authoritative sources) 
    3. Smart fallback (your existing fallback)
    """
    
    def __init__(self):
        self.style_retriever = StyleGuideRetriever()
        self.confidence_threshold = 0.75  # Threshold for using custom rules
        self.similarity_threshold = 0.4   # Threshold for style guide relevance
    
    def improve_sentence(self, sentence: str, context: str = "") -> Dict[str, Any]:
        """
        Main improvement pipeline with style guide integration.
        
        Args:
            sentence: The sentence to improve
            context: Additional context about the writing domain
            
        Returns:
            Dict containing improved sentence, strategy used, and sources
        """
        
        # Step 1: Try custom rules first (your existing logic)
        custom_result = self.apply_custom_rules(sentence)
        
        if custom_result and custom_result.get('confidence', 0) >= self.confidence_threshold:
            logger.info(f"Applied custom rule: {custom_result['rule_name']}")
            return {
                'original': sentence,
                'improved': custom_result['improved'],
                'strategy': 'custom_rules',
                'rule_name': custom_result['rule_name'],
                'confidence': custom_result['confidence'],
                'sources': ['custom']
            }
        
        # Step 2: Try style guide retrieval (whitelist sources)
        style_guidance = self.get_style_guidance(sentence, context)
        
        if style_guidance:
            logger.info(f"Using style guide fallback with {len(style_guidance)} sources")
            return self.apply_style_guidance(sentence, style_guidance)
        
        # Step 3: Fall back to your existing smart fallback
        logger.info("Using smart fallback - no authoritative guidance found")
        return self.smart_fallback(sentence)
    
    def get_style_guidance(self, sentence: str, context: str = "") -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve relevant style guidance for the sentence.
        
        Args:
            sentence: The sentence to get guidance for
            context: Additional context for better retrieval
            
        Returns:
            List of relevant guidance items or None if insufficient matches
        """
        
        # Build search queries based on sentence analysis
        queries = self.analyze_sentence_for_queries(sentence, context)
        
        all_guidance = []
        for query in queries:
            guidance = self.style_retriever.get_guidance(
                query=query,
                max_results=4,
                min_similarity=self.similarity_threshold
            )
            all_guidance.extend(guidance)
        
        # Deduplicate and filter by relevance
        seen_ids = set()
        unique_guidance = []
        for item in all_guidance:
            if item['id'] not in seen_ids and item['similarity'] >= self.similarity_threshold:
                unique_guidance.append(item)
                seen_ids.add(item['id'])
        
        # Sort by similarity and return top items
        unique_guidance.sort(key=lambda x: x['similarity'], reverse=True)
        
        return unique_guidance[:6] if unique_guidance else None
    
    def analyze_sentence_for_queries(self, sentence: str, context: str = "") -> List[str]:
        """
        Analyze the sentence to generate relevant search queries for style guides.
        
        Args:
            sentence: The sentence to analyze
            context: Additional context
            
        Returns:
            List of search queries to try
        """
        queries = []
        sentence_lower = sentence.lower()
        
        # Detect common writing issues and map to queries
        if 'was ' in sentence_lower or 'were ' in sentence_lower or 'been ' in sentence_lower:
            queries.append('active voice passive voice')
        
        if any(word in sentence_lower for word in ['click', 'button', 'menu', 'dialog']):
            queries.append('UI elements capitalization')
            queries.append('user interface text')
        
        if any(word in sentence_lower for word in ['procedure', 'step', 'instruction', 'how to']):
            queries.append('writing procedures instructions')
        
        if any(word in sentence_lower for word in ['he', 'she', 'guys', 'blacklist', 'whitelist']):
            queries.append('inclusive language guidelines')
        
        if sentence.isupper() or any(c.isupper() for c in sentence.split()[1:]):
            queries.append('capitalization guidelines')
        
        # Always include general writing guidance
        queries.append('clear writing principles')
        queries.append('concise sentences')
        
        # Add context-specific queries
        if context:
            queries.append(f'{context} writing style')
        
        return list(set(queries))  # Remove duplicates
    
    def apply_style_guidance(self, sentence: str, guidance_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Apply style guidance to improve the sentence using LLM with authoritative context.
        
        Args:
            sentence: Original sentence
            guidance_items: Relevant style guidance
            
        Returns:
            Improvement result with authoritative sources
        """
        
        # Build authoritative prompt
        prompt = self.style_retriever.build_authoritative_prompt(
            sentence=sentence, 
            guidance_items=guidance_items,
            max_context_items=4
        )
        
        if not prompt:
            return None
        
        # Here you would call your LLM with the authoritative prompt
        # For this example, I'll simulate the LLM response
        llm_response = self.call_llm_with_guidance(prompt)
        
        if llm_response and llm_response.get('rewrite'):
            sources_used = [item['metadata']['source'] for item in guidance_items[:3]]
            return {
                'original': sentence,
                'improved': llm_response['rewrite'],
                'strategy': 'style_guide_fallback',
                'rationale': llm_response.get('rationale', ''),
                'sources': sources_used,
                'guidance_used': len(guidance_items),
                'confidence': 0.8  # High confidence due to authoritative sources
            }
        
        return None
    
    def call_llm_with_guidance(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Call your LLM with the authoritative prompt.
        This is where you'd integrate with your existing LLM setup.
        
        Args:
            prompt: The prompt with style guide context
            
        Returns:
            LLM response with rewrite and rationale
        """
        
        # PLACEHOLDER: Replace with your actual LLM integration
        # This could be OpenAI, Anthropic, local models, etc.
        
        logger.info("🤖 Calling LLM with authoritative style guide context...")
        
        # Simulate LLM response for demo
        return {
            'rewrite': 'Improved sentence based on style guidelines...',
            'rationale': 'Applied Google Style Guide recommendations for clarity and conciseness',
            'sources_used': ['google']
        }
    
    def apply_custom_rules(self, sentence: str) -> Optional[Dict[str, Any]]:
        """
        Apply your existing custom rules.
        This is where your current rule-based logic would go.
        
        Args:
            sentence: Sentence to check
            
        Returns:
            Custom rule result or None
        """
        
        # PLACEHOLDER: Your existing custom rules logic
        # Return None to trigger style guide fallback
        return None
    
    def smart_fallback(self, sentence: str) -> Dict[str, Any]:
        """
        Your existing smart fallback when no authoritative sources are found.
        
        Args:
            sentence: Original sentence
            
        Returns:
            Fallback improvement result
        """
        
        # PLACEHOLDER: Your existing smart fallback logic
        return {
            'original': sentence,
            'improved': sentence,  # No change
            'strategy': 'smart_fallback',
            'confidence': 0.5,
            'sources': ['fallback']
        }

# Example usage and testing
def demo_integration():
    """Demonstrate the integrated pipeline."""
    
    pipeline = ImprovedWritingPipeline()
    
    test_sentences = [
        "Click on the Submit button to save your changes.",
        "The file was processed by the system successfully.", 
        "To configure the settings, you should navigate to the Settings menu and then click on Advanced Options.",
        "Use the whitelist to allow trusted sources.",
        "THIS BUTTON WILL DELETE ALL YOUR DATA.",
    ]
    
    print("🚀 Testing Improved Writing Pipeline with Style Guide Integration\n")
    
    for i, sentence in enumerate(test_sentences, 1):
        print(f"Test {i}: {sentence}")
        print("-" * 60)
        
        result = pipeline.improve_sentence(sentence, context="user_interface")
        
        print(f"Strategy: {result['strategy']}")
        print(f"Original: {result['original']}")
        print(f"Improved: {result['improved']}")
        print(f"Sources: {', '.join(result['sources'])}")
        
        if 'rationale' in result:
            print(f"Rationale: {result['rationale']}")
        
        print(f"Confidence: {result.get('confidence', 'N/A')}")
        print()

if __name__ == "__main__":
    demo_integration()

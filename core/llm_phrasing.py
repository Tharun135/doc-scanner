"""
LLM Phrasing Module

The LLM's role here is BRUTALLY narrow:
> You are not deciding what to do.
> The review decision is already made.
> Your task is to phrase the suggestion clearly for a first-time user.

That's it. phi3:mini performs fine in this constrained role.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LLMPhraser:
    """
    Uses LLM ONLY for phrasing pre-determined guidance.
    
    The LLM does NOT:
    - Decide what issue exists
    - Decide how to fix it
    - Invent structure
    - Add creativity
    
    The LLM ONLY:
    - Adapts template to specific content
    - Ensures natural language flow
    - Maintains consistent tone
    """
    
    def __init__(self, model_name: str = "phi3:mini"):
        self.model_name = model_name
        self.llm_available = self._check_llm_availability()
    
    def _check_llm_availability(self) -> bool:
        """Check if LLM is available."""
        try:
            from scripts.ollama_client import OllamaClient
            client = OllamaClient()
            return client.is_available()
        except Exception as e:
            logger.warning(f"LLM not available: {e}")
            return False
    
    def phrase_resolution(
        self,
        template: str,
        context: Dict[str, Any],
        fallback: str
    ) -> str:
        """
        Use LLM to adapt template to specific content.
        
        If LLM fails or produces low-quality output:
        → Return fallback immediately
        
        Args:
            template: Pre-written template with placeholders
            context: Specific content to adapt to
            fallback: Deterministic text to return if LLM fails
        
        Returns:
            Phrased guidance (or fallback)
        """
        if not self.llm_available:
            return fallback
        
        try:
            # Create narrow prompt
            prompt = self._create_narrow_prompt(template, context)
            
            # Get LLM response
            response = self._call_llm(prompt)
            
            # Validate response adds value
            if not response or len(response.strip()) < 20:
                logger.warning("LLM response too short, using fallback")
                return fallback
            
            # Check for hedge words without concrete action
            if self._is_too_vague(response):
                logger.warning("LLM response too vague, using fallback")
                return fallback
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error phrasing with LLM: {e}")
            return fallback
    
    def _create_narrow_prompt(self, template: str, context: Dict[str, Any]) -> str:
        """
        Create extremely narrow prompt for LLM.
        
        The LLM is told:
        - CODE already decided what's wrong and how to fix it
        - LLM ONLY phrases it clearly with an example
        - LLM does NOT change the solution or constraints
        """
        sentence = context.get('sentence', '')
        feedback = context.get('feedback', '')
        
        prompt = f"""You are a technical writing assistant. CODE already decided what to fix. You only decide how to say it.

CODE DECIDED (YOU CANNOT CHANGE):
✓ What the issue is: {feedback}
✓ What kind of solution is needed
✓ What constraints apply

YOUR ONLY JOB:
✓ Phrase the solution clearly
✓ Provide a concrete example showing before/after
✓ Make it sound human and helpful

SOLUTION TEMPLATE (from code):
{template}

SENTENCE TO IMPROVE:
{sentence}

OUTPUT REQUIRED (3 parts):
1. What needs to change (1 sentence, direct)
2. Example showing the transformation (before → after)
3. Why this improves clarity (1 sentence)

Be direct. Use "→" to show transformations. No hedging, no "consider", no "you could".
"""
        return prompt
    
    def _call_llm(self, prompt: str, max_tokens: int = 150) -> str:
        """Call LLM with timeout and error handling."""
        try:
            from scripts.ollama_client import OllamaClient
            client = OllamaClient()
            
            response = client.generate(
                model=self.model_name,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.3,  # Low temperature for consistency
                timeout=10  # 10 second timeout
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return ""
    
    def _is_too_vague(self, text: str) -> bool:
        """
        Check if LLM output is too vague to be useful.
        
        Vague output:
        - Uses "consider", "might", "possibly" without concrete action
        - Repeats the problem without helping
        - Lacks specific next steps
        """
        text_lower = text.lower()
        
        # Hedge words without action
        hedge_words = ['consider', 'might', 'possibly', 'perhaps', 'maybe', 'could']
        action_words = ['rewrite to', 'replace with', 'change to', 'use', 'add', 'remove']
        
        has_hedge = any(word in text_lower for word in hedge_words)
        has_action = any(word in text_lower for word in action_words)
        
        # If it only hedges, it's too vague
        if has_hedge and not has_action:
            return True
        
        # Check for explanatory phrases without guidance
        explanation_only = [
            'this means', 'this is because', 'the issue is',
            'the problem is', 'you should know'
        ]
        
        if any(phrase in text_lower for phrase in explanation_only):
            if not has_action:
                return True
        
        return False
    
    def phrase_rewrite(
        self,
        original: str,
        issue_type: str,
        fallback_rewrite: str
    ) -> str:
        """
        Generate a rewrite using LLM, with fallback.
        
        The LLM is told:
        - The type of change needed (already decided)
        - The original sentence
        - That it should ONLY perform the change, not explain
        
        Args:
            original: Original sentence
            issue_type: Type of change needed (passive_voice, vague_term, etc.)
            fallback_rewrite: Deterministic rewrite to use if LLM fails
        
        Returns:
            Rewritten sentence (or fallback)
        """
        if not self.llm_available:
            return fallback_rewrite
        
        try:
            prompt = self._create_rewrite_prompt(original, issue_type)
            response = self._call_llm(prompt, max_tokens=100)
            
            # Validate rewrite is different enough
            if not response or len(response.strip()) < 5:
                return fallback_rewrite
            
            # Check it's actually different
            from core.issue_resolution_engine import calculate_similarity
            similarity = calculate_similarity(original, response)
            
            if similarity > 0.8:
                logger.warning("LLM rewrite too similar to original, using fallback")
                return fallback_rewrite
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating rewrite: {e}")
            return fallback_rewrite
    
    def _create_rewrite_prompt(self, original: str, issue_type: str) -> str:
        """Create narrow prompt for rewriting."""
        
        instructions = {
            'passive_voice': 'Rewrite in active voice. Show who performs the action. Keep system-focused perspective.',
            'long_sentence': 'Split into 2-3 shorter sentences. Each conveys one clear idea. Maintain logical flow.',
            'vague_term': 'Replace vague terms with specific ones. Use concrete numbers where possible.',
            'dense_step': 'Split into separate steps. Format: Action → Expected result.',
        }
        
        instruction = instructions.get(issue_type, 'Improve clarity and directness.')
        
        prompt = f"""CODE decided what to fix: {issue_type}
YOU decide how to phrase it.

CONSTRAINTS (from code):
{instruction}

ORIGINAL:
{original}

RULES:
- Apply the transformation exactly as specified
- Keep technical accuracy
- Return ONLY the rewritten sentence
- No explanations, no alternatives

REWRITTEN:"""
        
        return prompt


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_phraser_instance = None


def get_llm_phraser() -> LLMPhraser:
    """Get singleton LLM phraser instance."""
    global _phraser_instance
    if _phraser_instance is None:
        _phraser_instance = LLMPhraser()
    return _phraser_instance


def phrase_with_llm(
    template: str,
    context: Dict[str, Any],
    fallback: str
) -> str:
    """
    Convenience function to phrase guidance with LLM.
    Always returns useful text (fallback if LLM fails).
    """
    phraser = get_llm_phraser()
    return phraser.phrase_resolution(template, context, fallback)


def rewrite_with_llm(
    original: str,
    issue_type: str,
    fallback_rewrite: str
) -> str:
    """
    Convenience function to generate rewrite with LLM.
    Always returns valid rewrite (fallback if LLM fails).
    """
    phraser = get_llm_phraser()
    return phraser.phrase_rewrite(original, issue_type, fallback_rewrite)

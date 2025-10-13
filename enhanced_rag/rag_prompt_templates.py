# enhanced_rag/rag_prompt_templates.py
"""
Enhanced RAG prompt templates with strict source attribution and fallback handling.
Implements the constrained prompting approach to prevent hallucinations.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
from .rule_specific_corrections import get_rule_specific_correction, EnhancedRulePrompts

@dataclass
class RAGContext:
    """Structured context for RAG prompting"""
    chunk_id: str
    text: str
    metadata: Dict[str, Any]
    score: float
    source_label: str


class EnhancedRAGPrompts:
    """Enhanced prompt templates with strict source attribution"""
    
    @staticmethod
    def build_constrained_prompt(
        flagged_sentence: str,
        rule_id: str,
        retrieved_chunks: List[RAGContext],
        max_chunks: int = 3
    ) -> str:
        """
        Build constrained prompt that forces LLM to use only retrieved context.
        
        Args:
            flagged_sentence: The problematic sentence
            rule_id: ID of the writing rule that was violated
            retrieved_chunks: Retrieved context chunks with metadata
            max_chunks: Maximum chunks to include in prompt
        
        Returns:
            Formatted prompt string
        """
        # Limit chunks to avoid overwhelming the LLM
        chunks_to_use = retrieved_chunks[:max_chunks]
        
        # Build context section with clear labels
        context_sections = []
        for i, chunk in enumerate(chunks_to_use, 1):
            metadata = chunk.metadata
            source_info = f"(product: {metadata.get('product', 'unknown')}) " \
                         f"(file: {metadata.get('source_doc_id', 'unknown')}) " \
                         f"(section: {metadata.get('section_title', 'unknown')})"
            
            context_sections.append(f"[{i}] {source_info}\n\"{chunk.text}\"")
        
        context_text = "\n\n".join(context_sections) if context_sections else "No relevant guidance found."
        
        # Build the constrained prompt
        prompt = f"""You are a technical writing assistant. A user flagged this sentence for [rule: {rule_id}]:
"{flagged_sentence}"

Relevant context (labelled):
{context_text}

Task:
1) Based only on the "Relevant context" above, propose a corrected sentence or steps to fix the issue.
2) Provide a one-line reason referencing which chunk (by label) you used.
3) If context doesn't contain guidance, reply exactly: "No guidance found in the retrieved documents."

Answer:
- Correction:
- Reason:
- Source:"""

        return prompt
    
    @staticmethod
    def build_explanation_prompt(
        flagged_sentence: str,
        rule_id: str,
        retrieved_chunks: List[RAGContext]
    ) -> str:
        """
        Build prompt for explaining why a sentence violates a rule.
        
        Args:
            flagged_sentence: The problematic sentence
            rule_id: ID of the writing rule that was violated
            retrieved_chunks: Retrieved context chunks
        
        Returns:
            Formatted explanation prompt
        """
        context_text = ""
        if retrieved_chunks:
            context_text = f"\n\nRelevant writing guidance:\n{retrieved_chunks[0].text[:300]}..."
        
        prompt = f"""Explain why this sentence violates the {rule_id} rule:
"{flagged_sentence}"{context_text}

Provide a brief, clear explanation:"""

        return prompt
    
    @staticmethod
    def build_confidence_prompt(
        original_sentence: str,
        proposed_correction: str,
        rule_id: str
    ) -> str:
        """Build prompt to assess confidence in a correction"""
        prompt = f"""Rate the quality of this writing correction on a scale of 1-5:

Original: "{original_sentence}"
Corrected: "{proposed_correction}"
Rule: {rule_id}

Consider:
- Does the correction fix the rule violation?
- Is the meaning preserved?
- Is the correction grammatically correct?

Rating (1-5):"""

        return prompt
    
    @staticmethod
    def build_alternative_suggestions_prompt(
        flagged_sentence: str,
        rule_id: str,
        retrieved_chunks: List[RAGContext]
    ) -> str:
        """Build prompt to generate multiple alternative corrections"""
        context_text = ""
        if retrieved_chunks:
            best_chunk = retrieved_chunks[0]
            context_text = f"\n\nGuidance: {best_chunk.text[:200]}..."
        
        prompt = f"""Provide 3 different ways to fix this {rule_id} issue:
"{flagged_sentence}"{context_text}

Option 1:
Option 2:
Option 3:"""

        return prompt
    
    @staticmethod
    def parse_llm_response(response: str) -> Dict[str, str]:
        """
        Parse structured LLM response from constrained prompt.
        
        Args:
            response: Raw LLM response text
        
        Returns:
            Parsed response with correction, reason, and source
        """
        # Initialize result
        result = {
            "correction": "",
            "reason": "",
            "source": "",
            "has_guidance": True
        }
        
        # Check for "no guidance" response
        if "No guidance found in the retrieved documents" in response:
            result["has_guidance"] = False
            result["correction"] = "No specific guidance available"
            return result
        
        # Parse structured response
        lines = response.strip().split('\n')
        current_field = None
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('- Correction:'):
                current_field = 'correction'
                result['correction'] = line.replace('- Correction:', '').strip()
            elif line.startswith('- Reason:'):
                current_field = 'reason'
                result['reason'] = line.replace('- Reason:', '').strip()
            elif line.startswith('- Source:'):
                current_field = 'source'
                result['source'] = line.replace('- Source:', '').strip()
            elif current_field and line:
                # Continue multi-line field
                result[current_field] += " " + line
        
        # Clean up empty fields
        for key in result:
            if isinstance(result[key], str):
                result[key] = result[key].strip()
        
        return result
    
    @staticmethod
    def build_fallback_prompt(
        flagged_sentence: str,
        rule_id: str
    ) -> str:
        """Build simple fallback prompt when no relevant context is found"""
        rule_guidance = {
            "passive-voice": "Convert passive voice to active voice by identifying the subject and making it perform the action.",
            "adverb-usage": "Remove unnecessary adverbs that don't add meaningful information.",
            "click-on": "Replace 'click on' with 'click' or 'select' for more direct instructions.",
            "modal-verbs": "Replace modal verbs (can, may, should) with direct imperative language.",
            "all-caps": "Replace ALL CAPS text with regular case or proper emphasis.",
            "filler-words": "Remove filler words like 'just', 'really', 'very' for clearer writing."
        }
        
        guidance = rule_guidance.get(rule_id, "Improve clarity and directness of the sentence.")
        
        prompt = f"""Fix this {rule_id} issue in the sentence:
"{flagged_sentence}"

Guidance: {guidance}

Corrected sentence:"""

        return prompt


class RAGResponseFormatter:
    """Format RAG responses for consistent output"""
    
    @staticmethod
    def format_suggestion(
        original_sentence: str,
        correction: str,
        explanation: str,
        confidence: str,
        sources: List[Dict[str, Any]],
        method: str = "rag_enhanced"
    ) -> Dict[str, Any]:
        """
        Format a complete RAG suggestion response.
        
        Args:
            original_sentence: Original problematic sentence
            correction: Proposed correction
            explanation: Explanation of the issue
            confidence: Confidence level (high/medium/low)
            sources: List of source chunks used
            method: Method used (rag_enhanced, fallback, etc.)
        
        Returns:
            Formatted suggestion dictionary
        """
        return {
            "original_sentence": original_sentence,
            "suggested_correction": correction,
            "explanation": explanation,
            "confidence": confidence,
            "method": method,
            "sources": sources,
            "timestamp": json.dumps({"generated_at": "now"}),  # Placeholder
            "version": "2.0"
        }
    
    @staticmethod
    def format_sources(retrieved_chunks: List[RAGContext]) -> List[Dict[str, Any]]:
        """Format source information for response"""
        sources = []
        
        for chunk in retrieved_chunks:
            metadata = chunk.metadata
            sources.append({
                "chunk_id": chunk.chunk_id,
                "source_doc": metadata.get('source_doc_id', 'unknown'),
                "section": metadata.get('section_title', 'unknown'),
                "product": metadata.get('product', 'unknown'),
                "version": metadata.get('version', 'unknown'),
                "score": chunk.score,
                "text_preview": chunk.text[:100] + "..." if len(chunk.text) > 100 else chunk.text
            })
        
        return sources
    
    @staticmethod
    def create_confidence_level(
        score: float,
        has_exact_match: bool,
        source_count: int
    ) -> str:
        """
        Calculate confidence level based on retrieval quality.
        
        Args:
            score: Best retrieval score
            has_exact_match: Whether query had exact text matches
            source_count: Number of relevant sources found
        
        Returns:
            Confidence level string
        """
        if score > 0.8 and source_count >= 2:
            return "high"
        elif score > 0.6 or has_exact_match:
            return "medium"
        elif score > 0.3 and source_count >= 1:
            return "low"
        else:
            return "very_low"


# Quick prompt testing utilities
def test_prompt_templates():
    """Test the prompt templates with sample data"""
    print("Testing RAG Prompt Templates")
    print("=" * 50)
    
    # Sample data
    sample_chunks = [
        RAGContext(
            chunk_id="rule_001",
            text="Passive voice makes writing unclear. Use active voice instead. Example: 'The system processes data' instead of 'Data is processed by the system'.",
            metadata={
                "product": "docscanner",
                "source_doc_id": "writing_rules.md",
                "section_title": "Voice Guidelines"
            },
            score=0.92,
            source_label="[1]"
        ),
        RAGContext(
            chunk_id="rule_002", 
            text="Technical writing should be direct and clear. Avoid passive constructions when possible.",
            metadata={
                "product": "docscanner",
                "source_doc_id": "style_guide.md", 
                "section_title": "Clarity Rules"
            },
            score=0.85,
            source_label="[2]"
        )
    ]
    
    # Test constrained prompt
    prompt = EnhancedRAGPrompts.build_constrained_prompt(
        flagged_sentence="The file was created by the system",
        rule_id="passive-voice",
        retrieved_chunks=sample_chunks
    )
    
    print("Constrained Prompt:")
    print(prompt)
    print("\n" + "=" * 50)
    
    # Test response parsing
    sample_response = """- Correction: The system created the file
- Reason: Used guidance from chunk [1] to convert passive to active voice
- Source: Chunk [1] - Voice Guidelines"""
    
    parsed = EnhancedRAGPrompts.parse_llm_response(sample_response)
    print("Parsed Response:")
    for key, value in parsed.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    test_prompt_templates()

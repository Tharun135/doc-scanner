#!/usr/bin/env python3
"""
Test the improved LLM prompts for adverb issues
"""

import sys
import os
sys.path.insert(0, '.')

# Test the prompt generation without actually calling LLM
def test_improved_prompts():
    """Test the improved prompt templates"""
    
    # Simulate the exact case from the user
    feedback_text = "Check use of adverb: 'only' in sentence 'In the IEM, you only get a very general overview about the CPU load of an app.'"
    sentence_context = "In the IEM, you only get a very general overview about the CPU load of an app."
    document_type = "technical"
    writing_goals = ["clarity", "conciseness"]
    
    print("🧠 Testing Improved LLM Prompts for Adverb Issues")
    print("="*60)
    
    # Test the basic Ollama prompt
    basic_prompt = f"""You are an expert technical writing assistant. Rewrite sentences to fix specific issues.

ISSUE DETECTED: {feedback_text}
ORIGINAL SENTENCE: "{sentence_context}"
DOCUMENT TYPE: {document_type}
WRITING GOALS: {', '.join(writing_goals)}

TASK: Provide a complete rewritten sentence that fixes the specific issue identified.

GUIDELINES:
- For adverb placement issues: Move the adverb closer to the word it modifies
- For passive voice: Convert to active voice showing who performs the action  
- For long sentences: Break into shorter, clearer sentences
- Preserve original meaning while improving clarity
- Use "Application" instead of "technical writer"

FORMAT:
IMPROVED_SENTENCE: [Complete rewritten sentence]
EXPLANATION: [What you changed and why]

Rewrite the sentence now:"""

    print("\n📝 BASIC OLLAMA PROMPT:")
    print(basic_prompt)
    
    # Test the RAG-enhanced prompt
    context_documents = [
        "Place limiting words like 'only' directly before the word or phrase they modify for clarity.",
        "Adverb placement affects meaning: 'You only get basic access' vs 'You get only basic access'"
    ]
    
    context_section = "\nRELEVANT CONTEXT from uploaded documents:\n"
    for i, doc in enumerate(context_documents, 1):
        context_section += f"Context {i}: {doc}\n"
    context_section += "\nUse this context to inform your suggestions.\n"
    
    rag_prompt = f"""You are an expert technical writing assistant. Your task is to rewrite sentences to fix specific writing issues.

ISSUE DETECTED: {feedback_text}
ORIGINAL SENTENCE: "{sentence_context}"
DOCUMENT TYPE: {document_type}
WRITING GOALS: {', '.join(writing_goals)}
{context_section}

INSTRUCTIONS:
1. You must provide a complete rewritten sentence that fixes the specific issue
2. For adverb issues (like "only"), reposition the adverb to clarify meaning
3. For passive voice, convert to active voice
4. For long sentences, break into shorter, clearer sentences
5. Preserve the original meaning while improving clarity
6. Use "Application" instead of "technical writer" in your suggestions

REQUIRED FORMAT:
IMPROVED_SENTENCE: [Complete rewritten sentence that fixes the issue]
EXPLANATION: [Brief explanation of what you changed and why it's better]

EXAMPLE FOR ADVERB ISSUES:
- If original: "You only get basic access"
- Consider: "You get only basic access" (if limiting access type) OR "Only you get basic access" (if limiting who gets access)
- Choose based on the intended meaning in context

Now rewrite the sentence above:"""

    print("\n\n📚 RAG-ENHANCED OLLAMA PROMPT:")
    print(rag_prompt)
    
    print("\n\n🎯 EXPECTED OUTPUT FROM LLM:")
    print("IMPROVED_SENTENCE: In the IEM, you get only a very general overview about the CPU load of an app.")
    print("EXPLANATION: Moved 'only' closer to 'a very general overview' to clarify that it limits the type of overview provided, not the action of getting it.")
    
    print("\n✅ The improved prompts now:")
    print("1. Clearly ask for a COMPLETE REWRITTEN SENTENCE")
    print("2. Provide specific guidance for adverb placement issues")
    print("3. Include examples of how to handle 'only' positioning")
    print("4. Require structured output format")
    print("5. Focus on fixing the issue rather than just analyzing it")

if __name__ == "__main__":
    test_improved_prompts()
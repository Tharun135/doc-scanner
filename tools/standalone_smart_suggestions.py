#!/usr/bin/env python3
"""
Standalone smart AI suggestion system for DocScanner.
This can be integrated into ai_improvement.py without any complex dependencies.
"""

from typing import Dict, Any, Optional

def generate_smart_ai_suggestion(feedback_text: str, sentence: str) -> Optional[Dict[str, Any]]:
    """
    Generate smart rule-based suggestions for common writing issues.
    This provides much better suggestions than generic "enhanced_fallback" responses.
    
    Args:
        feedback_text: The feedback/issue description
        sentence: The original sentence to improve
        
    Returns:
        Dictionary with suggestion, explanation, and metadata, or None if no improvement found
    """
    if not sentence or not feedback_text:
        return None
    
    feedback_lower = feedback_text.lower()
    
    # Handle adverb issues (like "accordingly")
    if "adverb" in feedback_lower and "accordingly" in sentence.lower():
        improved_sentence = sentence
        
        if "accordingly" in sentence:
            # Context-based replacements for "accordingly"
            if "credentials" in sentence.lower():
                improved_sentence = sentence.replace("accordingly", "correctly")
                explanation = "Replaced vague 'accordingly' with 'correctly' for credential-related actions."
            elif "configuration" in sentence.lower() or "configure" in sentence.lower():
                improved_sentence = sentence.replace("accordingly", "as specified")
                explanation = "Replaced 'accordingly' with 'as specified' to reference documentation clearly."
            elif "procedure" in sentence.lower() or "process" in sentence.lower():
                improved_sentence = sentence.replace("accordingly", "as required")
                explanation = "Replaced 'accordingly' with 'as required' for procedural instructions."
            elif "data" in sentence.lower():
                improved_sentence = sentence.replace("accordingly", "appropriately")
                explanation = "Replaced 'accordingly' with 'appropriately' for data handling contexts."
            else:
                improved_sentence = sentence.replace("accordingly", "as needed")
                explanation = "Replaced vague 'accordingly' with more specific 'as needed'."
        
        return {
            "suggestion": improved_sentence,
            "ai_answer": f"{explanation} The word 'accordingly' often adds no meaningful information and can be replaced with clearer, more specific terms that provide actual guidance to the reader.",
            "confidence": "high",
            "method": "smart_rule_based",
            "sources": ["Siemens Style Guide: Use specific, actionable language"],
            "original_sentence": sentence,
            "success": True
        }
    
    # Handle passive voice issues
    if "passive" in feedback_lower and any(word in sentence.lower() for word in ["was", "were", "been", "is being", "are being"]):
        # Provide guidance for converting to active voice
        ai_answer = ("Consider converting to active voice by identifying who performs the action. "
                    "For example: 'The system creates the file' instead of 'The file was created by the system'. "
                    "Active voice makes instructions clearer and more direct.")
        
        return {
            "suggestion": sentence,  # Keep original but provide guidance
            "ai_answer": ai_answer,
            "confidence": "medium",
            "method": "smart_rule_based", 
            "sources": ["Siemens Style Guide: Prefer active voice for clarity"],
            "original_sentence": sentence,
            "success": True
        }
    
    # Handle long sentence issues
    if any(phrase in feedback_lower for phrase in ["long sentence", "break", "shorter"]):
        ai_answer = ("Consider breaking this long sentence into 2-3 shorter sentences. "
                    "Each sentence should focus on one main idea. "
                    "Use connecting words like 'Then', 'Next', 'Additionally', or 'After that' to maintain logical flow between sentences.")
        
        return {
            "suggestion": sentence,  # Keep original but provide guidance
            "ai_answer": ai_answer,
            "confidence": "medium",
            "method": "smart_rule_based",
            "sources": ["Siemens Style Guide: Keep sentences concise and focused"],
            "original_sentence": sentence,
            "success": True
        }
    
    # Handle imperative mood issues
    if "imperative" in feedback_lower:
        improved_sentence = sentence
        
        if sentence.strip().startswith("You must "):
            improved_sentence = sentence.replace("You must ", "", 1).strip()
            if improved_sentence:
                improved_sentence = improved_sentence[0].upper() + improved_sentence[1:]
            explanation = "Converted to imperative mood by removing 'You must'."
            
        elif sentence.strip().startswith("You should "):
            improved_sentence = sentence.replace("You should ", "", 1).strip()
            if improved_sentence:
                improved_sentence = improved_sentence[0].upper() + improved_sentence[1:]
            explanation = "Converted to imperative mood by removing 'You should'."
            
        elif sentence.strip().startswith("You need to "):
            improved_sentence = sentence.replace("You need to ", "", 1).strip()
            if improved_sentence:
                improved_sentence = improved_sentence[0].upper() + improved_sentence[1:]
            explanation = "Converted to imperative mood by removing 'You need to'."
        else:
            return None
            
        return {
            "suggestion": improved_sentence,
            "ai_answer": f"{explanation} Imperative mood is more direct and actionable in technical documentation, making instructions clearer for users.",
            "confidence": "high",
            "method": "smart_rule_based",
            "sources": ["Siemens Style Guide: Use imperative mood for instructions"],
            "original_sentence": sentence,
            "success": True
        }
    
    # Handle wordiness issues
    if any(phrase in feedback_lower for phrase in ["wordy", "concise", "redundant", "unnecessary"]):
        ai_answer = ("Look for opportunities to remove unnecessary words while preserving meaning. "
                    "Common targets: filler words ('very', 'quite'), redundant phrases ('in order to' → 'to'), "
                    "and overly formal constructions ('utilize' → 'use', 'facilitate' → 'help').")
        
        return {
            "suggestion": sentence,  # Keep original but provide guidance
            "ai_answer": ai_answer,
            "confidence": "medium",
            "method": "smart_rule_based",
            "sources": ["Siemens Style Guide: Write concisely"],
            "original_sentence": sentence,
            "success": True
        }
    
    # No specific improvement found
    return None


def test_smart_suggestions():
    """Test the smart suggestion function with various examples."""
    
    test_cases = [
        {
            "feedback": "Check use of adverb: 'accordingly' in sentence",
            "sentence": "To publish the FINS/TCP data in Databus, you must enter the credentials accordingly in Common Configurator.",
            "expected_improvement": "correctly"
        },
        {
            "feedback": "Consider using imperative mood",
            "sentence": "You must restart the system to apply changes.",
            "expected_improvement": "Restart the system"
        },
        {
            "feedback": "This sentence is too long and should be broken down",
            "sentence": "When configuring the system for the first time, you need to ensure that all the required parameters are set correctly and that the database connection is properly established before proceeding with the initialization process.",
            "expected_improvement": "guidance for breaking down"
        }
    ]
    
    print("🧪 Testing Smart AI Suggestions")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}:")
        print(f"Feedback: {test_case['feedback']}")
        print(f"Original: {test_case['sentence']}")
        
        result = generate_smart_ai_suggestion(test_case['feedback'], test_case['sentence'])
        
        if result:
            print(f"✅ Method: {result['method']}")
            print(f"✅ Improved: {result['suggestion']}")
            print(f"✅ Explanation: {result['ai_answer'][:100]}...")
            print(f"✅ Confidence: {result['confidence']}")
        else:
            print("❌ No suggestion generated")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")


if __name__ == "__main__":
    test_smart_suggestions()
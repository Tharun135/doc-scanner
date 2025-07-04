#!/usr/bin/env python3
"""
Script to analyze the specific modal verb issue and debug the AI response structure problem.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import get_enhanced_ai_suggestion
import logging
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_modal_verb_issue():
    """Test the specific modal verb issue that's causing problems."""
    
    feedback_text = "Use of modal verb 'can' - should describe direct action"
    sentence_context = ""  # We might not have the sentence context
    document_type = "general"
    writing_goals = ['clarity', 'conciseness']
    
    print("=== TESTING MODAL VERB ISSUE ===")
    print(f"Feedback: {feedback_text}")
    print(f"Sentence: '{sentence_context}'")
    print(f"Document type: {document_type}")
    print(f"Writing goals: {writing_goals}")
    print()
    
    try:
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type=document_type,
            writing_goals=writing_goals
        )
        
        print("=== AI SUGGESTION RESULT ===")
        print(f"Type: {type(result)}")
        print(f"Keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")
        print(f"Full result: {json.dumps(result, indent=2)}")
        print()
        
        # Validate structure
        print("=== VALIDATION CHECKS ===")
        print(f"Is dict: {isinstance(result, dict)}")
        print(f"Has 'suggestion' key: {'suggestion' in result}")
        if 'suggestion' in result:
            print(f"Suggestion type: {type(result['suggestion'])}")
            print(f"Suggestion value: '{result['suggestion']}'")
            print(f"Suggestion is truthy: {bool(result['suggestion'])}")
            print(f"Suggestion length: {len(str(result['suggestion']))}")
        
        # Check for empty or None values
        if result.get('suggestion') is None:
            print("❌ PROBLEM: Suggestion is None")
        elif result.get('suggestion') == "":
            print("❌ PROBLEM: Suggestion is empty string")
        elif not result.get('suggestion'):
            print("❌ PROBLEM: Suggestion is falsy")
        else:
            print("✅ Suggestion appears valid")
            
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_with_sample_sentence():
    """Test with a sample sentence containing 'can'."""
    
    feedback_text = "Use of modal verb 'can' - should describe direct action"
    sentence_context = "Users can access their data through the dashboard."
    document_type = "technical"
    writing_goals = ['clarity', 'directness']
    
    print("\n=== TESTING WITH SAMPLE SENTENCE ===")
    print(f"Feedback: {feedback_text}")
    print(f"Sentence: '{sentence_context}'")
    print(f"Document type: {document_type}")
    print(f"Writing goals: {writing_goals}")
    print()
    
    try:
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type=document_type,
            writing_goals=writing_goals
        )
        
        print("=== AI SUGGESTION RESULT ===")
        print(f"Full result: {json.dumps(result, indent=2)}")
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_ai_availability():
    """Test if AI model is available."""
    print("=== TESTING AI AVAILABILITY ===")
    
    try:
        import ollama
        models = ollama.list()
        print(f"Ollama models available: {[model.model for model in models.models] if models and models.models else 'None'}")
        
        if models and models.models:
            # Test a simple AI call
            test_model = models.models[0].model
            print(f"Testing with model: {test_model}")
            
            response = ollama.chat(
                model=test_model,
                messages=[
                    {
                        'role': 'user',
                        'content': 'Say "AI is working" briefly.'
                    }
                ],
                options={'max_tokens': 20}
            )
            
            print(f"Test response: {response['message']['content']}")
            print("✅ AI is working")
            
        else:
            print("❌ No Ollama models available")
            
    except Exception as e:
        print(f"❌ AI Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting analysis of modal verb issue...\n")
    
    # Test AI availability first
    test_ai_availability()
    print()
    
    # Test the specific issue
    result1 = test_modal_verb_issue()
    
    # Test with sample sentence
    result2 = test_with_sample_sentence()
    
    print("\n=== SUMMARY ===")
    if result1 and result1.get('suggestion'):
        print("✅ Test 1 (no context): PASSED")
    else:
        print("❌ Test 1 (no context): FAILED")
        
    if result2 and result2.get('suggestion'):
        print("✅ Test 2 (with context): PASSED") 
    else:
        print("❌ Test 2 (with context): FAILED")

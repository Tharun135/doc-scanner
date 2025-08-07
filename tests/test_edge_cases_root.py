#!/usr/bin/env python3
"""
Test edge cases that might cause invalid response structure
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from ai_improvement import get_enhanced_ai_suggestion
    
    def test_edge_cases():
        """Test edge cases that might cause invalid response structure."""
        
        print("🔍 Testing Edge Cases for AI Suggestion")
        print("=" * 50)
        
        edge_cases = [
            {
                "feedback": "",  # Empty feedback
                "sentence": "Test sentence.",
                "name": "Empty Feedback"
            },
            {
                "feedback": "   ",  # Whitespace-only feedback
                "sentence": "Test sentence.",
                "name": "Whitespace Feedback"
            },
            {
                "feedback": "Test feedback",
                "sentence": "",  # Empty sentence
                "name": "Empty Sentence"
            },
            {
                "feedback": "Test feedback",
                "sentence": "   ",  # Whitespace-only sentence
                "name": "Whitespace Sentence"
            },
            {
                "feedback": None,  # None feedback
                "sentence": "Test sentence.",
                "name": "None Feedback"
            },
            {
                "feedback": "Unknown issue type: xyz123",
                "sentence": "",
                "name": "Unknown Issue Type"
            }
        ]
        
        for i, test_case in enumerate(edge_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case['name']}")
            print(f"Feedback: '{test_case['feedback']}'")
            print(f"Sentence: '{test_case['sentence']}'")
            print("-" * 30)
            
            try:
                result = get_enhanced_ai_suggestion(
                    feedback_text=test_case['feedback'],
                    sentence_context=test_case['sentence'],
                    document_type="technical",
                    writing_goals=['clarity']
                )
                
                if isinstance(result, dict) and 'suggestion' in result and result['suggestion'] and result['suggestion'].strip():
                    print("✅ VALID: Response structure is correct")
                    print(f"  Method: {result.get('method', 'N/A')}")
                    print(f"  Confidence: {result.get('confidence', 'N/A')}")
                    print(f"  Suggestion length: {len(result['suggestion'])}")
                else:
                    print("❌ INVALID: Response structure failed validation")
                    print(f"  Result type: {type(result)}")
                    print(f"  Result: {result}")
                    
            except Exception as e:
                print(f"❌ EXCEPTION: {e}")

    if __name__ == "__main__":
        test_edge_cases()
        
except Exception as e:
    print(f"❌ Import Error: {e}")
    import traceback
    traceback.print_exc()

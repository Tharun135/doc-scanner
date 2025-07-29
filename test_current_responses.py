"""
Direct test of Gemini integration with enhanced prompts for specific solutions.
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_current_responses():
    """Test current system responses."""
    print("🔍 Testing Current Gemini Responses...")
    print("=" * 50)
    
    try:
        from app.ai_improvement import get_enhanced_ai_suggestion
        
        test_cases = [
            {
                "name": "Passive Voice",
                "feedback": "Passive voice detected",
                "sentence": "The document was written by the team"
            },
            {
                "name": "Modal Verb Issue",
                "feedback": "Modal verb usage: 'may' for permission",
                "sentence": "You may use this feature when needed"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📝 Test: {test_case['name']}")
            print(f"Issue: {test_case['feedback']}")
            print(f"Sentence: '{test_case['sentence']}'")
            print("-" * 40)
            
            result = get_enhanced_ai_suggestion(
                feedback_text=test_case['feedback'],
                sentence_context=test_case['sentence']
            )
            
            print(f"Method: {result.get('method', 'unknown')}")
            print(f"Suggestion: {result.get('suggestion', 'No suggestion')}")
            print(f"Gemini Answer: {result.get('gemini_answer', 'No answer')}")
            
            if result.get('method') == 'gemini_rag':
                print("✅ Using Gemini AI")
            else:
                print("⚠️ Using fallback")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_current_responses()

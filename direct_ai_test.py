#!/usr/bin/env python3
"""
Direct test of AI suggestion function to identify response structure issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from app.intelligent_ai_improvement import IntelligentAISuggestionEngine, get_enhanced_ai_suggestion

def test_direct_ai_suggestion():
    """Test AI suggestion function directly without server"""
    print("🔧 Testing AI suggestion function directly...")
    
    # Test data
    test_data = {
        "feedback": "Avoid using ALL CAPS for emphasis. Use bold or italic formatting instead.",
        "sentence": "Some of the properties of alarm notifications are specifically implemented for the SIMATIC S7+ Connector.",
        "document_type": "technical",
        "writing_goals": ["clarity", "conciseness"],
        "option_number": 1
    }
    
    print("\nRequest data:")
    print(json.dumps(test_data, indent=2))
    
    try:
        # Call the standalone AI suggestion function directly
        result = get_enhanced_ai_suggestion(
            feedback_text=test_data["feedback"],
            sentence_context=test_data["sentence"],
            document_type=test_data["document_type"],
            writing_goals=test_data["writing_goals"],
            option_number=test_data["option_number"]
        )
        
        print(f"\n✅ Function call successful!")
        print(f"📝 Result type: {type(result)}")
        print(f"📝 Result: {result}")
        
        # Check if result is a valid response structure
        if isinstance(result, dict):
            print(f"\n🔍 Analyzing response structure:")
            print(f"   - Has 'suggestion' key: {'suggestion' in result}")
            if 'suggestion' in result:
                suggestion = result['suggestion']
                print(f"   - Suggestion type: {type(suggestion)}")
                print(f"   - Suggestion value: {repr(suggestion)}")
                print(f"   - Suggestion truthy: {bool(suggestion)}")
                if hasattr(suggestion, 'strip'):
                    print(f"   - Suggestion after strip(): {repr(suggestion.strip())}")
                    print(f"   - Suggestion strip() truthy: {bool(suggestion.strip())}")
            
            for key, value in result.items():
                print(f"   - {key}: {type(value)} = {repr(value)}")
        else:
            print(f"⚠️  Result is not a dictionary: {repr(result)}")
        
        # Test JavaScript validation logic
        if isinstance(result, dict) and result.get('suggestion'):
            suggestion = result['suggestion']
            if hasattr(suggestion, 'strip') and suggestion.strip():
                print("\n✅ Would pass JavaScript validation: result.suggestion && result.suggestion.trim()")
            else:
                print(f"\n❌ Would fail JavaScript validation: suggestion = {repr(suggestion)}")
        else:
            print(f"\n❌ Would fail JavaScript validation: no suggestion key or falsy suggestion")
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_direct_ai_suggestion()
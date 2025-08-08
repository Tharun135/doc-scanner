#!/usr/bin/env python3
"""
Test the improved AI suggestion system for "above" reference issues.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_above_reference_fix():
    """Test the AI suggestion system with the user's specific 'above' reference case."""
    
    try:
        from app.ai_improvement import ai_engine
        
        # Your exact case
        feedback_text = "Avoid using 'above' to refer to previous content; use specific references."
        sentence_context = "Common Configurator creates a JSON configuration file that is identical to the second configuration mentioned above."
        
        print("🧪 TESTING ABOVE REFERENCE FIX")
        print("=" * 60)
        print(f"📝 Feedback: {feedback_text}")
        print(f"📝 Original: {sentence_context}")
        print()
        
        result = ai_engine.generate_contextual_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type="technical"
        )
        
        print("🎯 AI SUGGESTION RESULT:")
        print("-" * 40)
        print(f"Suggestion: {result['suggestion']}")
        print(f"Confidence: {result.get('confidence', 'N/A')}")
        print(f"Method: {result.get('method', 'N/A')}")
        
        # Check if the suggestion actually provides improved alternatives
        suggestion_text = result['suggestion']
        
        if suggestion_text and sentence_context not in suggestion_text:
            print("\n✅ SUCCESS: AI provided actual improvements instead of echoing original!")
        elif "OPTION 1:" in suggestion_text and "OPTION 2:" in suggestion_text:
            print("\n✅ SUCCESS: AI provided multiple improvement options!")
        elif sentence_context in suggestion_text:
            print("\n❌ ISSUE: AI is still echoing the original sentence")
            print("   The fix may need further refinement")
        else:
            print("\n⚠️  UNCLEAR: AI response format may need review")
        
        print("\n📊 DETAILED ANALYSIS:")
        if "mentioned in" in suggestion_text or "described in" in suggestion_text or "second configuration" in suggestion_text:
            print("✅ Contains specific reference improvements")
        else:
            print("❌ Missing specific reference improvements") 
            
        if "OPTION" in suggestion_text:
            print("✅ Provides multiple alternatives")
        else:
            print("❌ No multiple alternatives provided")
        
    except Exception as e:
        print(f"❌ Error running test: {e}")
        import traceback
        traceback.print_exc()

def test_additional_above_cases():
    """Test other common 'above' reference patterns."""
    
    test_cases = [
        {
            "feedback": "Avoid using 'above' to refer to previous content; use specific references.",
            "sentence": "The settings described above should be configured carefully.",
            "expected_improvement": True
        },
        {
            "feedback": "Avoid using 'above' to refer to previous content; use specific references.",
            "sentence": "Follow the procedure shown above to complete the installation.",
            "expected_improvement": True
        },
        {
            "feedback": "Avoid using 'above' to refer to previous content; use specific references.",
            "sentence": "Use the above method for optimal results.",
            "expected_improvement": True
        }
    ]
    
    print("\n\n🔬 TESTING ADDITIONAL ABOVE REFERENCE CASES")
    print("=" * 60)
    
    try:
        from app.ai_improvement import ai_engine
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case['sentence']}")
            
            result = ai_engine.generate_contextual_suggestion(
                feedback_text=test_case['feedback'],
                sentence_context=test_case['sentence'],
                document_type="technical"
            )
            
            suggestion = result['suggestion']
            
            # Check if actual improvements were provided
            if test_case['sentence'] not in suggestion and any(word in suggestion.lower() for word in ['section', 'step', 'figure', 'procedure', 'method', 'earlier', 'previous']):
                print(f"    ✅ GOOD: Provided specific alternatives")
            elif "OPTION" in suggestion and len(suggestion.split("OPTION")) > 2:
                print(f"    ✅ GOOD: Multiple options provided")
            else:
                print(f"    ❌ ISSUE: May need improvement")
                print(f"    Result: {suggestion[:100]}...")
                
    except Exception as e:
        print(f"❌ Error in additional tests: {e}")

if __name__ == "__main__":
    test_above_reference_fix()
    test_additional_above_cases()

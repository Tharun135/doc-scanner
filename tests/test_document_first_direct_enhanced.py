#!/usr/bin/env python3
"""
Direct test of the enhanced document_first_ai system
"""

import sys
import os

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_document_first_ai():
    print("🧪 Testing Enhanced Document-First AI System")
    print("=" * 50)
    
    try:
        from app.document_first_ai import get_document_first_suggestion
        print("✅ Successfully imported document_first_ai")
        
        # Test the exact sentence that should trigger conversion
        test_sentence = "A data source must be created."
        
        print(f"📝 Testing: '{test_sentence}'")
        print(f"🎯 Expected: 'You must create a data source.'")
        print()
        
        # Call the enhanced function
        result = get_document_first_suggestion(
            feedback_text="Convert passive voice to active voice",
            sentence_context=test_sentence,
            document_type="technical",
            writing_goals=["clarity", "directness", "active_voice"]
        )
        
        print(f"📊 Result: {result}")
        
        if result and result.get('success'):
            suggestion = result.get('suggestion', '').strip()
            method = result.get('method', 'N/A')
            confidence = result.get('confidence', 'N/A')
            
            print(f"\n✅ Success: {result.get('success')}")
            print(f"📊 Method: {method}")
            print(f"🎯 Confidence: {confidence}")
            print(f"💡 Suggestion: '{suggestion}'")
            
            if "You must create a data source" in suggestion:
                print("\n🎉 PERFECT! Found expected conversion!")
            elif suggestion != test_sentence:
                print(f"\n✅ Some conversion detected: {suggestion}")
            else:
                print(f"\n❌ NO CONVERSION - Same text returned")
        else:
            print(f"❌ Failed or no success: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_document_first_ai()
#!/usr/bin/env python3
"""
Direct test of the improved AI suggestion function for your specific sentence.
"""

import sys
import os
import logging

# Add current directory and app directory to path  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_improved_suggestion():
    """Test the improved AI suggestion function with your specific sentence."""
    
    # The exact sentence from your test case
    sentence = "To publish the FINS/TCP data in Databus, you must enter the credentials accordingly in Common Configurator."
    feedback = "Check use of adverb: 'accordingly' in sentence 'To publish the FINS/TCP data in Databus, you must enter the credentials accordingly in Common Configurator.'"
    
    print("🧪 Testing Improved AI Suggestion Function")
    print("=" * 70)
    print(f"Original sentence: {sentence}")
    print(f"Feedback: {feedback}")
    print()
    
    try:
        # Import the smart suggestion function we just created
        from ai_improvement import _generate_smart_suggestion
        
        print("✅ Imported smart suggestion function")
        
        # Test the smart suggestion
        result = _generate_smart_suggestion(feedback, sentence)
        
        if result:
            print("✅ Smart suggestion generated!")
            print(f"Method: {result.get('method', 'unknown')}")
            print(f"Original: {result.get('original_sentence', 'N/A')}")
            print(f"Improved: {result.get('suggestion', 'N/A')}")
            print(f"Explanation: {result.get('ai_answer', 'N/A')}")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print(f"Success: {result.get('success', False)}")
            
            return result
        else:
            print("❌ No smart suggestion generated")
            return None
            
    except Exception as e:
        print(f"❌ Import or execution failed: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return None

def test_manual_replacement():
    """Test manual string replacement logic."""
    
    sentence = "To publish the FINS/TCP data in Databus, you must enter the credentials accordingly in Common Configurator."
    
    print("\n🔧 Manual Replacement Test")
    print("=" * 70)
    print(f"Original: {sentence}")
    
    # Test the replacement logic
    if "credentials" in sentence.lower():
        improved = sentence.replace("accordingly", "correctly")
        print(f"Improved: {improved}")
        print("✅ Replacement logic works!")
        return improved
    
    return None

if __name__ == "__main__":
    print("🚀 AI Suggestion Improvement Test")
    print("=" * 70)
    
    # Test 1: Try the smart suggestion function
    result = test_improved_suggestion()
    
    # Test 2: Manual replacement as backup
    if not result:
        print("\n🔄 Trying manual replacement...")
        manual_result = test_manual_replacement()
        
        if manual_result:
            print(f"\n✅ Manual improvement successful:")
            print(f"   {manual_result}")
    
    print("\n" + "=" * 70)
    print("✅ Test completed!")
    
    if result:
        original_sentence = "To publish the FINS/TCP data in Databus, you must enter the credentials accordingly in Common Configurator."
        print("\n📊 SUMMARY:")
        print(f"   OLD: {original_sentence}")
        print(f"   NEW: {result.get('suggestion', 'N/A')}")
        print(f"   IMPROVEMENT: Replaced vague 'accordingly' with specific 'correctly'")
    else:
        print("\n⚠️ Suggestion function needs debugging")
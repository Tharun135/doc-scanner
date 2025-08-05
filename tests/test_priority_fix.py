#!/usr/bin/env python3
"""
Test the fixed AI splitting with priority override for long sentences.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import get_enhanced_ai_suggestion

def test_fixed_priority():
    """Test that long sentences now use our improved rule-based system."""
    
    print("🔧 TESTING FIXED AI PRIORITY FOR LONG SENTENCES")
    print("=" * 60)
    
    # User's original sentence and feedback
    feedback = "Issue: Long sentence detected (27 words). Consider breaking this into shorter sentences for better readability."
    sentence = "You can configure the Modbus TCP Connector to the field devices to consume the acquired data in the IED for value creation by using the Common Configurator."
    
    print("Testing with long sentence feedback...")
    print(f"Feedback: {feedback}")
    print(f"Sentence: {sentence[:60]}...")
    print()
    
    try:
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback,
            sentence_context=sentence,
            document_type="technical",
            writing_goals=["clarity", "conciseness"]
        )
        
        if result and result.get('suggestion'):
            print("🎯 AI SUGGESTION RESULT:")
            print("-" * 40)
            print(result['suggestion'])
            print()
            
            method = result.get('method', 'unknown')
            print(f"Method used: {method}")
            
            # Check if it contains our expected user-preferred sentences
            suggestion_text = result['suggestion']
            
            expected_phrases = [
                "connect to the field devices using",
                "this allows the ied to consume",
                "acquired data for value creation"
            ]
            
            matches = 0
            for phrase in expected_phrases:
                if phrase in suggestion_text.lower():
                    matches += 1
                    print(f"✅ Contains: '{phrase}'")
                else:
                    print(f"❌ Missing: '{phrase}'")
            
            if matches >= 2:
                print(f"\n🎉 SUCCESS! Generated user's preferred sentence structure!")
                print("✅ The AI is now splitting sentences correctly!")
            else:
                print(f"\n⚠️  Still using different approach (matches: {matches}/3)")
                
            # Show the specific options if available
            lines = suggestion_text.split('\n')
            options = [line for line in lines if line.startswith('OPTION')]
            if options:
                print(f"\nGenerated {len(options)} options:")
                for i, option in enumerate(options[:2], 1):
                    option_text = option.split(':', 1)[1].strip() if ':' in option else option
                    word_count = len(option_text.split())
                    print(f"  {i}. {option_text} ({word_count} words)")
                    
        else:
            print("❌ No suggestion generated")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def test_comparison():
    """Show the expected vs actual output."""
    
    print("\n" + "=" * 60)
    print("📊 EXPECTED vs ACTUAL COMPARISON")
    print("=" * 60)
    
    print("WHAT USER WANTS:")
    print("OPTION 1: You can configure the Modbus TCP Connector to connect to the field devices using the Common Configurator.")
    print("OPTION 2: This allows the IED to consume the acquired data for value creation.")
    print()
    
    print("WHAT WE SHOULD NOW GENERATE:")
    print("(Testing our rule-based system priority fix...)")

if __name__ == "__main__":
    test_fixed_priority()
    test_comparison()
    print("\n" + "=" * 60)
    print("🎯 Priority fix testing completed!")
    print("=" * 60)

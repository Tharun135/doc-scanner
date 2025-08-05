#!/usr/bin/env python3
"""
Test the new formatting with various sentence types.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import get_enhanced_ai_suggestion

def test_various_sentences():
    """Test with different types of long sentences."""
    
    print("🔧 TESTING MULTIPLE SENTENCE TYPES")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "User's Tag Retention Example",
            "feedback": "Issue: Long sentence detected (27 words). Consider breaking this into shorter sentences for better readability.",
            "sentence": "Tag retention eliminates the need for repetitive tag selection, as the system automatically remembers and applies your previous choices, resulting in time and effort savings and a more streamlined workflow."
        },
        {
            "name": "Technical Configuration Example",
            "feedback": "Issue: Long sentence detected (24 words). Consider breaking this into shorter sentences.",
            "sentence": "You can configure the Modbus TCP Connector to the field devices to consume the acquired data in the IED for value creation by using the Common Configurator."
        },
        {
            "name": "Generic Long Sentence",
            "feedback": "Issue: Long sentence detected (22 words). Consider breaking this into shorter sentences.",
            "sentence": "The application provides comprehensive data analysis capabilities and generates detailed reports that help users make informed business decisions."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 40)
        print(f"Sentence: {test_case['sentence'][:60]}...")
        
        try:
            result = get_enhanced_ai_suggestion(
                feedback_text=test_case['feedback'],
                sentence_context=test_case['sentence'],
                document_type="technical",
                writing_goals=["clarity", "conciseness"]
            )
            
            if result and result.get('suggestion'):
                print("\nAI Suggestion:")
                print(result['suggestion'])
                
                # Check formatting
                suggestion_text = result['suggestion']
                if "OPTION 1 has sentence 1:" in suggestion_text and "sentence 2:" in suggestion_text:
                    print("✅ Format: Correct")
                else:
                    print("❌ Format: Incorrect")
                    
            else:
                print("❌ No suggestion generated")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_various_sentences()
    print("\n" + "=" * 60)
    print("🎯 Multiple sentence type testing completed!")
    print("=" * 60)

#!/usr/bin/env python3
"""
Test various passive voice patterns to ensure comprehensive coverage.
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from ai_improvement import GeminiAISuggestionEngine

def test_multiple_passive_patterns():
    """Test various passive voice patterns."""
    
    ai_engine = GeminiAISuggestionEngine()
    
    test_cases = [
        {
            "feedback": "Convert to active voice: 'The Docker daemon does not generate logs when no applications are running.'",
            "sentence": "Docker logs are not generated when there are no active applications.",
            "expected_pattern": "Docker daemon does not generate"
        },
        {
            "feedback": "Passive voice detected: 'are displayed' - convert to active voice for clearer communication.",
            "sentence": "The configuration options are displayed.",
            "expected_pattern": "system displays"
        },
        {
            "feedback": "Convert to active voice for better readability.",
            "sentence": "Changes were made to the document.",
            "expected_pattern": "team made changes"
        },
        {
            "feedback": "Use active voice instead of passive voice.",
            "sentence": "The report was written by John.",
            "expected_pattern": "John wrote"
        }
    ]
    
    print("🔍 Testing Multiple Passive Voice Patterns")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}:")
        print(f"Feedback: {test_case['feedback']}")
        print(f"Original: {test_case['sentence']}")
        print("-" * 40)
        
        result = ai_engine.generate_minimal_fallback(test_case['feedback'], test_case['sentence'])
        
        suggestion = result.get('suggestion', '')
        print(f"AI Suggestion:")
        print(suggestion)
        
        # Check if the expected pattern appears in any of the options
        if test_case['expected_pattern'].lower() in suggestion.lower():
            print(f"✅ SUCCESS: Found expected pattern '{test_case['expected_pattern']}'")
        else:
            print(f"❌ MISSING: Expected pattern '{test_case['expected_pattern']}' not found")
        
        # Check if original sentence still appears (should not)
        if test_case['sentence'] in suggestion:
            print(f"❌ ISSUE: Original sentence still appears in suggestion")
        else:
            print(f"✅ GOOD: Original sentence properly converted")
    
    print(f"\n🎯 Summary: Testing completed for {len(test_cases)} passive voice patterns")

if __name__ == "__main__":
    test_multiple_passive_patterns()

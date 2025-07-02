#!/usr/bin/env python3
"""
Debug which rule is generating the confusing feedback
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.app import load_rules, analyze_sentence

def test_specific_sentence():
    """Test the specific sentence that's causing issues"""
    
    # The exact sentence from the user's example
    sentence = "Modbus TCP tags are made available in the Databus after you have selected the corresponding option for selected tags."
    
    print("🔍 Testing Sentence Rule Analysis")
    print("=" * 60)
    print(f"Sentence: {sentence}")
    print()
    
    # Load rules
    rules = load_rules()
    print(f"Loaded {len(rules)} rules")
    
    # Analyze sentence
    feedback, readability_scores, quality_score = analyze_sentence(sentence, rules)
    
    print(f"\nFeedback items found: {len(feedback)}")
    
    for i, item in enumerate(feedback):
        print(f"\n--- Feedback Item {i+1} ---")
        if isinstance(item, dict):
            print(f"Type: dict")
            print(f"Message: {item.get('message', 'N/A')}")
            print(f"Full suggestion: {item.get('full_suggestion', 'N/A')}")
            print(f"Keys: {list(item.keys())}")
        else:
            print(f"Type: {type(item)}")
            print(f"Content: {item}")
    
    print(f"\nReadability scores: {readability_scores}")
    print(f"Quality score: {quality_score}")

if __name__ == "__main__":
    test_specific_sentence()

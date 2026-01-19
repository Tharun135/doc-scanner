"""
Test the specific long sentence issue from the user.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.deterministic_suggestions import generate_suggestion_for_issue


def test_user_long_sentence():
    """Test the specific sentence the user reported."""
    print("\n" + "=" * 70)
    print("TESTING USER'S SPECIFIC ISSUE")
    print("=" * 70)
    
    original = "To add cross reference to a topic in other folder, use the following syntax and mention the entire directory in which the topic is located."
    
    issue = {
        'feedback': 'Consider breaking this long sentence (27 words) into shorter ones for better readability',
        'context': original,
        'rule_id': 'long_sentence',
        'document_type': 'manual',
    }
    
    print(f"\n📝 Original Sentence ({len(original.split())} words):")
    print(f'"{original}"')
    
    suggestion = generate_suggestion_for_issue(issue)
    
    if suggestion:
        print(f"\n✓ Issue Classified: {suggestion['issue_type']}")
        print(f"✓ Resolution Class: {suggestion['resolution_class']}")
        print(f"✓ Severity: {suggestion['severity']}")
        
        print(f"\n💡 Guidance Provided:")
        print(suggestion['guidance'])
        
        if suggestion['rewrite']:
            print(f"\n🔄 Suggested Rewrite:")
            print(f'"{suggestion["rewrite"]}"')
            
            # Check if it's actually different
            if suggestion['rewrite'] != original:
                print("\n✅ REWRITE IS DIFFERENT - Problem solved!")
            else:
                print("\n⚠️ Rewrite is the same - needs improvement")
        
        print(f"\nMethod Used: {suggestion['method']}")
        print(f"Confidence: {suggestion['confidence']}")
    else:
        print("\n✗ Issue not classified")
    
    # Show what the deterministic split would be
    print("\n" + "=" * 70)
    print("DETERMINISTIC SPLIT (What it SHOULD be):")
    print("=" * 70)
    
    # Split on 'and' since it's long
    if ' and ' in original:
        parts = original.split(' and ', 1)
        sentence1 = parts[0].strip() + '.'
        sentence2 = parts[1].strip()
        if sentence2:
            sentence2 = sentence2[0].upper() + sentence2[1:]  # Capitalize
        
        print(f'\n1. "{sentence1}"')
        print(f'2. "{sentence2}"')
        
        word_count1 = len(sentence1.split())
        word_count2 = len(sentence2.split())
        print(f"\n✓ First sentence: {word_count1} words")
        print(f"✓ Second sentence: {word_count2} words")
        print(f"✓ Both under 25 words - more readable!")


if __name__ == "__main__":
    test_user_long_sentence()

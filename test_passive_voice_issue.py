"""
Test the passive voice issue the user reported.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.deterministic_suggestions import generate_suggestion_for_issue


def test_user_passive_voice():
    """Test the specific passive voice sentence the user reported."""
    print("\n" + "=" * 70)
    print("TESTING USER'S PASSIVE VOICE ISSUE")
    print("=" * 70)
    
    original = "The tags details are displayed."
    
    issue = {
        'feedback': 'Avoid passive voice - consider using active voice for clearer, more direct writing',
        'context': original,
        'rule_id': 'passive_voice',
        'document_type': 'manual',
    }
    
    print(f"\n📝 Original Sentence:")
    print(f'"{original}"')
    print("\n⚠️ Issue: Passive voice ('are displayed')")
    
    suggestion = generate_suggestion_for_issue(issue)
    
    if suggestion:
        print(f"\n✓ Issue Classified: {suggestion['issue_type']}")
        print(f"✓ Resolution Class: {suggestion['resolution_class']}")
        print(f"✓ Severity: {suggestion['severity']}")
        
        print(f"\n💡 Guidance Provided:")
        print(suggestion['guidance'])
        
        if suggestion['rewrite']:
            print(f"\n🔄 Deterministic Rewrite:")
            print(f'"{suggestion["rewrite"]}"')
            
            print("\n📊 Analysis:")
            print("  • Maintains system-focused perspective")
            print("  • Converts passive to active")
            print("  • Shows WHO performs the action")
        
        print(f"\nMethod Used: {suggestion['method']}")
        print(f"Confidence: {suggestion['confidence']}")
    else:
        print("\n✗ Issue not classified")
    
    # Show better alternatives
    print("\n" + "=" * 70)
    print("BETTER ALTERNATIVES (System-Focused Active Voice):")
    print("=" * 70)
    
    alternatives = [
        "The system displays the tag details.",
        "The application shows the tag details.",
        "The interface displays the tag details.",
    ]
    
    for i, alt in enumerate(alternatives, 1):
        print(f"\n{i}. \"{alt}\"")
        print(f"   ✓ Active voice")
        print(f"   ✓ System-focused (maintains original perspective)")
        print(f"   ✓ Clear who performs the action")
    
    print("\n" + "=" * 70)
    print("WHY NOT 'You see...'?")
    print("=" * 70)
    print("\n❌ 'You see the tag details' is problematic:")
    print("   • Changes from system action to user perception")
    print("   • Original focuses on what system displays")
    print("   • Technical docs should be system-focused")
    print("\n✅ Better: 'The system displays...'")
    print("   • Active voice")
    print("   • Maintains system focus")
    print("   • Clear causation")


if __name__ == "__main__":
    test_user_passive_voice()

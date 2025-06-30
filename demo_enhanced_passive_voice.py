#!/usr/bin/env python3
"""
Demonstration of the enhanced passive voice AI suggestions.
"""

import app.rules.passive_voice as passive_voice

def demo_enhanced_passive_voice():
    """Demonstrate the enhanced passive voice suggestions."""
    
    print("=== Enhanced Passive Voice AI Suggestions Demo ===\n")
    
    # The user's specific example
    user_example = "The original program for the Rockwell PLC has been exported."
    
    print("USER'S EXAMPLE:")
    print(f"Input: {user_example}")
    print("\n" + "="*60)
    
    suggestions = passive_voice.check(user_example)
    
    if suggestions:
        print("BEFORE (Generic suggestion):")
        print("Issue: Passive voice detected")
        print(f"Original sentence: {user_example}")
        print("AI suggestion: Rewrite in Active Voice: move the action performer to the beginning and make them the subject.")
        
        print("\n" + "-"*60)
        
        print("AFTER (Specific rewrite):")
        print(suggestions[0])
    
    print("\n" + "="*60)
    print("\n✅ IMPROVEMENT SUMMARY:")
    print("• Before: Generic instruction to 'rewrite in active voice'")
    print("• After: Specific rewritten sentence in active voice")
    print("• Users now get actionable, concrete suggestions")
    print("• Consistent with the structured format: Issue/Original sentence/AI suggestion")

if __name__ == "__main__":
    demo_enhanced_passive_voice()

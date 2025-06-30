#!/usr/bin/env python3
"""
Final demonstration of the structured AI suggestion format.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.rules import special_characters, can_may_terms, passive_voice

def demo_final_structure():
    """Demonstrate the final structured format."""
    
    print("=== FINAL DEMO: New AI Suggestion Structure ===\n")
    
    # Sample text with multiple issues
    sample_text = """
    You can download the API's from our website & save them locally. 
    The documentation was written by our team.
    """
    
    print("Sample text:")
    print(f'"{sample_text.strip()}"')
    print("\n" + "="*60 + "\n")
    
    # Check all rules
    all_suggestions = []
    
    # Collect suggestions from different rules
    rules_to_test = [
        ("Special Characters", special_characters),
        ("Modal Verbs", can_may_terms), 
        ("Passive Voice", passive_voice)
    ]
    
    for rule_name, rule_module in rules_to_test:
        suggestions = rule_module.check(sample_text)
        for suggestion in suggestions:
            all_suggestions.append((rule_name, suggestion))
    
    # Display all suggestions with the new structure
    for i, (rule_name, suggestion) in enumerate(all_suggestions, 1):
        print(f"SUGGESTION {i} ({rule_name}):")
        print("-" * 50)
        print(suggestion)
        print("-" * 50 + "\n")
    
    print(f"Total suggestions generated: {len(all_suggestions)}")
    print("\n✅ All suggestions now follow the consistent structure:")
    print("   Issue: [Brief description of the problem]")
    print("   Original sentence: [The sentence that triggered the rule]")
    print("   AI suggestion: [Specific recommendation for improvement]")

if __name__ == "__main__":
    demo_final_structure()

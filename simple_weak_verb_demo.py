#!/usr/bin/env python3
"""
Simple demonstration of improved weak verb detection.
"""

import app.rules.concise_simple_words as csw

def demo():
    print("=== Improved Weak Verb Detection Demo ===\n")
    
    # Examples that should NOT be flagged
    appropriate = [
        "The server is running.",
        "You have two options.",
        "The file is located here."
    ]
    
    # Examples that SHOULD be flagged  
    weak_constructions = [
        "There are three steps.",
        "It is important to save.",
        "You have the ability to edit."
    ]
    
    print("✅ APPROPRIATE (should not be flagged):")
    for text in appropriate:
        suggestions = csw.check(text)
        if suggestions:
            print(f"❌ '{text}' - incorrectly flagged")
        else:
            print(f"✅ '{text}' - correctly allowed")
    
    print("\n❌ WEAK CONSTRUCTIONS (should be flagged):")
    for text in weak_constructions:
        suggestions = csw.check(text)
        if suggestions:
            print(f"✅ '{text}' - correctly flagged")
        else:
            print(f"❌ '{text}' - missed")

if __name__ == "__main__":
    demo()

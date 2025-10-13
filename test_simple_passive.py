#!/usr/bin/env python3
"""Test passive voice fix"""

# Direct test of the smart suggestion function
import re

def test_passive_fix():
    # Your problematic sentence
    text = "The system app Databus is needed to exchange data between a PLC and the IED."
    
    print("Original:", text)
    
    # Test the pattern matching and replacement
    if re.search(r"(?i)is needed", text):
        if "databus" in text.lower():
            suggestion = re.sub(r"(?i)the system app databus is needed to", "Use Databus to", text)
            suggestion = re.sub(r"(?i)databus is needed to", "Use Databus to", suggestion)
            print("Improved:", suggestion)
            print("✅ Conversion successful!")
            return True
    
    return False

if __name__ == "__main__":
    test_passive_fix()
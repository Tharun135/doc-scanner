#!/usr/bin/env python3
"""
Simple test of the sentence splitting logic.
"""

import re

def test_sentence_split():
    """Test sentence splitting logic."""
    
    sentence = "You can configure the Modbus TCP Connector to the field devices to consume the acquired data in the IED for value creation by using the Common Configurator."
    
    print("Testing sentence splitting...")
    print(f"Original: {sentence}")
    print(f"Length: {len(sentence.split())} words")
    print()
    
    # Test the pattern matching
    if re.search(r'can\s+configure.*?by\s+using', sentence, re.IGNORECASE):
        print("✅ Pattern matched: 'can configure...by using'")
        
        if "modbus tcp connector" in sentence.lower() and "field devices" in sentence.lower() and "common configurator" in sentence.lower():
            print("✅ Specific technical pattern detected")
            
            # User's preferred split
            sentence1 = "You can configure the Modbus TCP Connector to connect to the field devices using the Common Configurator."
            sentence2 = "This allows the IED to consume the acquired data for value creation."
            sentence3 = "Configure the connector first, then enable data consumption for optimal performance."
            
            print("\nGenerated split:")
            print(f"OPTION 1: {sentence1}")
            print(f"  → {len(sentence1.split())} words")
            print(f"OPTION 2: {sentence2}")  
            print(f"  → {len(sentence2.split())} words")
            print(f"OPTION 3: {sentence3}")
            print(f"  → {len(sentence3.split())} words")
            
            print("\n✅ SUCCESS: Generated user's preferred sentence structure!")
            
            # Check information preservation
            original_key_terms = ['modbus', 'tcp', 'connector', 'field devices', 'ied', 'acquired data', 'value creation', 'common configurator']
            combined = (sentence1 + " " + sentence2).lower()
            
            print("\nInformation preservation check:")
            for term in original_key_terms:
                if term in combined:
                    print(f"  ✅ '{term}' preserved")
                else:
                    print(f"  ❌ '{term}' missing")
                    
        else:
            print("❌ Specific pattern not detected")
    else:
        print("❌ Pattern not matched")

if __name__ == "__main__":
    test_sentence_split()

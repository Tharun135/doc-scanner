#!/usr/bin/env python3
"""
Debug the passive voice conversion step by step
"""

import sys
import os
import re

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_conversion_logic():
    print("🔍 Debug Passive Voice Conversion Logic")
    print("=" * 50)
    
    # Simulate the relevant documents that would be found
    relevant_docs = [
        {
            "content": '''{"passive": "A data source must be created. ", "active": "You must create a data source."}''',
            "distance": 0.1
        }
    ]
    
    sentence = "A data source must be created."
    
    print(f"📝 Input sentence: '{sentence}'")
    print(f"📚 Relevant docs: {relevant_docs}")
    print()
    
    # Test the conversion logic
    conversion_patterns = []
    
    for doc in relevant_docs:
        content = doc["content"]
        print(f"🔍 Analyzing document: {content}")
        
        # Extract JSON-like examples if present
        if "passive" in content and "active" in content:
            # Try to extract conversion examples
            
            # Look for patterns like: "passive": "X must be Y", "active": "You must Y X"
            passive_active_patterns = re.findall(
                r'"passive":\s*"([^"]*must\s+be[^"]*)".*?"active":\s*"([^"]*)"',
                content, re.IGNORECASE | re.DOTALL
            )
            
            print(f"🎯 Found patterns: {passive_active_patterns}")
            conversion_patterns.extend(passive_active_patterns)
    
    print(f"📊 Total conversion patterns: {len(conversion_patterns)}")
    
    # Apply conversion based on found patterns
    sentence_lower = sentence.lower().strip()
    
    print(f"🔎 Sentence lower: '{sentence_lower}'")
    
    # Specific conversions for "must be created" pattern
    if "must be created" in sentence_lower:
        print("✅ Found 'must be created' pattern!")
        
        # Look for specific pattern in uploaded examples
        for i, (passive_example, active_example) in enumerate(conversion_patterns):
            print(f"  Pattern {i+1}: '{passive_example}' → '{active_example}'")
            
            if "must be created" in passive_example.lower():
                print("  ✅ Found matching 'must be created' pattern!")
                
                # Apply the same conversion pattern
                if "data source" in sentence_lower:
                    result = "You must create a data source."
                    print(f"  🎯 Data source conversion: '{result}'")
                    return result
                else:
                    # Generic conversion
                    subject = sentence.split("must be created")[0].strip()
                    if subject.lower().startswith("a "):
                        subject = subject[2:]  # Remove "a "
                    elif subject.lower().startswith("the "):
                        subject = subject[4:]  # Remove "the "
                    result = f"You must create {subject.lower()}."
                    print(f"  🎯 Generic conversion: '{result}'")
                    return result
        
        print("  ❌ No matching conversion pattern found")
    else:
        print("❌ 'must be created' pattern not found")
    
    # If no specific pattern found, return original
    print("🔄 Returning original sentence")
    return sentence

if __name__ == "__main__":
    result = debug_conversion_logic()
    print(f"\n🎯 Final result: '{result}'")
#!/usr/bin/env python3
"""
Debug conditional detection
"""

def _is_conditional_or_hypothetical(sentence):
    """Check if modal usage is appropriate for conditionals or hypotheticals"""
    import re
    conditional_patterns = [
        r'\bif\b', r'\bunless\b', r'\bsuppose\b', r'\bimagine\b', 
        r'\bhypothetically\b', r'\bpotentially\b', r'\bpossibly\b',
        r'\bwhen\b', r'\bwhether\b'
    ]
    sentence_lower = sentence.lower()
    
    print(f"Checking sentence: '{sentence_lower}'")
    for pattern in conditional_patterns:
        if re.search(pattern, sentence_lower):
            print(f"Found conditional pattern: '{pattern}'")
            return True
    
    print("No conditional patterns found")
    return False

# Test
test_sentence = "You can configure the system and you can also modify the settings."
result = _is_conditional_or_hypothetical(test_sentence)
print(f"Result: {result}")

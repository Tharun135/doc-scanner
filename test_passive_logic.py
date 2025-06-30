#!/usr/bin/env python3
"""
Direct test of passive voice pattern matching and rewriting logic.
"""

import re

def is_passive_voice_pattern(sentence):
    """Additional pattern-based detection for passive voice constructions."""
    passive_patterns = [
        r'\bis\s+\w+ed\b',  # "is needed", "is required"
        r'\bare\s+\w+ed\b',  # "are needed", "are required"
        r'\bwas\s+\w+ed\b', # "was created", "was developed"
        r'\bwere\s+\w+ed\b', # "were created", "were developed"
        r'\bhas\s+been\s+\w+ed\b', # "has been created"
        r'\bhave\s+been\s+\w+ed\b', # "have been created"
        r'\bbeing\s+\w+ed\b', # "being processed"
        r'\bto\s+be\s+\w+ed\b', # "to be processed"
        r'\bit\s+is\s+utilized\b', # "it is utilized"
        r'\bit\s+is\s+used\b', # "it is used"
        r'\bneeds\s+to\s+be\s+\w+ed\b', # "needs to be converted"
        r'\bneed\s+to\s+be\s+\w+ed\b', # "need to be converted"
    ]
    
    for pattern in passive_patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            return True
    return False

def create_active_voice_rewrite_enhanced(original_sentence):
    """Enhanced active voice rewrite with better pattern recognition."""
    
    sentence_lower = original_sentence.lower()
    
    # Pattern 0: "It is utilized when..." -> "Use it when..."
    if re.search(r'it\s+is\s+utilized\s+when', sentence_lower):
        rewrite = re.sub(r'it\s+is\s+utilized\s+when\s+(.+)', 
                       r'Use it when \1', 
                       original_sentence, flags=re.IGNORECASE)
        return rewrite
    
    # Pattern 0b: "It is used when..." -> "Use it when..."
    if re.search(r'it\s+is\s+used\s+when', sentence_lower):
        rewrite = re.sub(r'it\s+is\s+used\s+when\s+(.+)', 
                       r'Use it when \1', 
                       original_sentence, flags=re.IGNORECASE)
        return rewrite
    
    return None

def test_specific_sentence():
    """Test the specific problematic sentence."""
    
    test_sentence = "It is utilized when a provided configuration file needs to be converted to the format used by the"
    
    print("=" * 80)
    print("TESTING PASSIVE VOICE ENHANCEMENT")
    print("=" * 80)
    print(f"Test sentence: {test_sentence}")
    print()
    
    # Step 1: Check if passive voice is detected
    is_passive = is_passive_voice_pattern(test_sentence)
    print(f"1. Passive voice detected: {'✓ YES' if is_passive else '✗ NO'}")
    
    if is_passive:
        # Step 2: Try to rewrite
        rewrite = create_active_voice_rewrite_enhanced(test_sentence)
        
        if rewrite:
            print(f"2. Active voice rewrite: ✓ SUCCESS")
            print(f"   Original: {test_sentence}")
            print(f"   Rewrite:  {rewrite}")
            
            # Step 3: Format as structured suggestion
            suggestion = f"Issue: Passive voice detected\nOriginal sentence: {test_sentence}\nAI suggestion: {rewrite}"
            print(f"\n3. Formatted suggestion:")
            print("-" * 40)
            print(suggestion)
            
        else:
            print(f"2. Active voice rewrite: ✗ FAILED (would use generic advice)")
            suggestion = f"Issue: Passive voice detected\nOriginal sentence: {test_sentence}\nAI suggestion: Consider revising to active voice for clearer, more direct communication."
            print(f"\n3. Fallback suggestion:")
            print("-" * 40)
            print(suggestion)
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    if is_passive:
        rewrite = create_active_voice_rewrite_enhanced(test_sentence)
        if rewrite:
            print("✓ SUCCESS: The enhanced passive voice rule should now provide specific,")
            print("  actionable suggestions instead of generic advice!")
        else:
            print("⚠ PARTIAL: Passive voice detected but no specific rewrite available.")
    else:
        print("✗ ISSUE: Passive voice not detected. Pattern matching needs improvement.")

if __name__ == "__main__":
    test_specific_sentence()

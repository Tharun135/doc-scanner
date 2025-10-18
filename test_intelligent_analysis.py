#!/usr/bin/env python3
"""
Test script to reproduce and fix the 'No test named match' error.
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Test the analyze_sentence function that might be causing the error
try:
    # Import directly from the correct path
    sys.path.insert(0, 'app')
    from app import analyze_sentence, textstat
    
    # Load rules directly
    from rules import grammar_rules, passive_voice, long_sentence, consistency_rules, style_rules, terminology_rules, vague_terms
    
    rules = [
        grammar_rules.check,
        passive_voice.check,
        long_sentence.check,
        consistency_rules.check,
        style_rules.check,
        terminology_rules.check,
        vague_terms.check
    ]
    
    # Test sentence
    test_sentence = "The data can be processed by the system."
    
    print(f"Testing sentence: '{test_sentence}'")
    print("="*50)
    
    # Test textstat functions
    print("Testing textstat functions:")
    print(f"- flesch_reading_ease: {textstat.flesch_reading_ease(test_sentence)}")
    print(f"- gunning_fog: {textstat.gunning_fog(test_sentence)}")
    print(f"- smog_index: {textstat.smog_index(test_sentence)}")
    print(f"- automated_readability_index: {textstat.automated_readability_index(test_sentence)}")
    
    print("\nTesting analyze_sentence function:")
    result = analyze_sentence(test_sentence, rules)
    print(f"Result: {result}")
    
    print("\n✅ Test completed successfully - no 'No test named match' error!")
    
except Exception as e:
    print(f"❌ Error occurred: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
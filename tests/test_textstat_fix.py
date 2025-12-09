#!/usr/bin/env python3
"""
Simple test to check if the textstat issue is fixed.
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Test just the textstat functions that were causing the error
try:
    # Import textstat from app.py (it has the mock)
    import importlib.util
    spec = importlib.util.spec_from_file_location("app", "app/app.py")
    app_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app_module)
    
    textstat = app_module.textstat
    
    # Test sentence
    test_sentence = "The data can be processed by the system."
    
    print(f"Testing sentence: '{test_sentence}'")
    print("="*50)
    
    # Test all textstat functions
    print("Testing textstat functions:")
    try:
        print(f"- flesch_reading_ease: {textstat.flesch_reading_ease(test_sentence)}")
    except Exception as e:
        print(f"- flesch_reading_ease: ERROR - {e}")
    
    try:
        print(f"- gunning_fog: {textstat.gunning_fog(test_sentence)}")
    except Exception as e:
        print(f"- gunning_fog: ERROR - {e}")
    
    try:
        print(f"- smog_index: {textstat.smog_index(test_sentence)}")
    except Exception as e:
        print(f"- smog_index: ERROR - {e}")
    
    try:
        print(f"- automated_readability_index: {textstat.automated_readability_index(test_sentence)}")
    except Exception as e:
        print(f"- automated_readability_index: ERROR - {e}")
    
    print("\n✅ Textstat functions test completed!")
    
    # Now test the readability scores creation (this is what was failing)
    print("\nTesting readability_scores dictionary creation:")
    readability_scores = {
        "flesch_reading_ease": textstat.flesch_reading_ease(test_sentence),
        "gunning_fog": textstat.gunning_fog(test_sentence),
        "smog_index": textstat.smog_index(test_sentence),
        "automated_readability_index": textstat.automated_readability_index(test_sentence)
    }
    print(f"Readability scores: {readability_scores}")
    
    print("\n✅ All tests passed - the gunning_fog and smog_index issue should be fixed!")
    
except Exception as e:
    print(f"❌ Error occurred: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
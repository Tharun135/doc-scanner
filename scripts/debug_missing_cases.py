#!/usr/bin/env python3

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import LlamaIndexAISuggestionEngine

def debug_missing_cases():
    ai_manager = LlamaIndexAISuggestionEngine()
    
    test_cases = [
        "Data is processed by the system every hour.",
        "The configuration options are displayed in the interface."
    ]
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"Case {i+1}: {sentence}")
        try:
            result = ai_manager.generate_contextual_suggestion("Convert to active voice", sentence)
            suggestion = result.get('suggestion', 'No suggestion')
            print(f"Result: {suggestion}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        print("-" * 40)

if __name__ == "__main__":
    debug_missing_cases()

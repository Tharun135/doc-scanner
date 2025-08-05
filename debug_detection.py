#!/usr/bin/env python3
"""
Debug the procedural context detection
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.rules.rewriting_suggestions import _is_procedural_context, _is_types_verb_usage
import spacy

nlp = spacy.load("en_core_web_sm")

def debug_detection():
    """Debug why certain cases are failing"""
    
    failing_cases = [
        "User types a new password in the dialog box.",
        "The technician types configuration data into the form.",
        "The user types."
    ]
    
    for sentence in failing_cases:
        print(f"Sentence: {sentence}")
        
        # Check procedural context
        is_procedural = _is_procedural_context([sentence])
        print(f"  Is procedural context: {is_procedural}")
        
        # Check if types is verb usage
        doc = nlp(sentence)
        is_verb = _is_types_verb_usage(doc.sents.__next__(), "types")
        print(f"  Is types verb usage: {is_verb}")
        
        print()

if __name__ == "__main__":
    debug_detection()

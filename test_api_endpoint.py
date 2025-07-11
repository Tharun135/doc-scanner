#!/usr/bin/env python3
"""
Test through the actual API endpoint used by the web interface
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import json
from app.ai_improvement import get_enhanced_ai_suggestion

def test_api_endpoint():
    """Test through the API endpoint exactly like the web interface would"""
    
    # Test the problematic case
    test_data = {
        "feedback_text": "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.",
        "sentence_context": "Both options support backup files from the",
        "document_type": "technical",
        "writing_goals": ["clarity", "correctness"]
    }
    
    print("=== API Endpoint Test ===")
    print("Request data:")
    print(json.dumps(test_data, indent=2))
    print()
    
    # Call the function
    result = get_enhanced_ai_suggestion(
        test_data["feedback_text"],
        test_data["sentence_context"], 
        test_data["document_type"],
        test_data["writing_goals"]
    )
    
    print("Response:")
    print(json.dumps(result, indent=2))
    print()
    
    # Check if it's correct
    suggestion = result.get('suggestion', '')
    if "No change needed" in suggestion and "backup files" in suggestion:
        print("✅ SUCCESS: API correctly identifies noun usage")
    else:
        print("❌ ISSUE: API response unexpected")

if __name__ == "__main__":
    test_api_endpoint()

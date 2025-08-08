#!/usr/bin/env python3

"""
Test the user's specific passive voice example.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import ai_engine

def test_user_example():
    """Test the user's specific example."""
    
    feedback = "Convert passive voice to active voice for clearer, more direct communication. Example: Change 'The report was written by John' to 'John wrote the report'."
    sentence = "The selected configuration files are updated."
    
    print("🧪 TESTING USER'S SPECIFIC EXAMPLE")
    print("=" * 60)
    print(f"📝 Feedback: {feedback}")
    print(f"📝 Original: {sentence}")
    print()
    
    result = ai_engine.generate_contextual_suggestion(
        feedback_text=feedback,
        sentence_context=sentence,
        document_type="technical"
    )
    
    suggestion = result.get('suggestion', '')
    method = result.get('method', 'unknown')
    
    print(f"🤖 AI Result ({method}):")
    print(f"   {suggestion}")
    
    # Check if this matches the user's complaint
    if suggestion == f"Convert To Active Voice: {sentence}":
        print("\n❌ ISSUE: Still showing the template response!")
        print("   This is exactly what the user complained about.")
    elif sentence in suggestion and "OPTION" not in suggestion:
        print("\n❌ ISSUE: Still echoing original sentence")
    else:
        print("\n✅ SUCCESS: Providing actual conversion!")
        print(f"   Before: {sentence}")
        print(f"   After: {suggestion}")

if __name__ == "__main__":
    test_user_example()

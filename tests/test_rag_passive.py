#!/usr/bin/env python3
"""
Test RAG system with passive voice issue
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from app.rag_system import get_rag_suggestion

def test_passive_voice_rag():
    """Test RAG system with the passive voice issue."""
    
    feedback_text = "Passive voice detected: 'are displayed' - convert to active voice for clearer, more direct communication."
    sentence_context = "The configuration options of the data source are displayed."
    
    print("Testing RAG system with passive voice issue...")
    print(f"Feedback: {feedback_text}")
    print(f"Sentence: {sentence_context}")
    print("-" * 50)
    
    try:
        result = get_rag_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type="technical",
            document_content=""
        )
        
        if result:
            print("✅ RAG system generated suggestion:")
            print(f"Method: {result.get('method', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 'unknown')}")
            print(f"Suggestion: {result.get('suggestion', 'No suggestion')}")
            print(f"AI Answer: {result.get('ai_answer', 'No answer')}")
        else:
            print("❌ RAG system returned None")
            
    except Exception as e:
        print(f"❌ Error testing RAG system: {e}")

if __name__ == "__main__":
    test_passive_voice_rag()

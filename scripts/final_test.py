#!/usr/bin/env python3
"""
Final test of the enhanced AI suggestion function directly
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Test the enhanced function directly
from app.ai_improvement import get_enhanced_ai_suggestion

def test_enhanced_ai():
    """Test the enhanced AI function directly."""
    
    feedback_text = "Passive voice detected: 'are displayed' - convert to active voice for clearer, more direct communication."
    sentence_context = "The configuration options of the data source are displayed."
    
    print("Testing Enhanced AI Suggestion Function")
    print("="*50)
    print(f"Feedback: {feedback_text}")
    print(f"Sentence: {sentence_context}")
    print("-" * 50)
    
    try:
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type="technical",
            writing_goals=["clarity", "conciseness"],
            document_content=""
        )
        
        print("✅ Enhanced AI function returned result:")
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Confidence: {result.get('confidence', 'unknown')}")
        print(f"Suggestion: {result.get('suggestion', 'No suggestion')}")
        
        # Analyze which system was used
        method = result.get('method', 'unknown')
        if method == 'local_rag':
            print("\n🎯 SUCCESS: RAG system is working!")
        elif method == 'smart_fallback':
            print("\n⚠️  FALLBACK: Using rule-based system (RAG may have failed)")
        else:
            print(f"\n❓ UNKNOWN: Method '{method}' used")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing enhanced AI function: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_enhanced_ai()

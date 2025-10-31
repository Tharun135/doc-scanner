#!/usr/bin/env python3
"""
Quick test to verify the AI suggestion function works without hanging.
"""

import sys
import os
import logging

# Add current directory and app directory to path  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ai_suggestion_speed():
    """Test if the AI suggestion function responds quickly."""
    
    sentence = "To publish the FINS/TCP data in Databus, you must enter the credentials accordingly in Common Configurator."
    feedback = "Check use of adverb: 'accordingly' in sentence"
    
    print("🚀 Testing AI Suggestion Speed")
    print("=" * 60)
    print(f"Sentence: {sentence}")
    print(f"Feedback: {feedback}")
    print()
    
    try:
        import time
        start_time = time.time()
        
        # Import and call the function
        from ai_improvement import get_enhanced_ai_suggestion
        
        print("✅ Function imported successfully")
        
        # Call the function with a timeout
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback,
            sentence_context=sentence,
            document_type="technical"
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ Function completed in {duration:.2f} seconds")
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Original: {result.get('original_sentence', 'N/A')}")
        print(f"Improved: {result.get('suggestion', 'N/A')}")
        print(f"Success: {result.get('success', False)}")
        
        if duration < 2.0:
            print("🚀 FAST RESPONSE - No hanging detected!")
            return True
        else:
            print("⚠️ SLOW RESPONSE - Potential hanging issues")
            return False
            
    except Exception as e:
        print(f"❌ Function failed: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = test_ai_suggestion_speed()
    
    if success:
        print("\n✅ AI Suggestion system is working fast!")
        print("Your app should now respond quickly when clicking the AI icon.")
    else:
        print("\n❌ Still has issues. More debugging needed.")
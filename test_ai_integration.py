#!/usr/bin/env python3
"""
Test AI integration specifically for the EnhancedAISuggestionEngine
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_enhanced_ai_engine():
    """Test the enhanced AI suggestion engine"""
    try:
        from app.ai_improvement import get_enhanced_ai_suggestion, ai_engine
        print("✅ Enhanced AI suggestion engine imported successfully")
        print(f"   Model name: {ai_engine.model_name}")
        
        # Test with a simple passive voice example
        test_feedback = "This sentence contains passive voice"
        test_sentence = "The document was created by the team."
        
        print(f"\n🧪 Testing AI suggestion generation:")
        print(f"   Feedback: '{test_feedback}'")
        print(f"   Sentence: '{test_sentence}'")
        
        result = get_enhanced_ai_suggestion(
            feedback_text=test_feedback,
            sentence_context=test_sentence,
            document_type="technical",
            writing_goals=["clarity", "active_voice"]
        )
        
        print(f"\n✅ AI suggestion generated successfully:")
        print(f"   Suggestion: {result['suggestion']}")
        print(f"   Confidence: {result['confidence']}")
        print(f"   Method: {result['method']}")
        print(f"   Model used: {result.get('context_used', {}).get('model_used', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced AI engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_suggestion_endpoint():
    """Test the AI suggestion endpoint simulation"""
    try:
        from app.app import main
        print("\n🧪 Testing AI suggestion endpoint logic...")
        
        # This simulates what happens in the Flask route
        feedback_text = "This sentence contains passive voice"
        sentence_context = "The document was created by the team."
        document_type = "technical"
        writing_goals = ["clarity", "active_voice"]
        
        # Import the function used in the endpoint
        from app.ai_improvement import get_enhanced_ai_suggestion
        
        result = get_enhanced_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type=document_type,
            writing_goals=writing_goals
        )
        
        print("✅ Endpoint simulation successful")
        print(f"   Result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Endpoint simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 Enhanced AI Integration Test")
    print("=" * 50)
    
    print("\n1. Testing Enhanced AI Engine...")
    engine_ok = test_enhanced_ai_engine()
    
    print("\n2. Testing AI Suggestion Endpoint Logic...")
    endpoint_ok = test_ai_suggestion_endpoint()
    
    print("\n" + "=" * 50)
    if engine_ok and endpoint_ok:
        print("✅ All enhanced AI tests passed!")
    else:
        print("❌ Some enhanced AI tests failed.")

if __name__ == "__main__":
    main()

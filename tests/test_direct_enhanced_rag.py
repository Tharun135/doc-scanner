#!/usr/bin/env python3
"""
Test the enhanced RAG system directly with debug output
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_rag.enhanced_rag_system import EnhancedRAGSystem
    
    def test_direct_enhanced_rag():
        """Test the enhanced RAG system directly"""
        
        # Initialize the system
        system = EnhancedRAGSystem()
        
        # Test case: Capitalization issue
        sentence = "it is in ISO 8601 Zulu format."
        rule_id = "style"
        feedback = "Start sentences with a capital letter."
        
        print(f"🔍 Testing Direct Enhanced RAG:")
        print(f"  Sentence: '{sentence}'")
        print(f"  Rule ID: '{rule_id}'")
        print(f"  Feedback: '{feedback}'")
        
        try:
            result = system.get_rag_suggestion(
                feedback_text=feedback,
                sentence_context=sentence,
                rule_id=rule_id
            )
            
            print(f"  Method: {result.get('method', 'Unknown')}")
            print(f"  AI Suggestion: '{result.get('ai_suggestion', '')}'")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Confidence: {result.get('confidence', 0)}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    if __name__ == "__main__":
        test_direct_enhanced_rag()
        
except ImportError as e:
    print(f"Could not import enhanced RAG system: {e}")

#!/usr/bin/env python3
"""
Debug the enhanced RAG system step by step
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_rag.enhanced_rag_system import EnhancedRAGSystem
    from enhanced_rag.rule_specific_corrections import get_rule_specific_correction
    
    def debug_enhanced_rag():
        """Debug each step of the enhanced RAG system"""
        
        # Test case: Capitalization issue
        sentence = "it is in ISO 8601 Zulu format."
        rule_id = "style"
        feedback = "Start sentences with a capital letter."
        
        print(f"🔍 Debug Enhanced RAG Steps:")
        print(f"  Input: '{sentence}'")
        print(f"  Rule ID: '{rule_id}'")
        print(f"  Feedback: '{feedback}'")
        
        # Test rule-specific correction directly
        print(f"\n1. Testing rule-specific correction directly:")
        rule_result = get_rule_specific_correction(sentence, rule_id, feedback)
        print(f"   Result: '{rule_result}'")
        print(f"   Changed: {rule_result != sentence}")
        
        # Test the full enhanced RAG system
        print(f"\n2. Testing full enhanced RAG system:")
        system = EnhancedRAGSystem()
        
        result = system.get_rag_suggestion(
            feedback_text=feedback,
            sentence_context=sentence,
            rule_id=rule_id
        )
        
        print(f"   Full result: {result}")
        print(f"   Method: {result.get('method', 'Unknown') if result else 'None'}")
        print(f"   AI Suggestion: '{result.get('ai_suggestion', '') if result else 'None'}'")
        print(f"   Success: {result.get('success', False) if result else False}")
    
    if __name__ == "__main__":
        debug_enhanced_rag()
        
except ImportError as e:
    print(f"Could not import enhanced RAG system: {e}")

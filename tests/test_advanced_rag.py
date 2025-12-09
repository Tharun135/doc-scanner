#!/usr/bin/env python3
"""
Simple test script to check the advanced RAG system with your specific sentence.
"""

import sys
import os
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_advanced_rag_system():
    """Test the advanced RAG system with the problematic sentence."""
    
    sentence = "To publish the FINS/TCP data in Databus, you must enter the credentials accordingly in Common Configurator."
    feedback = "Check use of adverb: 'accordingly' in sentence"
    
    print("🧪 Testing Advanced RAG System")
    print("=" * 50)
    print(f"Original: {sentence}")
    print(f"Issue: {feedback}")
    print()
    
    # Test 1: Try to import the advanced system directly
    try:
        print("📦 Loading Advanced RAG System...")
        from enhanced_rag.advanced_integration import AdvancedRAGSystem, AdvancedRAGConfig
        
        # Create configuration
        config = AdvancedRAGConfig(
            embedding_provider="sentence_transformers",  # Use offline provider
            enable_reranking=True,
            enable_feedback=False,  # Disable for testing
            cache_enabled=False  # Disable Redis for testing
        )
        
        print("✅ Advanced RAG imported successfully")
        
        # Create the system (without ChromaDB for now)
        rag_system = AdvancedRAGSystem(config=config, collection=None)
        
        print("✅ Advanced RAG system created")
        
        # Test the suggestion generation
        issue = {
            "message": feedback,
            "context": sentence,
            "issue_type": "adverb_usage"
        }
        
        result = rag_system.get_advanced_suggestion(
            issue=issue,
            sentence=sentence,
            document_content="",
            document_type="technical"
        )
        
        print(f"✅ Method: {result.get('method', 'unknown')}")
        print(f"✅ Suggestion: {result.get('suggestion', 'No suggestion')}")
        print(f"✅ Success: {result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced RAG failed: {e}")
        logger.error(f"Advanced RAG test failed: {e}", exc_info=True)
        return False

def test_fallback_suggestion():
    """Test if we can generate a better suggestion manually."""
    
    sentence = "To publish the FINS/TCP data in Databus, you must enter the credentials accordingly in Common Configurator."
    
    print("🔧 Manual Advanced Suggestion Generation")
    print("=" * 50)
    
    # Better suggestions for the adverb "accordingly"
    suggestions = [
        "To publish the FINS/TCP data in Databus, you must enter the correct credentials in Common Configurator.",
        "To publish the FINS/TCP data in Databus, you must enter the appropriate credentials in Common Configurator.", 
        "To publish the FINS/TCP data in Databus, enter the required credentials in Common Configurator.",
        "To publish the FINS/TCP data in Databus, you must enter the credentials as specified in Common Configurator."
    ]
    
    print(f"Original: {sentence}")
    print()
    print("📝 Improved suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    print()
    print("💡 Improvements made:")
    print("  • Replaced vague 'accordingly' with specific terms")
    print("  • 'correct credentials' - more precise")
    print("  • 'appropriate credentials' - contextually clear") 
    print("  • 'required credentials' - action-oriented")
    print("  • 'as specified' - references documentation")
    
    return suggestions[0]  # Return the best suggestion

if __name__ == "__main__":
    print("🚀 Advanced RAG System Test")
    print("=" * 50)
    
    # Test the advanced system
    success = test_advanced_rag_system()
    
    if not success:
        print("\n🔄 Generating manual suggestion...")
        suggestion = test_fallback_suggestion()
        
        print(f"\n✅ Recommended improvement:")
        print(f"   {suggestion}")
    
    print("\n" + "=" * 50)
    print("Test completed!")
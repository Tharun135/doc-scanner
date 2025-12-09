#!/usr/bin/env python3
"""
Simple direct test of the advanced RAG system, bypassing __init__.py issues.
"""

import sys
import os
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_advanced_rag_direct():
    """Test the advanced RAG system by importing directly."""
    
    sentence = "To publish the FINS/TCP data in Databus, you must enter the credentials accordingly in Common Configurator."
    feedback = "Check use of adverb: 'accordingly' in sentence"
    
    print("🧪 Testing Advanced RAG System (Direct Import)")
    print("=" * 60)
    print(f"Original: {sentence}")
    print(f"Issue: {feedback}")
    print()
    
    try:
        # Import directly from the advanced_integration module
        import importlib.util
        
        spec = importlib.util.spec_from_file_location(
            "advanced_integration", 
            "enhanced_rag/advanced_integration.py"
        )
        advanced_integration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(advanced_integration)
        
        print("✅ Advanced integration loaded directly")
        
        # Create configuration
        config = advanced_integration.AdvancedRAGConfig(
            embedding_provider="sentence_transformers",
            enable_reranking=False,  # Disable reranking for simplicity
            enable_feedback=False,   # Disable feedback for testing
            cache_enabled=False      # Disable cache for testing
        )
        
        print("✅ Configuration created")
        
        # Create the system without ChromaDB collection for now
        rag_system = advanced_integration.AdvancedRAGSystem(config=config, collection=None)
        
        print("✅ Advanced RAG system created")
        
        # Test the suggestion generation
        issue = {
            "message": feedback,
            "context": sentence,
            "issue_type": "adverb_usage"
        }
        
        print("🔄 Generating suggestion...")
        result = rag_system.get_advanced_suggestion(
            issue=issue,
            sentence=sentence,
            document_content="",
            document_type="technical"
        )
        
        print(f"✅ Method: {result.get('method', 'unknown')}")
        print(f"✅ Original: {sentence}")
        print(f"✅ Suggestion: {result.get('suggestion', 'No suggestion')}")
        print(f"✅ AI Answer: {result.get('ai_answer', 'No answer')}")
        print(f"✅ Success: {result.get('success', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced RAG test failed: {e}")
        logger.error(f"Advanced RAG test failed: {e}", exc_info=True)
        return False

def manual_suggestion():
    """Generate manual suggestion for comparison."""
    
    sentence = "To publish the FINS/TCP data in Databus, you must enter the credentials accordingly in Common Configurator."
    
    print("\n🔧 Manual Advanced Suggestion")
    print("=" * 60)
    
    suggestions = [
        "To publish the FINS/TCP data in Databus, you must enter the correct credentials in Common Configurator.",
        "To publish the FINS/TCP data in Databus, you must enter the appropriate credentials in Common Configurator.", 
        "To publish the FINS/TCP data in Databus, enter the required credentials in Common Configurator.",
        "To publish the FINS/TCP data in Databus, you must enter the credentials as specified in Common Configurator."
    ]
    
    print(f"Original: {sentence}")
    print("\n📝 Improved suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    print("\n💡 Why this is better:")
    print("  • 'accordingly' is vague and adds no meaning")
    print("  • 'correct/appropriate/required' is more specific")
    print("  • 'as specified' refers to documentation")
    print("  • Removes unnecessary wordiness")
    
    return suggestions[0]

if __name__ == "__main__":
    print("🚀 Advanced RAG Direct Test")
    print("=" * 60)
    
    # Test the advanced system
    success = test_advanced_rag_direct()
    
    if not success:
        print("\n🔄 Using manual suggestion instead...")
        suggestion = manual_suggestion()
        
        print(f"\n✅ Final recommendation:")
        print(f"   {suggestion}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
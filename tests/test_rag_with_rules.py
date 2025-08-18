#!/usr/bin/env python3
"""
Test script to verify RAG system integration with rule knowledge base.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag_system import GeminiRAGSystem
from app.rules.passive_voice import check as passive_voice_check

def test_rag_system_with_rules():
    """Test the enhanced RAG system with rule knowledge base."""
    print("🧪 Testing RAG System with Rule Knowledge Base")
    print("=" * 60)
    
    # Initialize RAG system
    rag_system = GeminiRAGSystem()
    
    if not rag_system.is_initialized:
        print("❌ RAG system not initialized - check API key")
        return
    
    print("✅ RAG system initialized")
    
    # Check if rule knowledge base was loaded
    if hasattr(rag_system, 'rule_vectorstore') and rag_system.rule_vectorstore:
        print("✅ Rule knowledge base loaded successfully")
    else:
        print("⚠️  Rule knowledge base not loaded - testing without rules")
    
    # Test rule knowledge search
    print("\n🔍 Testing rule knowledge search...")
    test_queries = [
        "passive voice",
        "long sentences", 
        "modal verbs can may",
        "style guide formatting"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = rag_system.search_rule_knowledge(query, k=2)
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['rule_name']} (score: {result['score']:.3f})")
            print(f"     Tags: {result['tags']}")
    
    # Test enhanced RAG suggestions
    print("\n💡 Testing enhanced RAG suggestions...")
    test_content = """
    The document was written by the team. It should be reviewed carefully. 
    The changes were made by developers and the system was tested by QA engineers.
    """
    
    # Add some content to RAG
    rag_system.add_writing_guidelines("""
    PASSIVE VOICE GUIDELINES:
    - Use active voice instead of passive voice for clarity
    - Active voice makes writing more direct and engaging
    - Convert "was done by" to "X did" 
    """)
    
    # Test passive voice detection with RAG
    print("\n📝 Testing passive voice rule with RAG enhancement...")
    passive_results = passive_voice_check(test_content)
    
    print(f"Found {len(passive_results)} passive voice issues:")
    for i, result in enumerate(passive_results, 1):
        print(f"  {i}. Text: '{result.get('text', 'N/A')}'")
        print(f"     Message: {result.get('message', 'N/A')}")
        print(f"     Method: {result.get('method', 'N/A')}")
    
    # Test direct RAG suggestion
    print("\n🎯 Testing direct RAG suggestions...")
    rag_result = rag_system.get_rag_suggestion(
        feedback_text="passive voice detected",
        sentence_context="The document was written by the team",
        document_type="technical"
    )
    
    if rag_result:
        print("✅ RAG suggestion generated:")
        print(f"   Suggestion: {rag_result['suggestion']}")
        print(f"   Method: {rag_result['method']}")
        print(f"   Sources used: {len(rag_result['sources'])}")
        print(f"   Rule knowledge used: {rag_result['context_used'].get('rule_knowledge_used', 0)}")
    else:
        print("❌ No RAG suggestion generated")

def test_rule_knowledge_integration():
    """Test specific rule knowledge base integration."""
    print("\n🔧 Testing Rule Knowledge Base Integration")
    print("=" * 50)
    
    rag_system = GeminiRAGSystem()
    
    if not hasattr(rag_system, 'rule_vectorstore') or not rag_system.rule_vectorstore:
        print("❌ Rule knowledge base not available")
        return
    
    # Test semantic search for writing issues
    test_cases = [
        ("The system was designed by engineers", "passive voice"),
        ("This is a very long sentence that goes on and on", "sentence length"),
        ("You can click the button to proceed", "modal verbs"),
        ("The interface is not user-friendly", "style guide")
    ]
    
    for text, issue_type in test_cases:
        print(f"\n📄 Text: '{text}'")
        print(f"🎯 Issue type: {issue_type}")
        
        # Search for relevant rules
        rules = rag_system.search_rule_knowledge(issue_type, k=3)
        print(f"📚 Found {len(rules)} relevant rules:")
        
        for rule in rules:
            print(f"   • {rule['rule_name']} (relevance: {rule['score']:.3f})")

if __name__ == "__main__":
    test_rag_system_with_rules()
    test_rule_knowledge_integration()

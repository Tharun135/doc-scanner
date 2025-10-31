# test_enhanced_rag_demo.py
"""
Demonstration of Enhanced RAG system capabilities.
Shows the improvements over the original system.
"""
import sys
import os
import json
import time
from typing import Dict, Any, List

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_rag_integration import (
    get_enhanced_rag_integration,
    enhanced_enrich_issue_with_solution,
    monitor_enhanced_rag_performance,
    bulk_ingest_documents
)

def demo_enhanced_chunking():
    """Demonstrate improved chunking with metadata"""
    print("📝 Enhanced Chunking Demo")
    print("=" * 40)
    
    sample_document = """
# Technical Writing Guidelines for Software Documentation

## Passive Voice Issues

Passive voice is problematic in technical writing because it obscures responsibility and can confuse readers. 
The system was configured by the administrator. This sentence doesn't clearly indicate who performed the action.

### Examples of Passive Voice Problems
- "The file was created by the system"
- "Errors were found during testing"  
- "The configuration is managed by the admin"

### Active Voice Solutions
Instead of passive voice, use active voice to make instructions clearer:
- "The system creates the file"
- "Testing found errors"
- "The admin manages the configuration"

## Adverb Usage Guidelines

Adverbs like "easily", "simply", and "quickly" should be avoided in technical documentation.
You can easily configure the system by simply following these steps.
Really good documentation doesn't need unnecessary adverbs.

### Why Avoid Adverbs
- They add subjectivity ("easily" for whom?)
- They can mislead users about difficulty
- They make text less precise

## Click Instructions

Don't use "click on" in user interface instructions. Instead, use direct imperative language.

Bad: "Click on the Save button to continue"
Good: "Click Save to continue" or "Select Save to continue"
"""
    
    rag_integration = get_enhanced_rag_integration()
    
    if rag_integration.enhanced_system:
        # Demonstrate enhanced document ingestion
        chunk_count = rag_integration.ingest_document(
            document_text=sample_document,
            source_doc_id="demo_writing_guide",
            product="docscanner",
            version="2.0"
        )
        
        print(f"✅ Created {chunk_count} semantically coherent chunks")
        print("   Each chunk includes:")
        print("   - Rich metadata (product, version, section)")
        print("   - Context-aware boundaries (paragraph/heading)")
        print("   - Optimal size (2-8 sentences)")
        print("   - Embedded with metadata prefix for better retrieval")
    else:
        print("❌ Enhanced system not available")

def demo_hybrid_retrieval():
    """Demonstrate hybrid semantic + BM25 retrieval"""
    print("\n🔍 Hybrid Retrieval Demo")
    print("=" * 40)
    
    rag_integration = get_enhanced_rag_integration()
    
    test_queries = [
        {
            "query": "passive voice problems in technical writing",
            "description": "Semantic query - should find conceptually related content"
        },
        {
            "query": "click on button",
            "description": "Exact match query - BM25 should excel here"
        },
        {
            "query": "easily simply adverbs",
            "description": "Mixed query - both semantic and exact matching"
        }
    ]
    
    for test in test_queries:
        print(f"\n🔎 Query: '{test['query']}'")
        print(f"   Type: {test['description']}")
        
        if rag_integration.enhanced_system:
            # Get retrieval results with hybrid search
            results = rag_integration.enhanced_system.vector_store.query_enhanced(
                query_text=test['query'],
                n_results=3,
                use_hybrid=True
            )
            
            print(f"   Results: {len(results)} chunks found")
            
            for i, result in enumerate(results[:2], 1):
                score_info = ""
                if 'hybrid_score' in result:
                    score_info = f" (hybrid: {result['hybrid_score']:.3f})"
                elif 'distance' in result:
                    score_info = f" (semantic: {1-result['distance']:.3f})"
                
                print(f"   {i}. {result['text'][:80]}...{score_info}")
                
                # Show source information
                metadata = result.get('metadata', {})
                section = metadata.get('section_title', 'Unknown')
                print(f"      Source: {section}")
        else:
            print("   ❌ Enhanced retrieval not available")

def demo_constrained_prompting():
    """Demonstrate constrained prompting with source attribution"""
    print("\n🎯 Constrained Prompting Demo")
    print("=" * 40)
    
    test_cases = [
        {
            "sentence": "The file was created by the system automatically.",
            "rule_id": "passive-voice",
            "description": "Passive voice correction with source attribution"
        },
        {
            "sentence": "You can easily click on the Save button to continue.",
            "rule_id": "adverb-usage", 
            "description": "Multiple issues: adverb + click-on pattern"
        },
        {
            "sentence": "The configuration should be updated by the admin.",
            "rule_id": "passive-voice",
            "description": "Modal verb + passive voice combination"
        }
    ]
    
    rag_integration = get_enhanced_rag_integration()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"   Input: \"{test_case['sentence']}\"")
        print(f"   Rule: {test_case['rule_id']}")
        
        # Get enhanced suggestion
        response = rag_integration.get_rag_suggestion(
            feedback_text=f"{test_case['rule_id']} detected",
            sentence_context=test_case['sentence'],
            rule_id=test_case['rule_id']
        )
        
        if response:
            print(f"   ✅ Correction: \"{response.get('suggestion', 'N/A')}\"")
            print(f"   📊 Confidence: {response.get('confidence', 'N/A')}")
            print(f"   🔧 Method: {response.get('method', 'N/A')}")
            
            # Show sources if available
            sources = response.get('sources', [])
            if sources:
                print(f"   📚 Sources: {len(sources)} retrieved chunks")
                for j, source in enumerate(sources[:2], 1):
                    section = source.get('section', 'Unknown')
                    score = source.get('score', 0)
                    print(f"      {j}. {section} (score: {score:.3f})")
            else:
                print("   📚 Sources: Deterministic fallback used")
        else:
            print("   ❌ No response generated")

def demo_performance_comparison():
    """Demonstrate performance improvements"""
    print("\n⚡ Performance Comparison Demo")
    print("=" * 40)
    
    rag_integration = get_enhanced_rag_integration()
    
    # Run multiple queries to gather performance data
    test_sentences = [
        ("The document was created by the user.", "passive-voice"),
        ("You can easily complete this task really quickly.", "adverb-usage"),
        ("Click on the Submit button when ready.", "click-on"),
        ("The system should be configured properly.", "modal-verbs"),
        ("IMPORTANT information must be saved.", "all-caps")
    ]
    
    print("Running performance test with 10 queries...")
    
    start_time = time.time()
    successful_responses = 0
    response_times = []
    
    for sentence, rule_id in test_sentences * 2:  # Run each test twice
        query_start = time.time()
        
        response = rag_integration.get_rag_suggestion(
            feedback_text=f"{rule_id} detected",
            sentence_context=sentence,
            rule_id=rule_id
        )
        
        query_time = time.time() - query_start
        response_times.append(query_time)
        
        if response:
            successful_responses += 1
    
    total_time = time.time() - start_time
    avg_response_time = sum(response_times) / len(response_times)
    
    print(f"✅ Performance Results:")
    print(f"   Total queries: {len(response_times)}")
    print(f"   Successful responses: {successful_responses}")
    print(f"   Success rate: {successful_responses/len(response_times):.1%}")
    print(f"   Average response time: {avg_response_time:.3f}s")
    print(f"   Queries per second: {len(response_times)/total_time:.1f}")
    
    # Get system metrics
    stats = rag_integration.get_system_stats()
    if "enhanced_metrics" in stats:
        print(f"   Enhanced system usage: {stats.get('enhanced_usage_rate', 0):.1%}")
        print(f"   Fallback usage: {stats.get('fallback_usage_rate', 0):.1%}")

def demo_batch_ingestion():
    """Demonstrate batch document ingestion"""
    print("\n📚 Batch Ingestion Demo")
    print("=" * 40)
    
    sample_documents = [
        {
            "id": "style_guide_v1",
            "product": "docscanner",
            "version": "2.0",
            "content": """
# Microsoft Style Guide Excerpts

## Voice and Tone
Use active voice whenever possible. Active voice makes it clear who's performing an action.

Passive: "The file is processed by the system."
Active: "The system processes the file."

## Word Choice
Avoid unnecessary adverbs. Words like "easily," "simply," and "just" can be removed without losing meaning.
"""
        },
        {
            "id": "ui_guidelines",
            "product": "docscanner", 
            "version": "2.0",
            "content": """
# User Interface Guidelines

## Button Instructions
Use direct imperative language for button instructions:
- Say "Click Save" not "Click on the Save button"
- Say "Select Continue" not "Click on Continue"

## Error Messages  
Write clear, actionable error messages in active voice.
Avoid: "An error was encountered by the system"
Use: "The system encountered an error"
"""
        }
    ]
    
    print("Ingesting 2 sample documents with enhanced chunking...")
    
    ingestion_stats = bulk_ingest_documents(sample_documents)
    
    print(f"✅ Ingestion Results:")
    print(f"   Documents processed: {ingestion_stats['successful_ingestions']}/{ingestion_stats['total_documents']}")
    print(f"   Total chunks created: {ingestion_stats['total_chunks']}")
    
    if ingestion_stats['errors']:
        print(f"   Errors: {len(ingestion_stats['errors'])}")
        for error in ingestion_stats['errors'][:2]:
            print(f"     - {error}")

def main():
    """Run complete enhanced RAG demonstration"""
    print("🚀 Enhanced RAG System Demonstration")
    print("=" * 60)
    print("This demo shows the key improvements in the enhanced RAG system:")
    print("1. Semantic coherent chunking with rich metadata")
    print("2. Hybrid retrieval (semantic + BM25 exact-match)")
    print("3. Constrained prompting with source attribution")
    print("4. Performance optimizations and caching")
    print("5. Comprehensive evaluation metrics")
    print()
    
    # Run all demonstrations
    demo_enhanced_chunking()
    demo_hybrid_retrieval()
    demo_constrained_prompting()
    demo_performance_comparison()
    demo_batch_ingestion()
    
    print("\n🎉 Enhanced RAG Demonstration Complete!")
    print("\n📊 Final System Overview:")
    monitor_enhanced_rag_performance()
    
    print("\n💡 Integration Guide:")
    print("1. Replace existing RAG calls with enhanced_enrich_issue_with_solution()")
    print("2. Use bulk_ingest_documents() for adding new content")
    print("3. Monitor performance with monitor_enhanced_rag_performance()")
    print("4. Tune hybrid_alpha parameter for your use case")
    print("5. Add evaluation metrics to measure improvements")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Simple test to check RAG content and search functionality."""

import sys
import os

# Add app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def check_rag_content():
    """Check what content is in the RAG system."""
    try:
        from app.rag_routes import init_rag_system, retriever
        
        # Initialize RAG system
        print("Initializing RAG system...")
        init_success = init_rag_system()
        print(f"Init success: {init_success}")
        
        # Re-import to get updated retriever
        from app.rag_routes import retriever
        print(f"Retriever: {retriever}")
        
        if retriever:
            # Search for passive voice content
            print("\nSearching for passive voice content...")
            results = retriever.search("passive voice examples", k=5)
            print(f"Found {len(results) if results else 0} results")
            
            if results:
                for i, result in enumerate(results, 1):
                    score = result.get('score', 0)
                    content = result.get('content', '')[:300]
                    print(f"\nResult {i}: Score {score:.3f}")
                    print(f"Content: {content}...")
            
            # Test specific query for "must be created"
            print("\n" + "="*50)
            print("Testing specific query: 'must be created'")
            results2 = retriever.search("must be created passive active", k=3)
            print(f"Found {len(results2) if results2 else 0} results")
            
            if results2:
                for i, result in enumerate(results2, 1):
                    score = result.get('score', 0)
                    content = result.get('content', '')[:200]
                    print(f"Result {i}: Score {score:.3f} - {content}...")
        else:
            print("Retriever not available")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_rag_content()
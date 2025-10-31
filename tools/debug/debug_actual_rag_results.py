#!/usr/bin/env python3
"""
Debug what documents are actually being retrieved from ChromaDB
"""

import sys
import os
import re

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_actual_rag_search():
    print("🔍 Debug Actual RAG Search Results")
    print("=" * 45)
    
    try:
        from app.document_first_ai import DocumentFirstAIEngine
        
        print("✅ Creating DocumentFirstAIEngine...")
        engine = DocumentFirstAIEngine()
        
        if not engine.collection:
            print("❌ No ChromaDB collection available")
            return
        
        # Test the exact search queries used in _contextual_rag_search
        search_queries = [
            "passive voice A data source must be created.",
            "passive voice examples active voice conversion", 
            "must be created passive active",
            "special cases passive voice"
        ]
        
        for query in search_queries:
            print(f"\n🔍 Testing query: '{query}'")
            
            results = engine.collection.query(
                query_texts=[query],
                n_results=3,
                include=["documents", "metadatas", "distances"]
            )
            
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    distance = results["distances"][0][i] if results["distances"] else 1.0
                    print(f"  📄 Result {i+1} (distance: {distance:.3f}):")
                    print(f"     Content: {doc[:300]}...")
                    
                    # Test the regex on this actual content
                    if "passive" in doc and "active" in doc:
                        print("     🎯 Contains passive/active keywords")
                        
                        # Test the regex pattern
                        passive_active_patterns = re.findall(
                            r'"passive":\s*"([^"]*must\s+be[^"]*)".*?"active":\s*"([^"]*)"',
                            doc, re.IGNORECASE | re.DOTALL
                        )
                        
                        if passive_active_patterns:
                            print(f"     ✅ Regex found patterns: {passive_active_patterns}")
                            
                            for passive, active in passive_active_patterns:
                                if "must be created" in passive.lower():
                                    print(f"     🎉 FOUND TARGET PATTERN!")
                                    print(f"        Passive: '{passive}'")
                                    print(f"        Active: '{active}'")
                        else:
                            print("     ❌ Regex found no patterns")
                            
                            # Debug: try a simpler regex
                            simpler_patterns = re.findall(r'"passive"[^}]*"active"[^}]*', doc)
                            if simpler_patterns:
                                print(f"     🔍 Found simpler matches: {len(simpler_patterns)}")
                                print(f"        Example: {simpler_patterns[0][:200]}...")
            else:
                print(f"  ❌ No results for query")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_actual_rag_search()
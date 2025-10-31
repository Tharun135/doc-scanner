#!/usr/bin/env python3
"""
Debug script to see what passive voice content is actually stored in ChromaDB
"""

import chromadb
import json
from pathlib import Path

def debug_passive_voice_content():
    print("🔍 Debug: Passive Voice JSON Content in ChromaDB")
    print("=" * 60)
    
    try:
        # Connect to ChromaDB
        db_path = Path("./chroma_db")
        print(f"📁 ChromaDB path: {db_path}")
        
        client = chromadb.PersistentClient(path=str(db_path))
        collection = client.get_collection("docscanner_knowledge")
        
        print(f"📚 Total documents in collection: {collection.count()}")
        print()
        
        # Search for passive voice related content
        queries = [
            "passive voice",
            "active voice",
            "must be created", 
            "conversion examples",
            "data source",
            "special cases"
        ]
        
        for query in queries:
            print(f"🔍 Searching for: '{query}'")
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0][:2]):  # Show top 2
                    print(f"   📄 Result {i+1}: {doc[:200]}...")
                    
                    # Try to parse as JSON to see conversion patterns
                    try:
                        if doc.strip().startswith('{'):
                            json_data = json.loads(doc)
                            if 'examples' in json_data:
                                print(f"   🎯 Found examples: {len(json_data['examples'])} patterns")
                                for ex in json_data['examples'][:2]:
                                    print(f"      • {ex.get('passive', 'N/A')} → {ex.get('active', 'N/A')}")
                            elif 'conversion_patterns' in json_data:
                                print(f"   🎯 Found patterns: {len(json_data['conversion_patterns'])} rules")
                    except:
                        pass
            else:
                print(f"   ❌ No results found")
            print()
        
        # Get all documents to see what's actually there
        print("\n📋 All documents in collection:")
        print("-" * 40)
        all_docs = collection.get()
        
        for i, doc in enumerate(all_docs['documents'][:5]):  # Show first 5
            print(f"Doc {i+1}: {doc[:150]}...")
            
            # Check if it's JSON
            try:
                if doc.strip().startswith('{'):
                    json_data = json.loads(doc)
                    print(f"   📊 JSON keys: {list(json_data.keys())}")
                    if 'examples' in json_data:
                        print(f"   🎯 {len(json_data['examples'])} conversion examples found")
                        # Show a sample
                        if json_data['examples']:
                            sample = json_data['examples'][0]
                            print(f"   💡 Sample: '{sample.get('passive', 'N/A')}' → '{sample.get('active', 'N/A')}'")
            except:
                pass
            print()
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_passive_voice_content()
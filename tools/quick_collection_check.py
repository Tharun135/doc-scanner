#!/usr/bin/env python3
"""
Quick check of ChromaDB collections to diagnose upload issues
"""

import os
import chromadb
from chromadb.config import Settings

def check_collections():
    """Check ChromaDB collection status."""
    print("🔍 Quick ChromaDB Collection Check")
    print("=" * 40)
    
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collections = client.list_collections()
        
        print(f"📚 Found {len(collections)} collections:")
        
        total_docs = 0
        for collection in collections:
            count = collection.count()
            total_docs += count
            print(f"  🔹 {collection.name}: {count} documents")
        
        print(f"\n📊 Total documents across all collections: {total_docs}")
        
        # Check if the unified collection exists and has the expected count
        try:
            unified = client.get_collection("docscanner_knowledge")
            unified_count = unified.count()
            print(f"✅ Unified collection 'docscanner_knowledge': {unified_count} documents")
            
            if unified_count != total_docs:
                print(f"⚠️ Warning: Unified collection ({unified_count}) doesn't match total ({total_docs})")
        except:
            print("❌ No unified collection found")
            
        return total_docs
        
    except Exception as e:
        print(f"❌ Error checking collections: {e}")
        return 0

if __name__ == "__main__":
    check_collections()
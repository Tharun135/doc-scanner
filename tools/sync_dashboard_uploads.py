#!/usr/bin/env python3
"""
Update Unified Collection with New Uploads
This script will sync the unified collection with all new uploads.
"""

import os
import chromadb
from chromadb.config import Settings

def sync_unified_collection():
    """Sync the unified collection with all new uploads."""
    print("🔄 Syncing Unified Collection with New Uploads")
    print("=" * 50)
    
    try:
        client = chromadb.PersistentClient(path="./chroma_db")
        collections = client.list_collections()
        
        # Get the unified collection
        try:
            unified_collection = client.get_collection("docscanner_knowledge")
        except:
            print("❌ Unified collection not found!")
            return False
        
        current_unified_count = unified_collection.count()
        print(f"📊 Current unified collection count: {current_unified_count}")
        
        # Get current IDs in unified collection to avoid duplicates
        existing_results = unified_collection.get()
        existing_ids = set(existing_results['ids']) if existing_results['ids'] else set()
        print(f"📋 Existing IDs in unified collection: {len(existing_ids)}")
        
        # Collect new documents from all other collections
        new_documents = []
        new_metadatas = []
        new_ids = []
        
        for collection in collections:
            if collection.name != "docscanner_knowledge":
                print(f"\n📋 Checking {collection.name}...")
                try:
                    results = collection.get()
                    
                    if results['documents']:
                        added_count = 0
                        for i, (doc, metadata, doc_id) in enumerate(zip(
                            results['documents'], 
                            results['metadatas'] or [{}] * len(results['documents']),
                            results['ids']
                        )):
                            # Create unified ID
                            unified_id = f"{collection.name}_{doc_id}"
                            
                            # Skip if already exists
                            if unified_id in existing_ids:
                                continue
                            
                            # Ensure metadata is a dict
                            if metadata is None:
                                metadata = {}
                            
                            # Add source collection info
                            metadata['source_collection'] = collection.name
                            metadata['unified_id'] = unified_id
                            
                            new_documents.append(doc)
                            new_metadatas.append(metadata)
                            new_ids.append(unified_id)
                            added_count += 1
                        
                        print(f"  ✅ Found {added_count} new documents (total in collection: {len(results['documents'])})")
                    
                except Exception as e:
                    print(f"  ❌ Error reading {collection.name}: {e}")
        
        # Add new documents to unified collection
        if new_documents:
            print(f"\n📝 Adding {len(new_documents)} new documents to unified collection...")
            
            # Add documents in batches
            batch_size = 100
            for i in range(0, len(new_documents), batch_size):
                batch_docs = new_documents[i:i+batch_size]
                batch_metadata = new_metadatas[i:i+batch_size]
                batch_ids = new_ids[i:i+batch_size]
                
                unified_collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadata,
                    ids=batch_ids
                )
                print(f"  📝 Added batch {i//batch_size + 1} ({len(batch_docs)} documents)")
            
            final_count = unified_collection.count()
            print(f"\n✅ Unified collection updated!")
            print(f"📊 Final count: {final_count} documents")
            print(f"📈 Added: {final_count - current_unified_count} new documents")
            return True
        else:
            print("\n✅ No new documents to add - unified collection is up to date!")
            return True
            
    except Exception as e:
        print(f"❌ Error syncing unified collection: {e}")
        return False

def main():
    """Main execution function."""
    print("🔄 RAG Dashboard Sync Tool")
    print("=" * 30)
    print("This tool will sync your uploaded documents with the dashboard.")
    print()
    
    if sync_unified_collection():
        print("\n🎉 SUCCESS! Your dashboard should now show updated document counts!")
        print("\n📊 Next steps:")
        print("1. Refresh your browser at: http://localhost:5000/rag/dashboard")
        print("2. You should now see the increased document count!")
        print("3. Your search will now include all uploaded documents!")
    else:
        print("\n❌ Sync failed - please check the error messages above")

if __name__ == "__main__":
    main()
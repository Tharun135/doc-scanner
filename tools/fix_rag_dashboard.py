#!/usr/bin/env python3
"""
Fix RAG Dashboard to Show Uploaded Documents
This script fixes the connection between your uploaded documents and the dashboard.
"""

import os
import sys
import chromadb
from chromadb.config import Settings

def analyze_chromadb_collections():
    """Analyze existing ChromaDB collections and their contents."""
    print("🔍 Analyzing ChromaDB Collections...")
    print("=" * 50)
    
    # Check both possible ChromaDB locations
    db_paths = ["./chroma_db", "./chroma", "./app/chroma_db"]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"\n📂 Found ChromaDB at: {db_path}")
            try:
                client = chromadb.PersistentClient(path=db_path)
                collections = client.list_collections()
                
                print(f"📚 Collections ({len(collections)}):")
                total_chunks = 0
                
                for collection in collections:
                    print(f"  🔹 {collection.name}")
                    try:
                        count = collection.count()
                        total_chunks += count
                        print(f"    📊 Documents: {count}")
                        
                        # Get a sample to check structure
                        if count > 0:
                            sample = collection.get(limit=1)
                            if sample['documents']:
                                doc_preview = sample['documents'][0][:100] + "..." if len(sample['documents'][0]) > 100 else sample['documents'][0]
                                print(f"    📄 Sample: {doc_preview}")
                                if sample['metadatas'] and sample['metadatas'][0]:
                                    print(f"    🏷️  Metadata: {sample['metadatas'][0]}")
                    except Exception as e:
                        print(f"    ❌ Error reading collection: {e}")
                
                print(f"\n📈 Total chunks across all collections: {total_chunks}")
                
                if total_chunks > 0:
                    return db_path, collections, total_chunks
                    
            except Exception as e:
                print(f"❌ Error accessing {db_path}: {e}")
    
    return None, [], 0

def create_unified_collection():
    """Create a unified collection that the dashboard can read from."""
    print("\n🔧 Creating Unified Collection for Dashboard...")
    print("=" * 50)
    
    db_path, collections, total_chunks = analyze_chromadb_collections()
    
    if not db_path or total_chunks == 0:
        print("❌ No documents found in ChromaDB collections")
        return False
    
    try:
        client = chromadb.PersistentClient(path=db_path)
        
        # Check if unified collection already exists
        try:
            unified_collection = client.get_collection("docscanner_knowledge")
            print("✅ Found existing unified collection")
            existing_count = unified_collection.count()
            print(f"📊 Existing documents: {existing_count}")
            
            if existing_count >= total_chunks:
                print("✅ Unified collection is up to date!")
                return True
        except:
            print("📝 Creating new unified collection...")
        
        # Create or get the unified collection
        try:
            unified_collection = client.create_collection(
                name="docscanner_knowledge",
                metadata={"description": "Unified collection for dashboard display"}
            )
        except:
            unified_collection = client.get_collection("docscanner_knowledge")
        
        # Copy documents from all collections
        all_documents = []
        all_metadatas = []
        all_ids = []
        
        for collection in collections:
            if collection.name != "docscanner_knowledge":
                print(f"📋 Copying from {collection.name}...")
                try:
                    # Get all documents from this collection
                    results = collection.get()
                    
                    if results['documents']:
                        # Add collection source to metadata
                        for i, (doc, metadata, doc_id) in enumerate(zip(
                            results['documents'], 
                            results['metadatas'] or [{}] * len(results['documents']),
                            results['ids']
                        )):
                            # Ensure metadata is a dict
                            if metadata is None:
                                metadata = {}
                            
                            # Add source collection info
                            metadata['source_collection'] = collection.name
                            metadata['unified_id'] = f"{collection.name}_{doc_id}"
                            
                            all_documents.append(doc)
                            all_metadatas.append(metadata)
                            all_ids.append(f"{collection.name}_{doc_id}")
                    
                    print(f"  ✅ Copied {len(results['documents'])} documents")
                    
                except Exception as e:
                    print(f"  ❌ Error copying from {collection.name}: {e}")
        
        if all_documents:
            # Add documents to unified collection in batches
            batch_size = 100
            for i in range(0, len(all_documents), batch_size):
                batch_docs = all_documents[i:i+batch_size]
                batch_metadata = all_metadatas[i:i+batch_size]
                batch_ids = all_ids[i:i+batch_size]
                
                unified_collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadata,
                    ids=batch_ids
                )
                print(f"  📝 Added batch {i//batch_size + 1} ({len(batch_docs)} documents)")
            
            final_count = unified_collection.count()
            print(f"✅ Unified collection created with {final_count} documents!")
            return True
        else:
            print("❌ No documents found to copy")
            return False
            
    except Exception as e:
        print(f"❌ Error creating unified collection: {e}")
        return False

def verify_rag_system():
    """Verify that the RAG system can now see the documents."""
    print("\n🧪 Verifying RAG System...")
    print("=" * 30)
    
    try:
        # Import the retriever
        sys.path.append('.')
        from app.advanced_retrieval import AdvancedRetriever
        
        # Initialize retriever
        retriever = AdvancedRetriever()
        
        # Get stats
        stats = retriever.get_collection_stats()
        print(f"📊 Dashboard will now show:")
        print(f"   Total Chunks: {stats.get('total_chunks', 0)}")
        print(f"   Documents: {stats.get('documents_count', 0)}")
        print(f"   ChromaDB: {'✅ Healthy' if stats.get('chromadb_available') else '❌ Not Available'}")
        print(f"   Embeddings: {'✅ Active' if stats.get('embeddings_available') else '❌ Not Available'}")
        
        if stats.get('total_chunks', 0) > 0:
            print("✅ RAG system successfully sees your documents!")
            return True
        else:
            print("❌ RAG system still can't see documents")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying RAG system: {e}")
        return False

def main():
    """Main execution function."""
    print("🚀 RAG Dashboard Fix Tool")
    print("=" * 40)
    print("This tool will fix your RAG dashboard to show uploaded documents.")
    print()
    
    # Step 1: Analyze existing data
    db_path, collections, total_chunks = analyze_chromadb_collections()
    
    if total_chunks == 0:
        print("\n❌ No documents found in any ChromaDB collections.")
        print("💡 Make sure you've uploaded documents via the RAG upload interface.")
        return
    
    print(f"\n✅ Found {total_chunks} document chunks across {len(collections)} collections")
    
    # Step 2: Create unified collection
    if create_unified_collection():
        print("\n✅ Successfully created unified collection!")
    else:
        print("\n❌ Failed to create unified collection")
        return
    
    # Step 3: Verify RAG system
    if verify_rag_system():
        print("\n🎉 SUCCESS! Your RAG dashboard should now work properly!")
        print("\n📊 Next steps:")
        print("1. Start your Flask app: python run.py")
        print("2. Visit: http://localhost:5000/rag/dashboard")
        print("3. You should now see your document count and be able to search!")
    else:
        print("\n❌ RAG system verification failed")
        print("💡 Try restarting your Flask application")

if __name__ == "__main__":
    main()
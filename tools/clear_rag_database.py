#!/usr/bin/env python3
"""
Clear all files/documents from the ChromaDB database
"""

import chromadb
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_database():
    print("🗑️ Clearing All Files from ChromaDB Database")
    print("=" * 50)
    
    try:
        # Connect to ChromaDB
        db_path = Path("./chroma_db")
        print(f"📁 Database path: {db_path}")
        
        if not db_path.exists():
            print("❌ Database directory doesn't exist")
            return
        
        client = chromadb.PersistentClient(path=str(db_path))
        
        # Get all collections
        try:
            collections = client.list_collections()
            print(f"📚 Found {len(collections)} collections")
            
            for collection in collections:
                print(f"\n🔍 Processing collection: {collection.name}")
                
                # Get document count before deletion
                count_before = collection.count()
                print(f"   📊 Documents before deletion: {count_before}")
                
                if count_before > 0:
                    # Get all document IDs
                    all_docs = collection.get()
                    
                    if all_docs['ids']:
                        # Delete all documents
                        collection.delete(ids=all_docs['ids'])
                        print(f"   🗑️ Deleted {len(all_docs['ids'])} documents")
                    
                    # Verify deletion
                    count_after = collection.count()
                    print(f"   📊 Documents after deletion: {count_after}")
                    
                    if count_after == 0:
                        print(f"   ✅ Collection '{collection.name}' cleared successfully")
                    else:
                        print(f"   ⚠️ Collection '{collection.name}' still has {count_after} documents")
                else:
                    print(f"   ℹ️ Collection '{collection.name}' was already empty")
            
            print(f"\n🎯 Database clearing completed!")
            print(f"✅ All collections processed")
            
        except Exception as e:
            print(f"❌ Error accessing collections: {e}")
            
            # Alternative: Try to delete the specific collection we know exists
            try:
                print(f"\n🔄 Trying to clear known collection 'docscanner_knowledge'...")
                collection = client.get_collection("docscanner_knowledge")
                
                count_before = collection.count()
                print(f"   📊 Documents before deletion: {count_before}")
                
                if count_before > 0:
                    all_docs = collection.get()
                    if all_docs['ids']:
                        collection.delete(ids=all_docs['ids'])
                        print(f"   🗑️ Deleted {len(all_docs['ids'])} documents")
                    
                    count_after = collection.count()
                    print(f"   📊 Documents after deletion: {count_after}")
                    
                    if count_after == 0:
                        print(f"   ✅ Collection 'docscanner_knowledge' cleared successfully")
                else:
                    print(f"   ℹ️ Collection 'docscanner_knowledge' was already empty")
                    
            except Exception as e2:
                print(f"❌ Error clearing known collection: {e2}")
    
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        import traceback
        traceback.print_exc()

def clear_database_complete():
    """
    Complete database reset - removes the entire database directory
    """
    print("\n🔥 COMPLETE DATABASE RESET")
    print("=" * 30)
    print("⚠️ This will delete the entire database directory!")
    
    import shutil
    
    db_path = Path("./chroma_db")
    
    if db_path.exists():
        try:
            shutil.rmtree(db_path)
            print(f"🗑️ Deleted entire database directory: {db_path}")
            print("✅ Database completely reset")
        except Exception as e:
            print(f"❌ Error deleting database directory: {e}")
    else:
        print("ℹ️ Database directory doesn't exist")

if __name__ == "__main__":
    print("🛠️ Database Clearing Options:")
    print("1. Clear all documents (keep structure)")
    print("2. Complete reset (delete entire database)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        clear_database()
    elif choice == "2":
        clear_database_complete()
    else:
        print("Invalid choice. Clearing documents only...")
        clear_database()
    
    print("\n🎯 Operation completed!")
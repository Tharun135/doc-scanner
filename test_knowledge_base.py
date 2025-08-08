#!/usr/bin/env python3
"""
Test script to check what's in the knowledge base
"""

def test_knowledge_base():
    try:
        # Try to import and check ChromaDB directly
        import chromadb
        
        # Connect to the ChromaDB
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        try:
            collection = chroma_client.get_collection("doc_scanner_knowledge")
            data = collection.get()
            
            print(f"📊 KNOWLEDGE BASE ANALYSIS")
            print(f"=" * 40)
            print(f"Total documents in knowledge base: {len(data['ids'])}")
            
            if data['metadatas']:
                print(f"\n📝 DOCUMENT BREAKDOWN:")
                
                # Count by type
                type_counts = {}
                category_counts = {}
                files_imported = []
                
                for metadata in data['metadatas']:
                    doc_type = metadata.get('type', 'unknown')
                    category = metadata.get('category', 'unknown')
                    filename = metadata.get('filename', metadata.get('source', 'N/A'))
                    
                    type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
                    category_counts[category] = category_counts.get(category, 0) + 1
                    
                    if filename != 'N/A' and filename not in files_imported:
                        files_imported.append(filename)
                
                print(f"\n🗂️  BY TYPE:")
                for doc_type, count in type_counts.items():
                    print(f"   {doc_type}: {count} documents")
                
                print(f"\n📁 BY CATEGORY:")
                for category, count in category_counts.items():
                    print(f"   {category}: {count} documents")
                
                print(f"\n📄 IMPORTED FILES ({len(files_imported)} files):")
                for filename in sorted(files_imported):
                    print(f"   ✅ {filename}")
                
                # Show ALL documents with metadata
                print(f"\n📋 DETAILED DOCUMENT LIST:")
                for i, metadata in enumerate(data['metadatas'], 1):
                    filename = metadata.get('filename', metadata.get('source', 'N/A'))
                    doc_type = metadata.get('type', 'unknown')
                    category = metadata.get('category', 'unknown')
                    description = metadata.get('description', 'No description')
                    print(f"   {i:2d}. {filename} | {doc_type} | {category}")
                    if description != 'No description':
                        print(f"       → {description}")
                
                print(f"\n🔍 WHEN YOU USE THE APP:")
                print(f"   • It searches through ALL {len(data['ids'])} documents")
                print(f"   • Uses similarity search to find the top 3 most relevant")
                print(f"   • Combines findings with AI to generate suggestions")
                print(f"   • Your 7 style guide files are included in this search!")
                
            else:
                print("❌ No documents found in knowledge base")
                
        except Exception as e:
            print(f"❌ Could not access collection: {e}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure ChromaDB is installed and the knowledge base exists")

if __name__ == "__main__":
    test_knowledge_base()

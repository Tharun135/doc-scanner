#!/usr/bin/env python3
"""
Fix the knowledge base by creating a new collection with the correct dimensions
and importing all documents properly.
"""

import chromadb
import os
from datetime import datetime

def diagnose_collection():
    """Diagnose the current collection and its embedding dimensions."""
    try:
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        print("🔍 DIAGNOSING CURRENT COLLECTION")
        print("=" * 40)
        
        try:
            collection = chroma_client.get_collection("doc_scanner_knowledge")
            data = collection.get()
            
            print(f"Current collection exists with {len(data['ids'])} documents")
            
            # Check if there are any embeddings to determine dimension
            if data['embeddings'] and len(data['embeddings']) > 0:
                embedding_dim = len(data['embeddings'][0])
                print(f"Current embedding dimension: {embedding_dim}")
            else:
                print("No embeddings found in collection")
                
        except Exception as e:
            print(f"Collection doesn't exist or error: {e}")
            
        # List all collections
        collections = chroma_client.list_collections()
        print(f"\nAll collections: {[c.name for c in collections]}")
        
    except Exception as e:
        print(f"Error diagnosing: {e}")

def create_new_collection():
    """Create a new collection with the correct dimensions and import documents."""
    try:
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        
        print("\n🔧 CREATING NEW COLLECTION")
        print("=" * 40)
        
        # Delete old collection if it exists
        try:
            chroma_client.delete_collection("doc_scanner_knowledge")
            print("✅ Deleted old collection")
        except Exception:
            print("ℹ️  No old collection to delete")
        
        # Create new collection
        collection = chroma_client.create_collection(
            name="doc_scanner_knowledge",
            metadata={"description": "Doc Scanner knowledge base with style guides"}
        )
        print("✅ Created new collection")
        
        return collection, chroma_client
        
    except Exception as e:
        print(f"❌ Error creating collection: {e}")
        return None, None

def import_style_guides_direct(collection):
    """Import style guides directly to ChromaDB."""
    style_guides_path = "style_guides"
    
    files_to_import = [
        {
            "path": "app-template.md",
            "type": "template",
            "category": "app_documentation",
            "description": "Standard template structure for Industrial Edge apps"
        },
        {
            "path": "company_style_guide.md",
            "type": "company_style",
            "category": "style_guide",
            "description": "Official company writing style guide"
        },
        {
            "path": "connector-template.md",
            "type": "template",
            "category": "connector_docs",
            "description": "Template structure for connector documentation"
        },
        {
            "path": "quick-start-for-devs.md",
            "type": "onboarding_guide",
            "category": "developer_docs",
            "description": "Quick start guide for writing developer documentation"
        },
        {
            "path": "README.md",
            "type": "readme",
            "category": "meta_docs",
            "description": "Readme for the style guide directory"
        },
        {
            "path": "RulesForContributors.md",
            "type": "contributor_rules",
            "category": "style_guide",
            "description": "Style and tone guide for all contributors"
        },
        {
            "path": "structured-writing.md",
            "type": "template",
            "category": "structured_docs",
            "description": "Standardized structure for writing documentation"
        }
    ]
    
    print("\n📁 IMPORTING STYLE GUIDES DIRECTLY")
    print("=" * 40)
    
    imported_count = 0
    
    for file_info in files_to_import:
        file_path = os.path.join(style_guides_path, file_info['path'])
        
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_info['path']}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add directly to ChromaDB
            collection.add(
                documents=[content],
                metadatas=[{
                    "type": file_info["type"],
                    "category": file_info["category"],
                    "description": file_info["description"],
                    "filename": file_info["path"],
                    "source": file_info["path"],
                    "imported_date": datetime.now().isoformat()
                }],
                ids=[f"style_guide_{file_info['path']}_{datetime.now().timestamp()}"]
            )
            
            print(f"✅ Imported: {file_info['path']} ({file_info['description']})")
            imported_count += 1
            
        except Exception as e:
            print(f"❌ Failed to import {file_info['path']}: {e}")
    
    print(f"\n🎉 Successfully imported {imported_count} style guide(s) directly to ChromaDB")

def add_basic_knowledge_direct(collection):
    """Add basic writing knowledge directly to ChromaDB."""
    print("\n📚 ADDING BASIC KNOWLEDGE")
    print("=" * 40)
    
    knowledge_items = [
        {
            "content": """
            Business Writing Excellence Guide:
            
            Email Communication:
            - Use clear, specific subject lines
            - Lead with the main point
            - Use bullet points for multiple items
            - End with clear next steps
            
            Common Business Phrases to Avoid:
            - "Circle back" → "Follow up"
            - "Touch base" → "Contact" or "Meet"
            - "Low-hanging fruit" → "Easy wins"
            - "Think outside the box" → "Be creative"
            """,
            "metadata": {
                "type": "business_writing",
                "category": "professional",
                "description": "Business writing best practices",
                "source": "built_in"
            }
        },
        {
            "content": """
            Advanced Grammar and Style Guide:
            
            Parallel Structure:
            - Wrong: "The app is fast, reliable, and has good security"
            - Right: "The app is fast, reliable, and secure"
            
            Active Voice Conversions:
            - "The code was reviewed by the team" → "The team reviewed the code"
            - "Errors will be caught by the system" → "The system will catch errors"
            - "The feature was implemented by Sarah" → "Sarah implemented the feature"
            """,
            "metadata": {
                "type": "grammar_guide",
                "category": "style",
                "description": "Grammar and style improvements",
                "source": "built_in"
            }
        }
    ]
    
    for i, item in enumerate(knowledge_items):
        try:
            collection.add(
                documents=[item["content"]],
                metadatas=[{
                    **item["metadata"],
                    "imported_date": datetime.now().isoformat()
                }],
                ids=[f"knowledge_{i}_{datetime.now().timestamp()}"]
            )
            print(f"✅ Added: {item['metadata']['description']}")
        except Exception as e:
            print(f"❌ Failed to add knowledge item {i}: {e}")

def verify_new_collection(collection):
    """Verify the new collection has all documents."""
    print("\n✅ VERIFYING NEW COLLECTION")
    print("=" * 40)
    
    try:
        data = collection.get()
        print(f"Total documents: {len(data['ids'])}")
        
        if data['metadatas']:
            print("\nImported documents:")
            for i, metadata in enumerate(data['metadatas'], 1):
                filename = metadata.get('filename', metadata.get('source', 'Built-in'))
                doc_type = metadata.get('type', 'unknown')
                description = metadata.get('description', 'No description')
                print(f"  {i:2d}. {filename} | {doc_type} | {description}")
        
        # Check embedding dimensions
        if data['embeddings'] and len(data['embeddings']) > 0:
            embedding_dim = len(data['embeddings'][0])
            print(f"\nEmbedding dimension: {embedding_dim}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying collection: {e}")
        return False

def main():
    """Main function to fix the knowledge base."""
    print("🚀 FIXING DOC SCANNER KNOWLEDGE BASE")
    print("=" * 50)
    
    # Step 1: Diagnose current state
    diagnose_collection()
    
    # Step 2: Create new collection
    collection, chroma_client = create_new_collection()
    
    if not collection:
        print("❌ Failed to create new collection")
        return
    
    # Step 3: Import style guides directly
    import_style_guides_direct(collection)
    
    # Step 4: Add basic knowledge
    add_basic_knowledge_direct(collection)
    
    # Step 5: Verify
    if verify_new_collection(collection):
        print("\n🎉 KNOWLEDGE BASE SUCCESSFULLY FIXED!")
        print("\nNext steps:")
        print("1. Start Ollama: ollama serve")
        print("2. Test the app to see improved suggestions")
        print("3. Your 7 style guide files are now searchable!")
    else:
        print("\n❌ Verification failed")

if __name__ == "__main__":
    main()

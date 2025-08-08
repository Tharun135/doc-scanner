"""
Direct knowledge base importer - works even when Ollama is not running
"""

import os
import chromadb
from datetime import datetime
import numpy as np

def add_documents_directly():
    """Add style guide documents directly to ChromaDB"""
    
    # Connect to ChromaDB
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    try:
        collection = chroma_client.get_collection("doc_scanner_knowledge")
    except Exception:
        collection = chroma_client.create_collection("doc_scanner_knowledge")
    
    style_guides_path = "style_guides"
    
    # Map each file to a document type and description
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
    
    imported_count = 0
    
    for file_info in files_to_import:
        file_path = os.path.join(style_guides_path, file_info['path'])
        
        if not os.path.exists(file_path):
            print(f"⚠️  File not found: {file_info['path']}")
            continue
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create a unique ID for this document
            doc_id = f"style_guide_{file_info['path']}_{imported_count}"
            
            # Create metadata
            metadata = {
                "type": file_info["type"],
                "category": file_info["category"],
                "description": file_info["description"],
                "filename": file_info["path"],
                "source": file_info["path"],
                "imported_date": datetime.now().isoformat()
            }
            
            # Add to ChromaDB directly (without embeddings for now)
            collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            print(f"✅ Added directly: {file_info['path']} ({file_info['description']})")
            imported_count += 1
            
        except Exception as e:
            print(f"❌ Failed to add {file_info['path']}: {e}")
    
    print(f"\n🎉 Successfully added {imported_count} documents directly to ChromaDB")
    
    # Check final count
    data = collection.get()
    print(f"📊 Total documents in knowledge base: {len(data['ids'])}")

if __name__ == "__main__":
    add_documents_directly()

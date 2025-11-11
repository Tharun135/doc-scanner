# Upload documents to RAG knowledge base
# Run this script to upload sample documents

import os
import requests

# RAG upload endpoint
RAG_UPLOAD_URL = "http://localhost:5000/rag/api/upload"

# Documents to upload
documents = [
    {
        "path": "data/writing_style_guide.md",
        "type": "style_guide",
        "description": "Technical writing style guidelines and best practices"
    },
    {
        "path": "data/good_examples.md",
        "type": "examples",
        "description": "Examples of good technical writing"
    }
]

print("🚀 Uploading documents to RAG knowledge base...\n")

for doc in documents:
    file_path = doc["path"]
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        continue
    
    print(f"📄 Uploading: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/markdown')}
            data = {
                'document_type': doc['type'],
                'description': doc['description']
            }
            
            response = requests.post(RAG_UPLOAD_URL, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success! Chunks: {result.get('chunks_created', 'N/A')}")
            else:
                print(f"   ❌ Failed: {response.status_code} - {response.text[:100]}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n✨ Upload complete! Check http://localhost:5000/rag/dashboard for stats.")

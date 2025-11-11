"""
Upload documents to RAG using the proper endpoint
"""
import requests
import os

RAG_URL = "http://localhost:5000/rag/upload_knowledge"

documents = [
    "data/writing_style_guide.md",
    "data/good_examples.md"
]

print("🚀 Uploading documents to RAG knowledge base...\n")

for doc_path in documents:
    if not os.path.exists(doc_path):
        print(f"❌ File not found: {doc_path}")
        continue
    
    print(f"📄 Uploading: {doc_path}")
    
    try:
        with open(doc_path, 'rb') as f:
            files = {'files[]': (os.path.basename(doc_path), f, 'text/markdown')}
            data = {
                'chunking_method': 'adaptive',
                'chunk_size': '500'
            }
            
            response = requests.post(RAG_URL, files=files, data=data)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   ✅ Success!")
                    print(f"      Documents: {result.get('documents_processed', 'N/A')}")
                    print(f"      Chunks: {result.get('total_chunks', 'N/A')}")
                except:
                    print(f"   ✅ Upload successful")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"      {response.text[:200]}")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n✨ Upload complete! Checking stats...")

# Check stats
stats_response = requests.get("http://localhost:5000/rag/stats")
if stats_response.status_code == 200:
    stats = stats_response.json()
    print(f"\n📊 RAG Stats:")
    print(f"   Total Documents: {stats.get('total_documents', 0)}")
    print(f"   Total Chunks: {stats.get('stats', {}).get('total_chunks', 0)}")
    print(f"   Status: {stats.get('status', 'unknown')}")

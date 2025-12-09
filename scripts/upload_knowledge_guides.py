"""
Upload comprehensive writing guides to RAG knowledge base
"""
import requests
import os
import glob

RAG_URL = "http://localhost:5000/rag/upload_knowledge"

# Find all knowledge files
knowledge_dir = "data/rag_knowledge"
if not os.path.exists(knowledge_dir):
    print(f"❌ Directory not found: {knowledge_dir}")
    exit(1)

markdown_files = glob.glob(os.path.join(knowledge_dir, "*.md"))

if not markdown_files:
    print(f"❌ No markdown files found in {knowledge_dir}")
    exit(1)

print(f"🚀 Uploading {len(markdown_files)} knowledge guides to RAG...\n")

success_count = 0
failed_count = 0

for file_path in sorted(markdown_files):
    filename = os.path.basename(file_path)
    print(f"📄 Uploading: {filename}")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'files[]': (filename, f, 'text/markdown')}
            data = {
                'chunking_method': 'adaptive',
                'chunk_size': '800'  # Larger chunks for comprehensive guides
            }
            
            response = requests.post(RAG_URL, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    docs_processed = result.get('documents_processed', 'N/A')
                    print(f"   ✅ Success! Documents processed: {docs_processed}")
                    success_count += 1
                except:
                    print(f"   ✅ Upload successful")
                    success_count += 1
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                print(f"      {response.text[:200]}")
                failed_count += 1
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        failed_count += 1

print(f"\n{'='*60}")
print(f"📊 Upload Summary:")
print(f"   ✅ Successful: {success_count}")
print(f"   ❌ Failed: {failed_count}")
print(f"   📁 Total: {len(markdown_files)}")

# Check RAG stats
print(f"\n🔍 Checking RAG stats...")
try:
    stats_response = requests.get("http://localhost:5000/rag/stats", timeout=10)
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"\n📊 RAG Knowledge Base:")
        print(f"   Total Documents: {stats.get('total_documents', 0)}")
        print(f"   Total Chunks: {stats.get('stats', {}).get('total_chunks', 0)}")
        print(f"   Status: {stats.get('status', 'unknown')}")
    else:
        print(f"   ⚠️ Could not fetch stats (HTTP {stats_response.status_code})")
except Exception as e:
    print(f"   ⚠️ Error fetching stats: {e}")

print(f"\n✨ Knowledge base upload complete!")
print(f"\n💡 The AI system now has comprehensive guides for:")
print(f"   - Passive voice conversion (all patterns)")
print(f"   - Long sentence splitting (strategies + examples)")
print(f"   - Adverb removal and style improvement")
print(f"   - Issue-specific optimized prompts")
print(f"\n🎯 AI suggestions will now be more polished and consistent!")

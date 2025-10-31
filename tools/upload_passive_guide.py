#!/usr/bin/env python3
"""Upload the enhanced passive voice guide to RAG system."""

import requests
import os

def upload_passive_voice_guide():
    """Upload the passive voice guide to the RAG knowledge base."""
    
    file_path = "enhanced_passive_voice_guide.json"
    
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found")
        return False
    
    print(f"📁 Uploading {file_path} to RAG knowledge base...")
    
    try:
        with open(file_path, 'rb') as f:
            files = {'files[]': (file_path, f, 'application/json')}
            data = {
                'chunking_method': 'adaptive',
                'chunk_size': '200'  # Smaller chunks for better retrieval
            }
            
            response = requests.post(
                'http://localhost:5000/rag/upload_knowledge',
                files=files,
                data=data
            )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"📊 Documents processed: {result.get('documents_processed', 0)}")
            print(f"📊 Chunks created: {result.get('chunks_created', 0)}")
            return True
        else:
            print(f"❌ Upload failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during upload: {e}")
        return False

def test_rag_search():
    """Test RAG search for passive voice content."""
    try:
        print("\n🔍 Testing RAG search functionality...")
        
        # Test searches
        test_queries = [
            "A data source must be created",
            "passive voice must be active voice",
            "special cases passive voice examples"
        ]
        
        for query in test_queries:
            print(f"\n📝 Testing query: '{query}'")
            try:
                response = requests.post(
                    'http://localhost:5000/analyze_intelligent',
                    json={
                        'text': query,
                        'document_type': 'general'
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print(f"✅ Analysis: {result.get('analysis', 'No analysis')}")
                    else:
                        print(f"❌ Analysis failed: {result.get('error')}")
                else:
                    print(f"❌ Request failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error testing query: {e}")
        
    except Exception as e:
        print(f"❌ Error during RAG search test: {e}")

def check_final_stats():
    """Check final stats after upload."""
    try:
        response = requests.get('http://localhost:5000/rag/stats')
        if response.status_code == 200:
            data = response.json()
            print(f"\n📊 Updated RAG Stats:")
            print(f"Total chunks: {data.get('stats', {}).get('total_chunks', 0)}")
            print(f"Total documents: {data.get('total_documents', 0)}")
        
    except Exception as e:
        print(f"❌ Error checking stats: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced Passive Voice Guide Upload")
    print("=" * 45)
    
    success = upload_passive_voice_guide()
    
    if success:
        check_final_stats()
        test_rag_search()
        print("\n✅ Enhanced passive voice guide upload completed")
    else:
        print("\n❌ Upload failed")
    
    # Cleanup
    try:
        os.remove("enhanced_passive_voice_guide.json")
        print("🧹 Cleaned up test file")
    except:
        pass
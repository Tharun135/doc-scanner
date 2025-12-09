#!/usr/bin/env python3
"""
Test document upload and verify chunk count updates.
"""
import requests
import os
import time

def test_upload_and_stats():
    """Test uploading a document and check if stats update."""
    print("=== Testing Document Upload and Stats Update ===\n")
    
    base_url = "http://localhost:5000"
    
    # 1. Check initial stats
    print("1. Checking initial dashboard stats...")
    try:
        response = requests.get(f"{base_url}/rag/dashboard", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard accessible")
            # You could parse HTML here to extract stats, but let's use the stats API instead
        else:
            print(f"❌ Dashboard not accessible: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error accessing dashboard: {e}")
        return
    
    # 2. Check stats API
    print("\n2. Checking stats API...")
    try:
        response = requests.get(f"{base_url}/rag/stats", timeout=10)
        if response.status_code == 200:
            initial_stats = response.json()
            initial_chunks = initial_stats.get('total_chunks', 0)
            print(f"✅ Initial chunk count: {initial_chunks}")
        else:
            print(f"❌ Stats API not accessible: {response.status_code}")
            initial_chunks = 0
    except Exception as e:
        print(f"❌ Error accessing stats API: {e}")
        initial_chunks = 0
    
    # 3. Upload test document
    print("\n3. Uploading test document...")
    test_file = "test_document.md"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return
    
    try:
        with open(test_file, 'rb') as f:
            files = {'files[]': (test_file, f, 'text/markdown')}
            data = {
                'chunking_method': 'adaptive',
                'chunk_size': '500'
            }
            
            response = requests.post(f"{base_url}/rag/upload_knowledge", 
                                   files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                upload_result = response.json()
                print(f"✅ Upload successful: {upload_result.get('message', 'No message')}")
                chunks_created = upload_result.get('chunks_created', 0)
                print(f"   Chunks created: {chunks_created}")
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return
    
    # 4. Wait a moment for processing
    print("\n4. Waiting for processing...")
    time.sleep(2)
    
    # 5. Check updated stats
    print("\n5. Checking updated stats...")
    try:
        response = requests.get(f"{base_url}/rag/stats", timeout=10)
        if response.status_code == 200:
            updated_stats = response.json()
            updated_chunks = updated_stats.get('total_chunks', 0)
            print(f"✅ Updated chunk count: {updated_chunks}")
            
            if updated_chunks > initial_chunks:
                print(f"🎉 SUCCESS: Chunks increased from {initial_chunks} to {updated_chunks}")
                print(f"   Difference: +{updated_chunks - initial_chunks} chunks")
            else:
                print(f"⚠️  WARNING: Chunks did not increase (still {updated_chunks})")
                
        else:
            print(f"❌ Stats API not accessible: {response.status_code}")
    except Exception as e:
        print(f"❌ Error checking updated stats: {e}")

if __name__ == "__main__":
    test_upload_and_stats()
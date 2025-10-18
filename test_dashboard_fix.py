#!/usr/bin/env python3
"""
Quick test to verify the dashboard loads and upload works.
"""
import requests
import time

def test_dashboard_and_upload():
    """Test dashboard loading and basic upload functionality."""
    print("=== Testing Dashboard and Upload Fix ===\n")
    
    base_url = "http://localhost:5000"
    
    # 1. Test dashboard loads without error
    print("1. Testing dashboard load...")
    try:
        response = requests.get(f"{base_url}/rag/dashboard", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard loads successfully")
            if "AttributeError" in response.text:
                print("❌ AttributeError still present in response")
            else:
                print("✅ No AttributeError detected")
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
    
    # 2. Test upload page loads
    print("\n2. Testing upload page...")
    try:
        response = requests.get(f"{base_url}/rag/upload_knowledge", timeout=10)
        if response.status_code == 200:
            print("✅ Upload page loads successfully")
            if "RAG System Not Available" in response.text:
                print("❌ RAG system still shows as unavailable")
            else:
                print("✅ RAG system shows as available")
        else:
            print(f"❌ Upload page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Upload page error: {e}")
    
    # 3. Test stats endpoint
    print("\n3. Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/rag/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            chunk_count = stats.get('total_chunks', 'N/A')
            print(f"✅ Stats endpoint works - Current chunks: {chunk_count}")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")

if __name__ == "__main__":
    test_dashboard_and_upload()
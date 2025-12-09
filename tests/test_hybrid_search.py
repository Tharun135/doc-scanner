#!/usr/bin/env python3
"""
Test hybrid search functionality and availability.
"""
import requests
import json

def test_hybrid_search():
    """Test hybrid search availability and functionality."""
    print("=== Testing Hybrid Search Availability ===\n")
    
    base_url = "http://localhost:5000"
    
    # 1. Check stats endpoint for hybrid search availability
    print("1. Checking stats endpoint...")
    try:
        response = requests.get(f"{base_url}/rag/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Stats endpoint accessible")
            print(f"   RAG Available: {stats.get('rag_available', 'N/A')}")
            print(f"   ChromaDB Available: {stats.get('chromadb_available', 'N/A')}")
            print(f"   Embeddings Available: {stats.get('embeddings_available', 'N/A')}")
            print(f"   TF-IDF Available: {stats.get('tfidf_available', 'N/A')}")
            print(f"   Hybrid Available: {stats.get('hybrid_available', 'N/A')}")
            print(f"   Search Methods: {stats.get('search_methods', 'N/A')}")
            print(f"   Total Chunks: {stats.get('total_chunks', 'N/A')}")
            
            # Check if hybrid search should be available
            embeddings = stats.get('embeddings_available', False)
            tfidf = stats.get('tfidf_available', False)
            hybrid = stats.get('hybrid_available', False)
            
            if embeddings and tfidf:
                if hybrid:
                    print("🎉 Hybrid search should be AVAILABLE and is correctly detected!")
                else:
                    print("⚠️  Hybrid search should be available but is not detected")
            else:
                print(f"⚠️  Hybrid search requirements not met:")
                print(f"     Embeddings: {embeddings}, TF-IDF: {tfidf}")
                
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Stats check failed: {e}")
    
    # 2. Check dashboard
    print("\n2. Checking dashboard...")
    try:
        response = requests.get(f"{base_url}/rag/dashboard", timeout=10)
        if response.status_code == 200:
            content = response.text
            print("✅ Dashboard accessible")
            
            # Look for hybrid search indicators
            if "Hybrid Search" in content:
                print("✅ Hybrid Search section found in dashboard")
            else:
                print("❌ Hybrid Search section not found in dashboard")
                
            if "Combined" in content:
                print("✅ 'Combined' indicator found")
            else:
                print("❌ 'Combined' indicator not found")
                
        else:
            print(f"❌ Dashboard failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dashboard check failed: {e}")

if __name__ == "__main__":
    test_hybrid_search()
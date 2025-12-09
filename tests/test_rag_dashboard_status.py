#!/usr/bin/env python3
"""
Test RAG Dashboard Status via HTTP
Checks if the RAG dashboard is properly reporting availability.
"""

import requests
import json

def test_rag_dashboard():
    """Test the RAG dashboard endpoint."""
    try:
        # Test the dashboard page
        response = requests.get('http://127.0.0.1:5000/rag/dashboard', timeout=10)
        print(f"Dashboard page status: {response.status_code}")
        
        if response.status_code == 200:
            # Check if the page contains RAG system indicators
            content = response.text
            if "RAG System Not Available" in content:
                print("❌ Dashboard shows RAG system not available")
                return False
            elif "Upload Knowledge Base Documents" in content:
                print("✅ Dashboard shows RAG system available")
                return True
            else:
                print("⚠️ Dashboard status unclear")
                return False
        else:
            print(f"❌ Dashboard page failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing dashboard: {e}")
        return False

def test_rag_stats():
    """Test the RAG stats endpoint."""
    try:
        response = requests.get('http://127.0.0.1:5000/rag/api/stats', timeout=10)
        print(f"Stats API status: {response.status_code}")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"📊 RAG stats: {json.dumps(stats, indent=2)}")
            
            rag_available = stats.get('rag_available', False)
            if rag_available:
                print("✅ Stats API reports RAG available")
                return True
            else:
                print("❌ Stats API reports RAG not available")
                return False
        else:
            print(f"❌ Stats API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing stats: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing RAG Dashboard Status via HTTP")
    print("=" * 50)
    
    # Test stats API
    stats_success = test_rag_stats()
    
    print("\n" + "=" * 50)
    
    # Test dashboard page
    dashboard_success = test_rag_dashboard()
    
    print("\n" + "=" * 50)
    
    if stats_success and dashboard_success:
        print("🎉 RAG dashboard is fully functional!")
    else:
        print("⚠️ RAG dashboard has issues")
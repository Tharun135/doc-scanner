#!/usr/bin/env python3
"""
Test script to verify the RAG dashboard TypeError fix.
"""

import requests
import sys

def test_rag_dashboard():
    """Test if the RAG dashboard loads without TypeError."""
    print("🧪 Testing RAG Dashboard Fix...")
    
    try:
        # Test the dashboard route
        url = "http://127.0.0.1:5000/rag/"
        print(f"📡 Requesting: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ RAG Dashboard loaded successfully!")
            print(f"📄 Response length: {len(response.text)} characters")
            
            # Check if the response contains expected content
            if "RAG Knowledge Base" in response.text or "dashboard" in response.text.lower():
                print("✅ Dashboard content detected")
            else:
                print("⚠️ Dashboard content not detected (but no error)")
                
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"📝 Response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server might not be running")
        print("💡 Make sure Flask server is running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_rag_stats_api():
    """Test the RAG stats API endpoint."""
    print("\n🧪 Testing RAG Stats API...")
    
    try:
        url = "http://127.0.0.1:5000/rag/stats"
        print(f"📡 Requesting: {url}")
        
        response = requests.get(url, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ RAG Stats API responded successfully!")
            print(f"📊 Stats keys: {list(data.get('stats', {}).keys())}")
            
            # Check for expected default values
            stats = data.get('stats', {})
            if isinstance(stats.get('total_chunks'), (int, float)):
                print("✅ Stats structure looks correct")
                return True
            else:
                print("⚠️ Unexpected stats structure")
                return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Stats API test failed: {e}")
        return False

def main():
    """Run all dashboard tests."""
    print("🚀 RAG Dashboard TypeError Fix Test Suite")
    print("=" * 50)
    
    tests = [
        ("RAG Dashboard Page", test_rag_dashboard),
        ("RAG Stats API", test_rag_stats_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The TypeError fix is working correctly.")
        print("💡 The RAG dashboard should now load without errors.")
    else:
        print(f"\n⚠️ {len(results) - passed} tests failed.")
        print("💡 Check server logs for additional details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
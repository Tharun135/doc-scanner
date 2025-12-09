#!/usr/bin/env python3
"""
Test RAG Dashboard Performance Improvements
Measures load times before and after optimization.
"""

import time
import requests
import sys
import threading

def test_dashboard_performance():
    """Test the RAG dashboard loading performance."""
    print("🧪 Testing RAG Dashboard Performance")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:5000"
    
    def test_endpoint(endpoint, description):
        """Test a single endpoint and measure response time."""
        print(f"\n{description}:")
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            load_time = time.time() - start_time
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code}")
                print(f"   ⏱️  Load time: {load_time:.2f}s")
                print(f"   📄 Content length: {len(response.text)} bytes")
                return load_time
            else:
                print(f"   ❌ Status: {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Connection failed - server not running?")
            return None
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    # Test multiple endpoints
    tests = [
        ("/rag/stats", "RAG Stats API (optimized)"),
        ("/rag/dashboard", "RAG Dashboard (optimized)"),
        ("/rag/", "RAG Main Route"),
    ]
    
    results = {}
    
    # Run tests
    for endpoint, description in tests:
        load_time = test_endpoint(endpoint, description)
        if load_time is not None:
            results[endpoint] = load_time
    
    # Performance summary
    print(f"\n🎯 Performance Summary:")
    print("-" * 30)
    for endpoint, load_time in results.items():
        status = "🚀 Fast" if load_time < 2.0 else "⚡ Good" if load_time < 5.0 else "🐌 Slow"
        print(f"   {endpoint}: {load_time:.2f}s {status}")
    
    if results:
        avg_time = sum(results.values()) / len(results)
        print(f"\n📊 Average load time: {avg_time:.2f}s")
        
        if avg_time < 3.0:
            print("🎉 Excellent performance! Dashboard loads quickly.")
        elif avg_time < 5.0:
            print("✅ Good performance! Dashboard is responsive.")
        else:
            print("⚠️  Performance could be improved.")
    else:
        print("❌ No successful tests - check if server is running")
    
    return results

def load_test_dashboard(concurrent_users=5, requests_per_user=3):
    """Perform a load test with multiple concurrent requests."""
    print(f"\n🔥 Load Testing with {concurrent_users} concurrent users")
    print("-" * 50)
    
    results = []
    threads = []
    
    def user_test(user_id):
        """Simulate a single user making multiple requests."""
        user_results = []
        for i in range(requests_per_user):
            try:
                start_time = time.time()
                response = requests.get("http://127.0.0.1:5000/rag/dashboard", timeout=15)
                load_time = time.time() - start_time
                
                if response.status_code == 200:
                    user_results.append(load_time)
                    print(f"   User {user_id} request {i+1}: {load_time:.2f}s ✅")
                else:
                    print(f"   User {user_id} request {i+1}: Failed ({response.status_code}) ❌")
                    
            except Exception as e:
                print(f"   User {user_id} request {i+1}: Error - {str(e)[:50]}... ❌")
        
        results.extend(user_results)
    
    # Start concurrent users
    start_time = time.time()
    for user_id in range(concurrent_users):
        thread = threading.Thread(target=user_test, args=(user_id + 1,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    
    # Analyze results
    if results:
        avg_response = sum(results) / len(results)
        min_response = min(results)
        max_response = max(results)
        success_rate = len(results) / (concurrent_users * requests_per_user) * 100
        
        print(f"\n📈 Load Test Results:")
        print(f"   Total test time: {total_time:.2f}s")
        print(f"   Successful requests: {len(results)}/{concurrent_users * requests_per_user}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Average response time: {avg_response:.2f}s")
        print(f"   Min response time: {min_response:.2f}s")
        print(f"   Max response time: {max_response:.2f}s")
        
        # Performance rating
        if avg_response < 2.0 and success_rate > 95:
            print("🏆 Excellent load performance!")
        elif avg_response < 5.0 and success_rate > 90:
            print("✅ Good load performance!")
        else:
            print("⚠️  Load performance needs optimization.")
    else:
        print("❌ Load test failed - no successful requests")

def test_cache_effectiveness():
    """Test if caching is working effectively."""
    print(f"\n🧠 Testing Cache Effectiveness")
    print("-" * 30)
    
    endpoint = "http://127.0.0.1:5000/rag/stats"
    
    # First request (cache miss)
    print("First request (cache miss):")
    start_time = time.time()
    response1 = requests.get(endpoint)
    time1 = time.time() - start_time
    print(f"   Time: {time1:.2f}s")
    
    # Second request (should be cached)
    print("Second request (should be cached):")
    start_time = time.time()
    response2 = requests.get(endpoint)
    time2 = time.time() - start_time
    print(f"   Time: {time2:.2f}s")
    
    if response1.status_code == 200 and response2.status_code == 200:
        improvement = ((time1 - time2) / time1) * 100
        print(f"\n📊 Cache Performance:")
        print(f"   First request: {time1:.2f}s")
        print(f"   Second request: {time2:.2f}s")
        print(f"   Improvement: {improvement:.1f}%")
        
        if improvement > 50:
            print("🚀 Excellent caching! Significant speed improvement.")
        elif improvement > 20:
            print("✅ Good caching! Noticeable speed improvement.")
        elif improvement > 0:
            print("📈 Some caching benefit detected.")
        else:
            print("❓ Caching may not be working effectively.")
    else:
        print("❌ Cache test failed - requests unsuccessful")

if __name__ == "__main__":
    print("🚀 RAG Dashboard Performance Test Suite")
    print("=" * 60)
    
    # Basic performance test
    results = test_dashboard_performance()
    
    if results:
        # Cache effectiveness test
        test_cache_effectiveness()
        
        # Load test
        load_test_dashboard(concurrent_users=3, requests_per_user=2)
    else:
        print("\n❌ Skipping additional tests - basic connectivity failed")
        print("💡 Make sure Flask server is running: python run.py")
    
    print("\n" + "=" * 60)
    print("✅ Performance test suite completed!")
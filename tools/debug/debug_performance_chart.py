#!/usr/bin/env python3
"""
Test the performance chart functionality by checking the dashboard response
and verifying the JavaScript behavior.
"""
import requests
import re
import json

def check_dashboard_performance():
    """Check the dashboard and performance chart functionality."""
    print("=== Dashboard Performance Chart Debug ===\n")
    
    # 1. Check dashboard loads
    try:
        response = requests.get("http://localhost:5000/rag/dashboard", timeout=10)
        print(f"✅ Dashboard loads: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check if performance chart elements are present
            if 'id="performanceChart"' in content:
                print("✅ Performance chart canvas element found")
            else:
                print("❌ Performance chart canvas element NOT found")
                
            if 'loadPerformanceChart(' in content:
                print("✅ loadPerformanceChart function found")
            else:
                print("❌ loadPerformanceChart function NOT found")
                
            if 'chartLoading' in content:
                print("✅ Chart loading element found")
            else:
                print("❌ Chart loading element NOT found")
                
            # Check auto-load call
            if "loadPerformanceChart('7d')" in content:
                print("✅ Auto-load call found")
            else:
                print("❌ Auto-load call NOT found")
                
        else:
            print(f"❌ Dashboard error: {response.text}")
            
    except Exception as e:
        print(f"❌ Dashboard request failed: {e}")
    
    print()
    
    # 2. Test performance data endpoints
    periods = ['7d', '30d', '90d']
    for period in periods:
        try:
            response = requests.get(f"http://localhost:5000/rag/performance_data?period={period}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Performance data ({period}): {len(data.get('labels', []))} data points")
            else:
                print(f"❌ Performance data ({period}) failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Performance data ({period}) error: {e}")
    
    print()
    
    # 3. Check for common JavaScript issues
    print("=== Potential Issues ===")
    
    # CORS issues
    try:
        response = requests.options("http://localhost:5000/rag/performance_data", timeout=5)
        print(f"✅ CORS preflight: {response.status_code}")
    except Exception as e:
        print(f"❌ CORS preflight failed: {e}")
    
    # Response time
    import time
    start_time = time.time()
    try:
        response = requests.get("http://localhost:5000/rag/performance_data?period=7d", timeout=10)
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        print(f"✅ Response time: {response_time:.2f}ms")
        
        if response_time > 5000:
            print("⚠️  Slow response - might cause timeout in browser")
            
    except Exception as e:
        print(f"❌ Response time test failed: {e}")

if __name__ == "__main__":
    check_dashboard_performance()
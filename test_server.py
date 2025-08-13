#!/usr/bin/env python3
"""
Simple server test
"""

import requests
import time

def test_server():
    """Test if the server is responding"""
    
    url = 'http://127.0.0.1:5000'
    
    try:
        print("Testing server...")
        response = requests.get(url, timeout=5)
        print(f"Server responded with status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Server is running correctly!")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Server connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    # Wait a moment for server to be ready
    time.sleep(2)
    test_server()

#!/usr/bin/env python3

import requests
import time

def test_routes():
    base_url = "http://127.0.0.1:5000"
    
    # Test main route
    try:
        response = requests.get(f"{base_url}/")
        print(f"Main route (/): Status {response.status_code}")
    except Exception as e:
        print(f"Main route error: {e}")
    
    # Test fresh route
    try:
        response = requests.get(f"{base_url}/fresh")
        print(f"Fresh route (/fresh): Status {response.status_code}")
        if response.status_code == 200:
            content = response.text
            if "FRESH PROGRESS DISPLAY" in content:
                print("✅ Fresh route contains expected content!")
            else:
                print("❌ Fresh route missing expected content")
        else:
            print(f"❌ Fresh route failed: {response.text}")
    except Exception as e:
        print(f"Fresh route error: {e}")

if __name__ == "__main__":
    print("Testing Flask routes...")
    test_routes()

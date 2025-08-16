#!/usr/bin/env python3
"""
Final comprehensive test to verify the web interface integration
"""
import requests
import time
import sys
import subprocess
import threading
import os

def start_server():
    """Start the Flask server in background"""
    try:
        process = subprocess.Popen([
            sys.executable, "run.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return process
    except Exception as e:
        print(f"Failed to start server: {e}")
        return None

def test_web_interface():
    """Test the web interface after server is running"""
    print("Testing web interface...")
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test document with clear issues
        test_content = "this is a test. microsoft should be capitalized. The test should work properly."
        
        files = {'file': ('test.txt', test_content, 'text/plain')}
        response = requests.post('http://127.0.0.1:5000/upload', files=files, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            sentences = data.get('sentences', [])
            total_issues = sum(len(s.get('feedback', [])) for s in sentences)
            
            print(f"Sentences processed: {len(sentences)}")
            print(f"Total issues found: {total_issues}")
            
            if total_issues > 0:
                print("✅ SUCCESS: Issues are being detected by web interface!")
                for i, sentence in enumerate(sentences):
                    if sentence.get('feedback'):
                        print(f"  Sentence {i+1}: {len(sentence['feedback'])} issues")
                        for issue in sentence['feedback']:
                            print(f"    - {issue.get('category', 'Unknown')}: {issue.get('message', 'No message')}")
                return True
            else:
                print("❌ FAILED: No issues detected in web interface")
                print("Response:", data)
                return False
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print("Response:", response.text)
            return False
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    print("Starting comprehensive web interface test...")
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Failed to start server")
        return False
    
    try:
        # Test the interface
        success = test_web_interface()
        
        if success:
            print("\n🎉 COMPATIBILITY CONFIRMED: New rules format works with web interface!")
        else:
            print("\n💔 COMPATIBILITY ISSUE: New rules format not working with web interface")
            
        return success
        
    finally:
        # Stop server
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

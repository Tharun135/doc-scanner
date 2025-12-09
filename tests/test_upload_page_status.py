#!/usr/bin/env python3
"""
Simple test to verify RAG availability and upload page functionality
"""

import os
import sys
import requests

def test_upload_page():
    """Test the upload knowledge page"""
    try:
        # Test the upload page endpoint
        response = requests.get('http://127.0.0.1:5001/rag/upload_knowledge', timeout=10)
        
        if response.status_code == 200:
            print("✅ Upload page is accessible")
            
            # Check if RAG is available by looking at page content
            if "RAG System Not Available" in response.text:
                print("❌ RAG system shows as not available on upload page")
                print("   This indicates the RAG_AVAILABLE flag is False")
                return False
            elif "Add documents to enhance" in response.text:
                print("✅ RAG system shows as available on upload page")
                return True
            else:
                print("⚠️ Upload page content unclear")
                return False
        else:
            print(f"❌ Upload page not accessible: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to Flask app: {e}")
        print("   Make sure the Flask app is running on http://127.0.0.1:5000")
        return False

def test_rag_dashboard():
    """Test the RAG dashboard"""
    try:
        response = requests.get('http://127.0.0.1:5001/rag/dashboard', timeout=10)
        
        if response.status_code == 200:
            print("✅ RAG dashboard is accessible")
            return True
        else:
            print(f"❌ RAG dashboard not accessible: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to RAG dashboard: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing RAG upload page functionality...")
    print()
    
    # Test dashboard first
    dashboard_ok = test_rag_dashboard()
    print()
    
    # Test upload page
    upload_ok = test_upload_page()
    print()
    
    if dashboard_ok and upload_ok:
        print("✅ All tests passed! RAG system should be working correctly.")
    else:
        print("❌ Some tests failed. Check the issues above.")
        
    print("\n💡 If RAG shows as 'not available', the Flask app needs to be restarted")
    print("   to properly set the RAG_AVAILABLE flag after our recent fixes.")
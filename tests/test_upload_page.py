#!/usr/bin/env python3
"""
Test the upload knowledge page to verify RAG availability.
"""
import requests
import re

def test_upload_page():
    """Test the upload knowledge page."""
    print("=== Testing Upload Knowledge Page ===\n")
    
    try:
        response = requests.get("http://localhost:5000/rag/upload_knowledge", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check for RAG availability messages
            if "RAG System Not Available" in content:
                print("❌ Upload page shows RAG system NOT available")
                print("   Still displaying dependency warning")
                
                # Extract the warning message for details
                if "pip install chromadb sentence-transformers scikit-learn" in content:
                    print("   Shows installation command")
                    
            elif "Upload Knowledge Base Documents" in content and "Add documents to enhance" in content:
                print("✅ Upload page shows RAG system IS available")
                print("   Ready to accept document uploads")
                
                # Check for upload form elements
                if 'type="file"' in content:
                    print("✅ File upload form present")
                else:
                    print("❌ File upload form missing")
                    
                if "chunking_method" in content:
                    print("✅ Chunking options present")
                else:
                    print("❌ Chunking options missing")
                    
                if "supported_formats" in content:
                    print("✅ Supported formats information present")
                else:
                    print("❌ Supported formats information missing")
                    
            else:
                print("⚠️  Upload page loaded but content unclear")
                
        else:
            print(f"❌ Upload page failed to load: {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - is it running?")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_upload_page()
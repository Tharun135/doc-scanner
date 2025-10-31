#!/usr/bin/env python3
"""
Test RAG Document Upload Functionality
Checks if document upload is working correctly.
"""

import requests
import json
import os
import tempfile

def create_test_document():
    """Create a test document for upload."""
    test_content = """
# Test Document for RAG System

This is a test document to verify the RAG upload functionality.

## Key Points:
- Document processing verification
- RAG system testing
- Upload functionality check

## Content:
This document contains sample text that can be indexed by the RAG system.
It includes multiple paragraphs to test chunking strategies.

The RAG system should be able to:
1. Process this document
2. Create embeddings
3. Store in vector database
4. Enable semantic search

This is sufficient content for testing purposes.
"""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(test_content)
        return f.name

def test_upload_page():
    """Test if the upload page is accessible."""
    try:
        response = requests.get('http://127.0.0.1:5000/rag/upload_knowledge', timeout=10)
        print(f"Upload page status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if "rag_available=False" in content or "RAG system dependencies not available" in content:
                print("❌ Upload page shows RAG not available")
                return False
            elif "Drag & drop files here" in content or "upload" in content.lower():
                print("✅ Upload page is accessible and functional")
                return True
            else:
                print("⚠️ Upload page status unclear")
                return False
        else:
            print(f"❌ Upload page failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing upload page: {e}")
        return False

def test_upload_functionality():
    """Test actual file upload functionality."""
    try:
        # Create test document
        test_file_path = create_test_document()
        print(f"Created test document: {test_file_path}")
        
        # Prepare upload
        url = 'http://127.0.0.1:5000/rag/upload_knowledge'
        
        with open(test_file_path, 'rb') as f:
            files = {'files[]': ('test_document.md', f, 'text/markdown')}
            data = {
                'chunking_method': 'adaptive',
                'chunk_size': '500'
            }
            
            print("Attempting to upload test document...")
            response = requests.post(url, files=files, data=data, timeout=30)
            
        # Clean up
        os.unlink(test_file_path)
        
        print(f"Upload response status: {response.status_code}")
        print(f"Upload response: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                if "success" in result or "processed" in result:
                    print("✅ Document upload successful!")
                    return True
                else:
                    print("⚠️ Upload completed but with issues")
                    return False
            except:
                if "success" in response.text.lower():
                    print("✅ Document upload successful!")
                    return True
                else:
                    print("⚠️ Upload response unclear")
                    return False
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing upload: {e}")
        return False

def test_supported_formats():
    """Check what file formats are supported."""
    try:
        response = requests.get('http://127.0.0.1:5000/rag/api/stats', timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"📄 Supported formats: {stats.get('supported_formats', 'Unknown')}")
            return True
        else:
            print("⚠️ Could not retrieve supported formats")
            return False
    except Exception as e:
        print(f"❌ Error checking formats: {e}")
        return False

def check_upload_directory():
    """Check if upload directory exists and is writable."""
    try:
        # Check common upload directories
        possible_dirs = [
            './uploads',
            './app/uploads', 
            './data',
            './knowledge_base'
        ]
        
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                print(f"✅ Found directory: {dir_path}")
                if os.access(dir_path, os.W_OK):
                    print(f"✅ Directory is writable: {dir_path}")
                else:
                    print(f"⚠️ Directory not writable: {dir_path}")
            else:
                print(f"📁 Directory does not exist: {dir_path}")
        
        return True
    except Exception as e:
        print(f"❌ Error checking directories: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing RAG Document Upload Functionality")
    print("=" * 60)
    
    # Test 1: Check upload page accessibility
    print("\n1. Testing upload page accessibility...")
    page_ok = test_upload_page()
    
    # Test 2: Check supported formats
    print("\n2. Checking supported formats...")
    formats_ok = test_supported_formats()
    
    # Test 3: Check upload directories
    print("\n3. Checking upload directories...")
    dirs_ok = check_upload_directory()
    
    # Test 4: Test actual upload functionality
    print("\n4. Testing actual file upload...")
    upload_ok = test_upload_functionality()
    
    print("\n" + "=" * 60)
    print("📋 Test Results Summary:")
    print(f"   Upload Page: {'✅' if page_ok else '❌'}")
    print(f"   Formats Check: {'✅' if formats_ok else '❌'}")
    print(f"   Directories: {'✅' if dirs_ok else '❌'}")
    print(f"   Upload Function: {'✅' if upload_ok else '❌'}")
    
    if all([page_ok, upload_ok]):
        print("\n🎉 Upload functionality is working correctly!")
        print("💡 If you're having issues, try:")
        print("   1. Ensure files are in supported formats")
        print("   2. Check file size (should be reasonable)")
        print("   3. Try different browsers")
        print("   4. Check browser console for JavaScript errors")
    else:
        print("\n⚠️ Upload functionality has issues")
        print("🔧 Try the troubleshooting steps below")
#!/usr/bin/env python3
"""
Test RAG Dependencies Installation
Verifies that all RAG system dependencies are working correctly.
"""

import sys
import traceback

def test_import(module_name, description):
    """Test importing a module."""
    try:
        __import__(module_name)
        print(f"✅ {description}: Successfully imported {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description}: Failed to import {module_name} - {e}")
        return False
    except Exception as e:
        print(f"⚠️ {description}: Error importing {module_name} - {e}")
        return False

def test_chromadb():
    """Test ChromaDB functionality."""
    try:
        import chromadb
        print(f"✅ ChromaDB version: {chromadb.__version__}")
        
        # Test creating a client
        client = chromadb.Client()
        print("✅ ChromaDB client created successfully")
        
        # Test creating a collection
        collection = client.create_collection("test_collection")
        print("✅ ChromaDB collection created successfully")
        
        # Clean up
        client.delete_collection("test_collection")
        print("✅ ChromaDB test completed successfully")
        return True
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return False

def test_sentence_transformers():
    """Test Sentence Transformers functionality."""
    try:
        from sentence_transformers import SentenceTransformer
        
        # Test loading a small model
        print("🔄 Loading sentence transformer model (this may take a moment)...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ Sentence transformer model loaded successfully")
        
        # Test encoding
        test_sentences = ["This is a test sentence.", "This is another test."]
        embeddings = model.encode(test_sentences)
        print(f"✅ Generated embeddings with shape: {embeddings.shape}")
        return True
    except Exception as e:
        print(f"❌ Sentence Transformers test failed: {e}")
        return False

def test_sklearn():
    """Test scikit-learn functionality."""
    try:
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np
        
        # Test cosine similarity calculation
        vectors = np.array([[1, 2, 3], [4, 5, 6]])
        similarity = cosine_similarity(vectors)
        print(f"✅ Sklearn cosine similarity test passed: {similarity.shape}")
        return True
    except Exception as e:
        print(f"❌ Sklearn test failed: {e}")
        return False

def main():
    """Run all dependency tests."""
    print("🧪 Testing RAG System Dependencies")
    print("=" * 50)
    
    # Core dependencies
    results = []
    
    # Test basic imports
    results.append(test_import("chromadb", "ChromaDB"))
    results.append(test_import("sentence_transformers", "Sentence Transformers"))
    results.append(test_import("sklearn", "Scikit-learn"))
    
    print("\n" + "=" * 50)
    print("🔬 Running Functionality Tests")
    
    # Test functionality
    if results[0]:  # ChromaDB imported successfully
        results.append(test_chromadb())
    
    if results[1]:  # Sentence Transformers imported successfully
        results.append(test_sentence_transformers())
    
    if results[2]:  # Sklearn imported successfully
        results.append(test_sklearn())
    
    print("\n" + "=" * 50)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("✅ RAG system dependencies are fully functional!")
        print("\n📋 Next steps:")
        print("   1. Restart your Flask application")
        print("   2. The RAG dashboard should now have full vector search capabilities")
        print("   3. You can now upload documents for semantic search")
    else:
        print(f"⚠️ Some tests failed: {passed}/{total} passed")
        if passed >= 3:  # Basic imports work
            print("🔄 Basic functionality is available, but some advanced features may not work")
        else:
            print("❌ Critical dependencies are missing")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
# test_fastapi_setup.py
"""
Quick test script to verify FastAPI setup is working.
Run this after installation to validate everything is configured correctly.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required packages can be imported."""
    print("🔍 Testing imports...")
    
    try:
        import fastapi
        print("  ✅ fastapi")
    except ImportError as e:
        print(f"  ❌ fastapi: {e}")
        return False
    
    try:
        import chromadb
        print("  ✅ chromadb")
    except ImportError as e:
        print(f"  ❌ chromadb: {e}")
        return False
    
    try:
        import sentence_transformers
        print("  ✅ sentence_transformers")
    except ImportError as e:
        print(f"  ❌ sentence_transformers: {e}")
        return False
    
    try:
        import nltk
        print("  ✅ nltk")
        
        # Check for punkt data
        try:
            nltk.data.find('tokenizers/punkt')
            print("  ✅ nltk punkt data")
        except LookupError:
            print("  ⚠️  nltk punkt data missing - run: python -c \"import nltk; nltk.download('punkt')\"")
    except ImportError as e:
        print(f"  ❌ nltk: {e}")
        return False
    
    try:
        from pydantic import BaseModel
        print("  ✅ pydantic")
    except ImportError as e:
        print(f"  ❌ pydantic: {e}")
        return False
    
    return True


def test_embeddings():
    """Test embedding generation."""
    print("\n🔍 Testing embeddings...")
    
    try:
        from fastapi_app.services.embeddings import EmbeddingModel
        
        embedder = EmbeddingModel()
        print(f"  ✅ Model loaded: {embedder.model_name}")
        
        # Test single embedding
        test_text = "This is a test sentence."
        embedding = embedder.embed_query(test_text)
        
        print(f"  ✅ Generated embedding with dimension: {len(embedding)}")
        
        # Test batch embeddings
        test_texts = ["First sentence.", "Second sentence.", "Third sentence."]
        embeddings = embedder.embed_texts(test_texts)
        
        print(f"  ✅ Generated {len(embeddings)} batch embeddings")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Embedding test failed: {e}")
        return False


def test_vector_store():
    """Test vector store operations."""
    print("\n🔍 Testing vector store...")
    
    try:
        from fastapi_app.services.vector_store import ChromaManager
        from fastapi_app.services.embeddings import EmbeddingModel
        
        # Use a test directory
        test_dir = "./test_chroma_db"
        store = ChromaManager(persist_directory=test_dir, collection_name="test_collection")
        print(f"  ✅ Vector store initialized: {test_dir}")
        
        embedder = EmbeddingModel()
        
        # Add test data
        texts = [
            "Use active voice for clear writing.",
            "Passive voice should be avoided in technical documents.",
            "Keep sentences short and simple."
        ]
        embeddings = embedder.embed_texts(texts)
        ids = [f"test_{i}" for i in range(len(texts))]
        metadatas = [{"source": "test", "chunk_id": i, "type": "test"} for i in range(len(texts))]
        
        store.add_chunks(ids, texts, embeddings, metadatas)
        print(f"  ✅ Added {len(texts)} test chunks")
        
        # Query
        query_text = "How to write clearly?"
        query_emb = embedder.embed_query(query_text)
        results = store.query(query_emb, top_k=2)
        
        print(f"  ✅ Query returned {len(results['documents'])} results")
        
        if results['documents']:
            top_result = results['documents'][0]
            score = results['distances'][0]
            print(f"  ✅ Top result: '{top_result[:50]}...' (score: {score:.3f})")
        
        # Cleanup (Windows-safe)
        import shutil
        import time
        if os.path.exists(test_dir):
            try:
                # Close any open connections
                store.client = None
                store.collection = None
                time.sleep(0.5)  # Give Windows time to release file handles
                shutil.rmtree(test_dir)
                print(f"  ✅ Cleaned up test directory")
            except Exception as e:
                print(f"  ⚠️  Could not cleanup test directory (OK): {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Vector store test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parser():
    """Test document parser."""
    print("\n🔍 Testing document parser...")
    
    try:
        from fastapi_app.services.parser import DocumentParser
        
        parser = DocumentParser(chunk_size=100, chunk_overlap=20)
        print("  ✅ Parser initialized")
        
        # Test text chunking
        test_text = """
        This is the first sentence. This is the second sentence. 
        This is the third sentence. This is the fourth sentence.
        This is the fifth sentence. This is the sixth sentence.
        """
        
        chunks = parser.chunk_text(test_text)
        print(f"  ✅ Created {len(chunks)} chunks from test text")
        
        if chunks:
            print(f"  ✅ First chunk: {chunks[0]['text'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Parser test failed: {e}")
        return False


def test_api_startup():
    """Test that the FastAPI app can be created."""
    print("\n🔍 Testing FastAPI app...")
    
    try:
        from fastapi_app.main import app
        print("  ✅ FastAPI app created successfully")
        
        # Check routes
        routes = [route.path for route in app.routes]
        print(f"  ✅ Registered {len(routes)} routes")
        
        expected_routes = ["/health", "/upload", "/query", "/analyze"]
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"  ✅ {route} route registered")
            else:
                print(f"  ⚠️  {route} route missing")
        
        return True
        
    except Exception as e:
        print(f"  ❌ FastAPI app test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 FastAPI Setup Validation")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Embeddings", test_embeddings()))
    results.append(("Vector Store", test_vector_store()))
    results.append(("Parser", test_parser()))
    results.append(("FastAPI App", test_api_startup()))
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:12} {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 60)
    if all_passed:
        print("✅ All tests passed! Your FastAPI setup is ready.")
        print("\nNext steps:")
        print("  1. Run: python run_fastapi.py")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Start uploading documents!")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - pip install -r fastapi_requirements.txt")
        print("  - python -c \"import nltk; nltk.download('punkt')\"")
        print("  - Check your .env file configuration")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

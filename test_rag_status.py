#!/usr/bin/env python3
"""
Test RAG System Status
Checks if the RAG system is properly initialized in the Flask application.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_rag_imports():
    """Test the RAG module imports."""
    print("Testing RAG module imports...")
    
    try:
        # Test core dependencies
        import chromadb
        print("✅ ChromaDB imported successfully")
        
        from sentence_transformers import SentenceTransformer
        print("✅ SentenceTransformer imported successfully")
        
        # Test application modules
        from app.rag_routes import RAG_AVAILABLE
        print(f"📊 RAG_AVAILABLE status: {RAG_AVAILABLE}")
        
        if RAG_AVAILABLE:
            print("🎉 RAG system is available in the application!")
            return True
        else:
            print("⚠️ RAG system is not available in the application")
            return False
            
    except Exception as e:
        print(f"❌ Error testing imports: {e}")
        return False

def test_rag_routes():
    """Test the RAG routes functionality."""
    try:
        from app.rag_routes import rag
        print("✅ RAG blueprint imported successfully")
        
        # Test stats endpoint logic
        from app.rag_routes import get_stats
        stats = get_stats()
        print(f"📈 RAG stats: {stats}")
        
        return stats.get('rag_available', False)
        
    except Exception as e:
        print(f"❌ Error testing RAG routes: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing RAG System Status")
    print("=" * 50)
    
    # Test imports
    import_success = test_rag_imports()
    
    print("\n" + "=" * 50)
    
    # Test routes
    route_success = test_rag_routes()
    
    print("\n" + "=" * 50)
    
    if import_success and route_success:
        print("🎉 RAG system is fully functional!")
    else:
        print("⚠️ RAG system has issues")
        
    print(f"\nFinal status: imports={import_success}, routes={route_success}")
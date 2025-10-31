#!/usr/bin/env python3
"""
Test core document processing functionality without RAG dependencies.
This tests the spaCy E088 fix directly on document processing.
"""

import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_document_processing_directly():
    """Test document processing without RAG system dependencies."""
    
    print("🧪 Testing Core Document Processing (No RAG)")
    print("=" * 50)
    
    try:
        # Test 1: Import and use data_ingestion directly
        from data_ingestion import DocumentLoader
        print("✅ Successfully imported DocumentLoader")
        
        # Create a test document
        test_content = """
        This is a very large test document with many vague terms like excellent performance.
        
        This sentence is extremely long and contains numerous words that might trigger the long sentence detector because it has many clauses and could potentially be flagged for being too verbose and difficult to read which was causing the spaCy E088 error before our fix.
        
        This document tests the spaCy processing without RAG dependencies.
        """ * 500  # Make it large enough to test spaCy limits
        
        print(f"📄 Created test document: {len(test_content):,} characters")
        
        # Test document processing
        loader = DocumentLoader()
        
        # Simulate file processing
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_content)
            temp_file = f.name
        
        try:
            # This should work with our spaCy fixes
            document = loader.load_single_document(temp_file)
            print(f"✅ Successfully processed document")
            
            if document:
                content_size = len(document['content'])
                print(f"   Document content size: {content_size} characters")
                
        finally:
            os.unlink(temp_file)
        
        # Test 2: Test rule processing with large text
        print("\n🧪 Testing Rules Processing...")
        
        # Test vague terms (this was causing E088 error)
        from rules.vague_terms import check as check_vague
        vague_suggestions = check_vague(test_content)
        print(f"✅ Vague terms rule processed: {len(vague_suggestions)} suggestions")
        
        # Test long sentences
        from rules.long_sentence import check as check_long
        long_suggestions = check_long(test_content)
        print(f"✅ Long sentence rule processed: {len(long_suggestions)} suggestions")
        
        return True
        
    except Exception as e:
        if "E088" in str(e) or "exceeds maximum" in str(e):
            print(f"❌ FAILED: spaCy E088 error still occurring: {e}")
        else:
            print(f"❌ FAILED: Other error: {e}")
        return False

if __name__ == "__main__":
    success = test_document_processing_directly()
    
    if success:
        print(f"\n🎉 CORE PROCESSING WORKS!")
        print(f"✅ The spaCy E088 fix is working for document processing")
        print(f"✅ File processing functionality is ready")
        print(f"")
        print(f"💡 The '0 docs' issue is likely due to RAG dependencies.")
        print(f"   To enable full upload functionality, install:")
        print(f"   pip install chromadb sentence-transformers scikit-learn")
    
    sys.exit(0 if success else 1)
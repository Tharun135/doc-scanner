#!/usr/bin/env python3
"""
Check documents in the RAG vector database
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def check_vector_database():
    """Check what documents are stored in the vector database"""
    print("🔍 Checking RAG vector database contents...")
    
    try:
        # Import required modules
        import chromadb
        from app.advanced_retrieval import AdvancedRetriever
        
        print("✅ Successfully imported required modules")
        
        # Initialize the retriever to connect to existing database
        retriever = AdvancedRetriever()
        print("✅ Connected to vector database")
        
        # Get collection statistics
        stats = retriever.get_collection_stats()
        print(f"\n📊 Collection Statistics:")
        print(f"  • Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  • Documents count: {stats.get('documents_count', 0)}")
        print(f"  • ChromaDB available: {stats.get('chromadb_available', False)}")
        print(f"  • Embeddings available: {stats.get('embeddings_available', False)}")
        print(f"  • TF-IDF available: {stats.get('tfidf_available', False)}")
        
        # Try to get the collection directly to examine documents
        print(f"\n📋 Examining ChromaDB collection...")
        
        # Get the collection from the retriever
        if hasattr(retriever, 'collection') and retriever.collection:
            collection = retriever.collection
            
            # Get all documents with their metadata (fix the include parameter)
            try:
                # Query to get all documents (with a large limit)
                results = collection.get(
                    include=['documents', 'metadatas']
                )
                
                if results and results.get('documents'):
                    total_docs = len(results['documents'])
                    print(f"  • Found {total_docs} document chunks")
                    
                    # Analyze unique source files
                    source_files = set()
                    chunk_info = []
                    
                    documents = results['documents']
                    metadatas = results.get('metadatas', [{}] * len(documents))
                    
                    for i, (document, metadata) in enumerate(zip(documents, metadatas)):
                        if metadata:
                            source = metadata.get('source', 'Unknown')
                            source_files.add(source)
                            
                            # Show first few characters of document content
                            preview = document[:100] + "..." if len(document) > 100 else document
                            chunk_info.append({
                                'id': f"chunk_{i}",
                                'source': source,
                                'preview': preview,
                                'length': len(document)
                            })
                    
                    print(f"\n📁 Unique source files ({len(source_files)}):")
                    for source in sorted(source_files):
                        print(f"  • {source}")
                    
                    print(f"\n📄 Document chunks (first 10):")
                    for i, chunk in enumerate(chunk_info[:10]):
                        print(f"  {i+1}. ID: {chunk['id']}")
                        print(f"     Source: {chunk['source']}")
                        print(f"     Length: {chunk['length']} chars")
                        print(f"     Preview: {chunk['preview']}")
                        print()
                    
                    if len(chunk_info) > 10:
                        print(f"  ... and {len(chunk_info) - 10} more chunks")
                        
                else:
                    print("  • No documents found in the collection")
                    
            except Exception as e:
                print(f"  ❌ Error querying collection: {e}")
                
                # Try alternative method to get collection info
                try:
                    collection_info = collection.peek()
                    print(f"  📊 Collection peek: {len(collection_info.get('documents', []))} documents")
                    
                    # Try to get count
                    count = collection.count()
                    print(f"  📊 Collection count: {count}")
                    
                except Exception as e2:
                    print(f"  ❌ Error getting collection info: {e2}")
                    
        else:
            print("  ❌ Could not access collection")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this in the virtual environment with RAG dependencies")
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()

def search_sample_query():
    """Test search functionality with a sample query"""
    print(f"\n🔍 Testing search functionality...")
    
    try:
        from app.advanced_retrieval import AdvancedRetriever
        
        retriever = AdvancedRetriever()
        
        # Test search with a common term
        test_queries = [
            "network configuration",
            "security settings", 
            "performance optimization",
            "protocol settings"
        ]
        
        for query in test_queries:
            print(f"\n📍 Searching for: '{query}'")
            try:
                results = retriever.search(query, method='hybrid', n_results=3)
                
                if results:
                    print(f"  ✅ Found {len(results)} results:")
                    for i, result in enumerate(results):
                        score = result.get('relevance_score', 0)
                        content = result.get('content', '')[:100] + "..."
                        print(f"    {i+1}. Score: {score:.3f} | {content}")
                else:
                    print(f"  ❌ No results found")
                    
            except Exception as e:
                print(f"  ❌ Search error: {e}")
                
    except Exception as e:
        print(f"❌ Search test error: {e}")

def test_upload_functionality():
    """Test if we can upload a document to the RAG system"""
    print("\n🧪 Testing document upload functionality...")
    
    try:
        from app.advanced_retrieval import AdvancedRetriever
        from app.chunking_strategies import Chunk, TextChunker
        import uuid
        
        # Create a sample document to test
        sample_doc = """
        This is a test document for the RAG knowledge base.
        
        It contains information about document processing and vector storage.
        
        The system should be able to process this text, create embeddings,
        and store it in the ChromaDB vector database for retrieval.
        
        This test helps verify that the upload and storage functionality
        is working correctly in the doc-scanner application.
        
        Additional content includes details about chunking strategies,
        embedding generation, and hybrid retrieval methods.
        """
        
        # Create a mock document structure
        test_document = {
            'id': str(uuid.uuid4()),
            'content': sample_doc,
            'filename': 'test_document.txt',
            'file_type': 'text',
            'word_count': len(sample_doc.split()),
            'char_count': len(sample_doc),
            'metadata': {
                'source': 'test_document.txt',
                'type': 'test',
                'uploaded_at': '2024-01-01T00:00:00Z'
            }
        }
        
        # Create chunks using the TextChunker
        chunker = TextChunker(default_chunk_size=200, overlap_size=20)
        chunks = chunker.chunk_document(test_document, method="fixed")
        
        print(f"📝 Created {len(chunks)} chunks from test document")
        
        # Initialize retriever and add chunks
        retriever = AdvancedRetriever()
        result = retriever.index_chunks(chunks)
        
        print(f"✅ Successfully indexed chunks: {result}")
        
        # Check if the document was added
        stats = retriever.get_collection_stats()
        print(f"\n📊 Updated statistics:")
        print(f"  • Total chunks: {stats.get('total_chunks', 0)}")
        print(f"  • Documents count: {stats.get('documents_count', 0)}")
        
        # Try a test search using the available retrieval methods
        print(f"\n🔍 Testing retrieval functionality...")
        
        # Test embedding-based retrieval
        try:
            embedding_results = retriever.retrieve_embedding("test document", n_results=3)
            print(f"   Embedding search: Found {len(embedding_results)} results")
            for i, result in enumerate(embedding_results[:2]):
                print(f"   {i+1}. Score: {result.relevance_score:.3f}")
                print(f"      Preview: {result.content[:100]}...")
        except Exception as e:
            print(f"   ❌ Embedding search error: {e}")
        
        # Test keyword-based retrieval
        try:
            keyword_results = retriever.retrieve_keyword("document processing", n_results=3)
            print(f"   Keyword search: Found {len(keyword_results)} results")
            for i, result in enumerate(keyword_results[:2]):
                print(f"   {i+1}. Score: {result.relevance_score:.3f}")
                print(f"      Preview: {result.content[:100]}...")
        except Exception as e:
            print(f"   ❌ Keyword search error: {e}")
        
        # Test hybrid retrieval
        try:
            hybrid_results = retriever.retrieve_hybrid("storage functionality", n_results=3)
            print(f"   Hybrid search: Found {len(hybrid_results)} results")
            for i, result in enumerate(hybrid_results[:2]):
                print(f"   {i+1}. Score: {result.relevance_score:.3f}")
                print(f"      Preview: {result.content[:100]}...")
        except Exception as e:
            print(f"   ❌ Hybrid search error: {e}")
            
    except Exception as e:
        print(f"❌ Error testing upload: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    check_vector_database()
    test_upload_functionality()
    search_sample_query()
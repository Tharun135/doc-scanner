#!/usr/bin/env python3
"""
Explore ChromaDB Contents
Shows what writing rules and documents are stored in the RAG system's vector database.
"""

import sys
import os
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from scripts.docscanner_ollama_rag import DocScannerOllamaRAG
    RAG_AVAILABLE = True
except ImportError as e:
    print(f"❌ Could not import RAG system: {e}")
    RAG_AVAILABLE = False

def explore_chromadb():
    """Explore the contents of ChromaDB in the RAG system."""
    print("🔍 Exploring ChromaDB Contents")
    print("=" * 50)
    
    if not RAG_AVAILABLE:
        print("❌ RAG system not available - cannot explore ChromaDB")
        return
    
    try:
        print("🚀 Initializing DocScanner RAG system...")
        rag_system = DocScannerOllamaRAG()
        
        if not rag_system.is_initialized:
            print("⚠️  RAG system not initialized (likely due to missing Ollama or llama-index)")
            print("📊 ChromaDB Status: Not available")
            return
        
        print("✅ RAG system initialized successfully!")
        
        # Access the ChromaDB collection
        collection = rag_system.collection if hasattr(rag_system, 'collection') else None
        
        if collection:
            print(f"📚 ChromaDB Collection: {collection.name}")
            
            # Get collection count
            try:
                count = collection.count()
                print(f"📊 Total documents in ChromaDB: {count}")
                
                if count > 0:
                    print(f"\n📝 Exploring collection contents...")
                    
                    # Get all documents (with limit to avoid overwhelming output)
                    try:
                        # Get documents with their metadata
                        results = collection.get(
                            limit=min(count, 20),  # Limit to first 20 documents
                            include=['documents', 'metadatas', 'embeddings']
                        )
                        
                        documents = results.get('documents', [])
                        metadatas = results.get('metadatas', [])
                        embeddings = results.get('embeddings', [])
                        
                        print(f"📋 Retrieved {len(documents)} documents:")
                        print("-" * 40)
                        
                        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
                            print(f"📄 Document {i+1}:")
                            print(f"   Content: {doc[:200]}..." if len(doc) > 200 else f"   Content: {doc}")
                            if meta:
                                print(f"   Metadata: {meta}")
                            if embeddings and i < len(embeddings):
                                embedding_info = embeddings[i]
                                if embedding_info:
                                    print(f"   Embedding: Vector of length {len(embedding_info)}")
                            print()
                            
                    except Exception as e:
                        print(f"⚠️  Could not retrieve documents: {e}")
                        
                        # Try alternative method
                        try:
                            # Just get basic info
                            print("🔍 Trying alternative method...")
                            basic_results = collection.get(limit=5)
                            if basic_results:
                                print(f"✅ Collection accessible - contains data")
                                if 'documents' in basic_results:
                                    docs = basic_results['documents']
                                    print(f"📝 Sample documents: {len(docs)} found")
                                    for i, doc in enumerate(docs[:3]):
                                        print(f"   {i+1}. {doc[:100]}...")
                            else:
                                print("⚠️  Collection appears empty")
                        except Exception as e2:
                            print(f"⚠️  Alternative method also failed: {e2}")
                else:
                    print("📭 ChromaDB collection is empty")
                    
            except Exception as e:
                print(f"⚠️  Could not get collection count: {e}")
        else:
            print("❌ ChromaDB collection not accessible")
            
        # Try to explore the vector store index
        if hasattr(rag_system, 'index') and rag_system.index:
            print(f"\n🔍 Vector Store Index Information:")
            try:
                # Get some basic info about the index
                print(f"✅ Index exists and is accessible")
                
                # Try a sample query to see what's in there
                query_engine = rag_system.index.as_query_engine(similarity_top_k=3)
                sample_query = "What writing rules are available?"
                
                print(f"🔍 Testing with sample query: '{sample_query}'")
                response = query_engine.query(sample_query)
                
                print(f"📝 Sample Response: {str(response)[:300]}...")
                
                # Show source documents if available
                if hasattr(response, 'source_nodes') and response.source_nodes:
                    print(f"📚 Source Documents Found: {len(response.source_nodes)}")
                    for i, node in enumerate(response.source_nodes[:3]):
                        print(f"   Source {i+1}: {node.text[:100]}...")
                        
            except Exception as e:
                print(f"⚠️  Could not query index: {e}")
        else:
            print("❌ Vector Store Index not available")
            
    except Exception as e:
        print(f"❌ Error exploring ChromaDB: {e}")
        import traceback
        traceback.print_exc()

def show_rag_knowledge_sources():
    """Show what sources the RAG system loads its knowledge from."""
    print("\n📚 RAG Knowledge Sources")
    print("=" * 50)
    
    # Look for rule files that get loaded
    rules_dir = os.path.join(os.path.dirname(__file__), 'app', 'rules')
    if os.path.exists(rules_dir):
        print(f"📁 Rules Directory: {rules_dir}")
        rule_files = [f for f in os.listdir(rules_dir) if f.endswith('.py')]
        print(f"📋 Rule Files Found: {len(rule_files)}")
        for rule_file in sorted(rule_files):
            print(f"   - {rule_file}")
    else:
        print("❌ Rules directory not found")
    
    # Look for any knowledge base files
    knowledge_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if any(keyword in file.lower() for keyword in ['knowledge', 'rules', 'writing']):
                if file.endswith(('.txt', '.md', '.json', '.py')):
                    knowledge_files.append(os.path.join(root, file))
    
    if knowledge_files:
        print(f"\n📚 Potential Knowledge Sources Found:")
        for kf in sorted(knowledge_files)[:10]:  # Show first 10
            print(f"   - {kf}")
        if len(knowledge_files) > 10:
            print(f"   ... and {len(knowledge_files) - 10} more")
    
if __name__ == "__main__":
    explore_chromadb()
    show_rag_knowledge_sources()

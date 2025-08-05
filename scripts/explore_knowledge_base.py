#!/usr/bin/env python3
"""
Explore the RAG knowledge base contents
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def explore_knowledge_base():
    """Explore what's actually stored in the knowledge base."""
    print("🔍 Exploring RAG Knowledge Base Contents")
    print("=" * 50)
    
    kb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rule_knowledge_base")
    
    try:
        # Import ChromaDB
        try:
            from langchain_chroma import Chroma
        except ImportError:
            from langchain_community.vectorstores import Chroma
        
        # Load the vectorstore
        print("📚 Loading knowledge base...")
        vectorstore = Chroma(persist_directory=kb_path)
        
        # Get collection info
        collection = vectorstore._collection
        if collection:
            count = collection.count()
            print(f"📊 Total documents in knowledge base: {count}")
            
            if count > 0:
                # Get all documents (limited to avoid overwhelming output)
                print(f"\\n📝 Sample documents (showing first 10):") 
                try:
                    # Get documents with limit
                    results = collection.get(limit=10, include=['documents', 'metadatas'])
                    
                    for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                        print(f"\\n{i+1}. Document:")
                        print(f"   Title: {metadata.get('title', 'N/A')}")
                        print(f"   Type: {metadata.get('type', 'N/A')}")
                        print(f"   Tags: {metadata.get('tags', 'N/A')}")
                        print(f"   File: {metadata.get('file_name', 'N/A')}")
                        print(f"   Content: {doc[:200]}..." if len(doc) > 200 else f"   Content: {doc}")
                
                except Exception as e:
                    print(f"   ❌ Error retrieving documents: {e}")
            
            # Show categories/types
            print(f"\\n📋 Document Categories:")
            try:
                all_results = collection.get(include=['metadatas'])
                types = set()
                tags = set()
                
                for metadata in all_results['metadatas']:
                    if 'type' in metadata:
                        types.add(metadata['type'])
                    if 'tags' in metadata:
                        # Split tags string and add individual tags
                        tag_list = [tag.strip() for tag in metadata['tags'].split(',') if tag.strip()]
                        tags.update(tag_list)
                
                print(f"   Types: {list(types)}")
                print(f"   Tags: {sorted(list(tags))[:20]}...")  # Show first 20 tags
                
            except Exception as e:
                print(f"   ❌ Error analyzing categories: {e}")
        
        else:
            print("❌ No collection found")
    
    except Exception as e:
        print(f"❌ Error exploring knowledge base: {e}")
        import traceback
        traceback.print_exc()

def test_sample_queries():
    """Test the knowledge base with sample queries."""
    print(f"\\n🎯 Testing Sample Queries")
    print("=" * 30)
    
    kb_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rule_knowledge_base")
    
    try:
        # Import without embeddings for basic testing
        try:
            from langchain_chroma import Chroma
        except ImportError:
            from langchain_community.vectorstores import Chroma
        
        # Note: We can't do similarity search without embeddings/API key
        # But we can show what queries would be possible
        print("🔍 Available query types (requires API key for actual search):")
        
        sample_queries = [
            "passive voice detection",
            "long sentences readability", 
            "can may modal verbs",
            "UI terminology guidelines",
            "accessibility rules",
            "technical writing standards",
            "grammar corrections",
            "style formatting"
        ]
        
        for query in sample_queries:
            print(f"   • '{query}'")
        
        print(f"\\n💡 To perform actual searches:")
        print("   1. Set GOOGLE_API_KEY environment variable")
        print("   2. Use the app's RAG system with check_with_rag()")
        
    except Exception as e:
        print(f"❌ Error setting up query test: {e}")

if __name__ == "__main__":
    explore_knowledge_base()
    test_sample_queries()

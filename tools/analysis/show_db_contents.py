#!/usr/bin/env python3

from app.advanced_retrieval import AdvancedRetriever

def show_database_contents():
    """Show what's currently in the vector database"""
    print("📊 Current Vector Database Contents:")
    
    retriever = AdvancedRetriever()
    collection = retriever.collection
    
    if collection:
        results = collection.get(include=['documents', 'metadatas'])
        documents = results['documents']
        metadatas = results['metadatas']
        
        print(f"  • Total chunks: {len(documents)}")
        
        # Group by source
        sources = {}
        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
            source = meta.get('source_doc_id', 'Unknown')
            if source not in sources:
                sources[source] = []
            sources[source].append({
                'chunk': i+1, 
                'preview': doc[:80] + '...' if len(doc) > 80 else doc
            })
        
        print(f"  • Unique documents: {len(sources)}")
        for source, chunks in sources.items():
            print(f"    - {source}: {len(chunks)} chunks")
            for chunk in chunks[:2]:  # Show first 2 chunks
                print(f"      {chunk['chunk']}. {chunk['preview']}")
            if len(chunks) > 2:
                print(f"      ... and {len(chunks) - 2} more chunks")
    
    else:
        print("  ❌ No collection found")

if __name__ == "__main__":
    show_database_contents()
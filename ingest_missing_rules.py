#!/usr/bin/env python3
"""
Add missing technical writing rules to the ChromaDB knowledge base.
This fills gaps in the current knowledge base for better RAG performance.
"""

import json
import chromadb
import os
from datetime import datetime

def ingest_missing_rules():
    """Add missing technical writing rules to the knowledge base"""
    
    # Load the missing rules
    with open('missing_technical_writing_rules.json', 'r') as f:
        missing_rules = json.load(f)
    
    print(f"📚 Loading {len(missing_rules)} missing technical writing rules...")
    
    # Connect to ChromaDB
    chroma_path = os.getenv("CHROMA_PATH", "./chroma_db")
    collection_name = os.getenv("DOCSCANNER_SOLUTIONS_COLLECTION", "docscanner_solutions")
    
    client = chromadb.PersistentClient(path=chroma_path)
    
    try:
        collection = client.get_collection(collection_name)
        print(f"✅ Connected to existing collection: {collection_name}")
    except Exception:
        print(f"❌ Collection {collection_name} not found. Creating new collection...")
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "Doc Scanner AI writing rules and solutions"}
        )
    
    # Prepare documents for ingestion
    documents = []
    metadatas = []
    ids = []
    
    for i, rule in enumerate(missing_rules):
        rule_id = rule.get('rule_id', f'MISSING-{i}')
        
        # Create document text combining all rule information
        document_text = f"""
{rule.get('title', 'Technical Writing Rule')}

{rule.get('explanation', '')}

Why:
{rule.get('why', '')}

Examples:
Bad: {', '.join(rule.get('examples', {}).get('bad', []))}
Good: {', '.join(rule.get('examples', {}).get('good', []))}

Solution: {rule.get('solution', '')}
        """.strip()
        
        # Prepare metadata (flatten complex objects to strings)
        rewrite_policy = rule.get('rewrite_policy', {})
        metadata = {
            'rule_id': rule_id,
            'title': rule.get('title', ''),
            'category': 'technical_writing',
            'ingested_date': datetime.now().isoformat(),
            'source': 'missing_rules_update',
            'solution': rule.get('solution', ''),
            'explanation': rule.get('explanation', ''),
            'rewrite_policy': json.dumps(rewrite_policy) if rewrite_policy else ''
        }
        
        documents.append(document_text)
        metadatas.append(metadata)
        ids.append(f"missing_{rule_id}_{i}")
    
    # Add to collection
    try:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"✅ Successfully added {len(documents)} missing rules to knowledge base!")
        
        # Verify the addition
        total_count = collection.count()
        print(f"📊 Total documents in knowledge base: {total_count}")
        
        # Test a few queries to make sure the new rules work
        test_queries = [
            "adverb easily simply",
            "modal verb can may should",
            "click on button",
            "ALL CAPS capitalization"
        ]
        
        print("\n🧪 Testing new rules with sample queries:")
        for query in test_queries:
            results = collection.query(query_texts=[query], n_results=1)
            if results['documents'] and results['documents'][0]:
                doc = results['documents'][0][0]
                meta = results['metadatas'][0][0] if results['metadatas'][0] else {}
                rule_id = meta.get('rule_id', 'unknown')
                print(f"   ✅ '{query}' → {rule_id}: {doc[:60]}...")
            else:
                print(f"   ❌ '{query}' → No match found")
                
    except Exception as e:
        print(f"❌ Failed to add rules to knowledge base: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Adding missing technical writing rules to knowledge base...")
    success = ingest_missing_rules()
    
    if success:
        print("\n🎉 Knowledge base update completed successfully!")
        print("💡 The RAG system should now provide better suggestions for:")
        print("   • Adverb overuse")
        print("   • Modal verb issues") 
        print("   • UI interaction language")
        print("   • Capitalization problems")
        print("   • Hedging language")
        print("   • Filler words")
        print("   • Redundant phrases")
        print("   • And more...")
    else:
        print("❌ Knowledge base update failed!")

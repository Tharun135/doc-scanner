#!/usr/bin/env python3
"""
Ingest comprehensive writing rules to make the KB more resourceful.
This addresses the request: "What can be possible to make the KB more resourceful, to not get any error in suggestion"
"""

import json
import chromadb
from chromadb.config import Settings

def ingest_comprehensive_rules():
    """Ingest comprehensive writing rules into ChromaDB."""
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Get or create the collection
    collection = client.get_or_create_collection(
        name="docscanner_solutions",
        metadata={"description": "Enhanced DocScanner writing solutions"}
    )
    
    # Load the comprehensive rules
    try:
        with open('comprehensive_writing_rules.json', 'r', encoding='utf-8') as f:
            rules = json.load(f)
    except FileNotFoundError:
        print("❌ comprehensive_writing_rules.json not found!")
        return False
    
    print(f"📖 Loading {len(rules)} comprehensive writing rules...")
    
    # Check current collection size
    try:
        current_count = collection.count()
        print(f"📊 Current KB size: {current_count} documents")
    except Exception as e:
        print(f"⚠️ Could not get current count: {e}")
        current_count = 0
    
    # Process each rule
    documents = []
    metadatas = []
    ids = []
    
    for rule in rules:
        rule_id = rule.get('rule_id', 'unknown')
        title = rule.get('title', 'Untitled Rule')
        explanation = rule.get('explanation', '')
        why = rule.get('why', '')
        examples = rule.get('examples', {})
        solution = rule.get('solution', '')
        
        # Create comprehensive document text for vector search
        doc_text = f"""
Title: {title}

Problem: {explanation}

Why it matters: {why}

Solution: {solution}

Bad examples: {', '.join(examples.get('bad', []))}

Good examples: {', '.join(examples.get('good', []))}

Category: Grammar and Style
Type: Writing Enhancement
"""
        
        documents.append(doc_text.strip())
        
        metadatas.append({
            "rule_id": rule_id,
            "title": title,
            "category": "comprehensive_grammar",
            "type": "writing_rule",
            "explanation": explanation,
            "solution": solution
        })
        
        ids.append(f"comprehensive_{rule_id}")
    
    # Add to collection
    try:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        new_count = collection.count()
        added = new_count - current_count
        print(f"✅ Successfully added {added} comprehensive rules")
        print(f"📈 KB now contains {new_count} total documents")
        
        # Test query to verify ingestion
        test_results = collection.query(
            query_texts=["fix passive voice"],
            n_results=3
        )
        
        if test_results['documents'][0]:
            print(f"🔍 Test query successful - found {len(test_results['documents'][0])} results")
            if test_results['metadatas'][0]:
                print(f"📝 Sample result metadata available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding comprehensive rules: {e}")
        return False

def verify_kb_coverage():
    """Verify that the KB now covers common writing issues."""
    
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    
    collection = client.get_collection(name="docscanner_solutions")
    
    # Test queries for previously failing cases
    test_queries = [
        "passive voice",
        "adverbs",
        "modal verbs", 
        "double negatives",
        "comma splices",
        "dangling modifiers",
        "split infinitives"
    ]
    
    print("\n🔍 Testing KB coverage for previously failing cases:")
    
    for query in test_queries:
        try:
            results = collection.query(
                query_texts=[query],
                n_results=2
            )
            
            if results['documents'][0]:
                best_match = results['metadatas'][0][0]['title']
                print(f"✅ {query}: Found '{best_match}'")
            else:
                print(f"❌ {query}: No results found")
                
        except Exception as e:
            print(f"⚠️ {query}: Query error - {e}")

if __name__ == "__main__":
    print("🚀 Ingesting comprehensive writing rules to make KB more resourceful...")
    
    success = ingest_comprehensive_rules()
    
    if success:
        print("\n🎯 KB Enhancement Complete!")
        verify_kb_coverage()
        print("\n💡 The KB is now much more resourceful and should handle all common writing issues!")
    else:
        print("\n❌ KB enhancement failed!")

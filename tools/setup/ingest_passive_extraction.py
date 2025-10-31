#!/usr/bin/env python3
"""
Ingest passive voice extraction rules into the knowledge base.
"""

import json
import chromadb

def ingest_passive_voice_extraction_rules():
    """Add comprehensive passive voice extraction rules to KB."""
    
    print("🔍 INGESTING PASSIVE VOICE EXTRACTION RULES")
    print("=" * 45)
    
    # Connect to ChromaDB
    CHROMA_PATH = "./chroma_db"
    COLLECTION_NAME = "docscanner_solutions"
    
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    try:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"✅ Connected to existing collection: {COLLECTION_NAME}")
    except Exception:
        print(f"❌ Collection not found: {COLLECTION_NAME}")
        return
    
    # Load the new rules
    try:
        with open('passive_voice_extraction_rules.json', 'r') as f:
            data = json.load(f)
        
        extraction_rules = data['extraction_guidance_rules']
        print(f"✅ Loaded {len(extraction_rules)} extraction rules")
    except Exception as e:
        print(f"❌ Error loading rules: {e}")
        return
    
    # Add each rule to the knowledge base
    added_count = 0
    
    for rule in extraction_rules:
        try:
            # Create comprehensive document content
            document_content = f"""
Title: {rule['title']}

Description: {rule['description']}

Content:
{rule['content']}

Category: {rule['category']}
Priority: {rule['priority']}
Rule ID: {rule['rule_id']}
"""
            
            # Add to collection
            collection.add(
                documents=[document_content],
                metadatas=[{
                    'rule_id': rule['rule_id'],
                    'title': rule['title'],
                    'category': rule['category'],
                    'priority': rule['priority'],
                    'type': 'extraction_guidance'
                }],
                ids=[f"extraction_{rule['rule_id']}"]
            )
            
            added_count += 1
            print(f"✅ Added: {rule['rule_id']} - {rule['title']}")
            
        except Exception as e:
            print(f"❌ Error adding {rule['rule_id']}: {e}")
    
    print(f"\n📊 INGESTION SUMMARY:")
    print(f"   Total rules processed: {len(extraction_rules)}")
    print(f"   Successfully added: {added_count}")
    print(f"   KB enhancement complete!")
    
    return added_count

def verify_kb_enhancement():
    """Verify that the new rules are accessible via queries."""
    
    print(f"\n🔍 VERIFYING KB ENHANCEMENT")
    print("=" * 30)
    
    from app.services.enrichment import _cached_vector_query
    
    # Test queries that should now return better results
    test_queries = [
        "passive voice extraction patterns",
        "active voice conversion format", 
        "response format guidelines passive voice",
        "common passive constructions"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        
        results = _cached_vector_query(query, n_results=3)
        
        if results and results.get('documents') and results['documents'][0]:
            print(f"   ✅ Found {len(results['documents'][0])} results")
            
            for i, (doc, meta) in enumerate(zip(
                results['documents'][0][:2],
                results['metadatas'][0][:2] if results.get('metadatas') else [{}]*2
            )):
                rule_id = meta.get('rule_id', 'unknown')
                title = meta.get('title', 'Unknown')
                print(f"     {i+1}. {rule_id}: {title}")
                
        else:
            print(f"   ❌ No results found")
    
    return True

def test_improved_extraction():
    """Test if the KB enhancement improves extraction."""
    
    print(f"\n🎯 TESTING IMPROVED EXTRACTION")
    print("=" * 35)
    
    import requests
    
    test_cases = [
        {
            "name": "File Upload Test",
            "feedback": "passive voice detected by rule",
            "sentence": "The file was uploaded by the user."
        },
        {
            "name": "System Configuration Test",
            "feedback": "passive voice detected by rule",
            "sentence": "The system can be configured by administrators."
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 {test_case['name']}:")
        print(f"   Input: '{test_case['sentence']}'")
        
        try:
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json={
                    'feedback': test_case['feedback'],
                    'sentence': test_case['sentence']
                },
                timeout=25
            )
            
            if response.status_code == 200:
                result = response.json()
                method = result.get('method', 'unknown')
                ai_answer = result.get('ai_answer', '')
                suggestion = result.get('suggestion', '')
                sources = result.get('sources', [])
                
                print(f"   Method: {method}")
                print(f"   AI Answer: \"{ai_answer[:100]}...\"")
                print(f"   Suggestion: \"{suggestion[:100]}...\"")
                print(f"   Sources: {len(sources)}")
                
                # Check if extraction improved
                if 'Active Voice:' in ai_answer:
                    print(f"   ✅ AI using improved format!")
                elif suggestion != test_case['sentence'] and len(suggestion) > 20:
                    print(f"   ✅ Meaningful extraction achieved")
                else:
                    print(f"   ⚠️ Still needs improvement")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    # Step 1: Ingest the new rules
    added = ingest_passive_voice_extraction_rules()
    
    if added and added > 0:
        # Step 2: Verify they're accessible 
        verify_kb_enhancement()
        
        # Step 3: Test improved extraction
        test_improved_extraction()
        
        print(f"\n🎉 KB ENHANCEMENT COMPLETE!")
        print(f"   The knowledge base now contains comprehensive")
        print(f"   passive voice extraction guidance that should")
        print(f"   improve AI response formatting and extraction.")
    else:
        print(f"\n❌ KB enhancement failed - no rules were added")

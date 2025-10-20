#!/usr/bin/env python3
"""
Search for the specific passive voice conversion for "must be created"
"""

import chromadb
import json
from pathlib import Path

def find_must_be_created_conversion():
    print("🔍 Finding 'must be created' conversion pattern")
    print("=" * 50)
    
    try:
        # Connect to ChromaDB
        db_path = Path("./chroma_db")
        client = chromadb.PersistentClient(path=str(db_path))
        collection = client.get_collection("docscanner_knowledge")
        
        # Search for "special_cases" content
        results = collection.query(
            query_texts=["special_cases data source must be created"],
            n_results=5
        )
        
        print("📄 Found results:")
        for i, doc in enumerate(results['documents'][0]):
            print(f"\nResult {i+1}:")
            print("-" * 30)
            print(doc)
            
            # Try to parse as JSON and extract special cases
            try:
                # Look for JSON pattern in the document
                lines = doc.split('\n')
                json_started = False
                json_content = ""
                
                for line in lines:
                    if line.strip().startswith('{'):
                        json_started = True
                    
                    if json_started:
                        json_content += line + '\n'
                        if line.strip().endswith('}') and json_content.count('{') == json_content.count('}'):
                            break
                
                if json_content:
                    json_data = json.loads(json_content)
                    
                    if 'special_cases' in json_data:
                        print("🎯 Found special_cases!")
                        for case in json_data['special_cases']:
                            print(f"   • '{case.get('passive', 'N/A')}' → '{case.get('active', 'N/A')}'")
                            
                            # Check if this is our target pattern
                            passive = case.get('passive', '').strip()
                            active = case.get('active', '').strip()
                            
                            if "data source must be created" in passive.lower():
                                print(f"✅ FOUND TARGET PATTERN!")
                                print(f"   Passive: {passive}")
                                print(f"   Active: {active}")
                    
                    if 'examples' in json_data:
                        print(f"📊 Also found {len(json_data['examples'])} regular examples")
                        
            except Exception as e:
                print(f"   ❌ Could not parse JSON: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_must_be_created_conversion()
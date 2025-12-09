#!/usr/bin/env python3
"""
Final test to verify the enhanced KB is working properly and solving the resourcefulness issue.
"""

import chromadb
from chromadb.config import Settings
import requests
import time
import json

def check_kb_status():
    """Check the current status of the knowledge base."""
    
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(anonymized_telemetry=False)
    )
    
    collection = client.get_collection(name="docscanner_solutions")
    total_docs = collection.count()
    
    print(f"📊 Knowledge Base Status:")
    print(f"   Total Documents: {total_docs}")
    
    # Get sample of document categories
    sample_results = collection.get(limit=10)
    if sample_results['metadatas']:
        categories = {}
        for metadata in sample_results['metadatas']:
            cat = metadata.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"   Categories: {dict(categories)}")
    
    return total_docs

def test_enhanced_ai_suggestions():
    """Test AI suggestions with the enhanced KB."""
    
    # Test cases that were previously failing
    test_cases = [
        {
            "text": "The report was written by the team and it was reviewed by management.",
            "issue": "Passive voice - should be active"
        },
        {
            "text": "You should really carefully configure the settings properly.",
            "issue": "Too many adverbs"
        },
        {
            "text": "You might possibly want to consider maybe updating the software.",
            "issue": "Weak modal verbs"
        },
        {
            "text": "We don't need no additional configuration.",
            "issue": "Double negative"
        },
        {
            "text": "Click Save, the file will be stored automatically.",
            "issue": "Comma splice"
        }
    ]
    
    print("\n🧪 Testing Enhanced AI Suggestions:")
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}/{total_tests}: {test_case['issue']}")
        print(f"   Input: \"{test_case['text']}\"")
        
        try:
            # Make request to AI suggestion endpoint
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json={'feedback': test_case['text']},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if we got a proper AI-enhanced response
                method = result.get('method', 'unknown')
                suggestion = result.get('suggestion', '')
                
                print(f"   ✅ Method: {method}")
                print(f"   💡 Suggestion: \"{suggestion}\"")
                
                if method in ['chromadb_deterministic', 'chromadb_llm'] and suggestion:
                    successful_tests += 1
                    print(f"   🎯 SUCCESS - Enhanced AI suggestion provided!")
                else:
                    print(f"   ⚠️ LIMITED - Got basic response: {method}")
            
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
        
        except requests.exceptions.Timeout:
            print(f"   ⏱️ TIMEOUT - Server took too long")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
        
        # Brief pause between tests
        time.sleep(0.5)
    
    # Summary
    success_rate = (successful_tests / total_tests) * 100
    print(f"\n📊 Test Results Summary:")
    print(f"   Successful AI-enhanced responses: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("   🎉 EXCELLENT - KB is very resourceful!")
    elif success_rate >= 60:
        print("   👍 GOOD - KB is mostly resourceful")  
    else:
        print("   ⚠️ NEEDS IMPROVEMENT - KB needs more resources")
    
    return success_rate

def verify_server_running():
    """Verify the Flask server is running."""
    try:
        response = requests.get('http://localhost:5000', timeout=2)
        return True
    except:
        return False

if __name__ == "__main__":
    print("🔍 Final Verification of Enhanced Knowledge Base")
    print("=" * 50)
    
    # Check KB status
    kb_size = check_kb_status()
    
    # Check if server is running
    if not verify_server_running():
        print("\n⚠️ Flask server not running. Starting server check...")
        print("💡 You may need to run: python run_simple.py")
    else:
        print("\n✅ Flask server is running")
        
        # Test enhanced AI suggestions
        success_rate = test_enhanced_ai_suggestions()
        
        print(f"\n🎯 CONCLUSION:")
        print(f"   Knowledge Base Size: {kb_size} documents (was 23, now {kb_size})")
        print(f"   Enhancement Success Rate: {success_rate:.1f}%")
        
        if kb_size > 30 and success_rate >= 60:
            print("   ✅ KB IS NOW MORE RESOURCEFUL - Should prevent suggestion errors!")
        else:
            print("   ⚠️ KB may need additional enhancements")

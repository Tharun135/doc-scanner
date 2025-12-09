#!/usr/bin/env python3
"""
Test how the current RAG system handles long sentence issues.
"""

import requests
import json

def test_long_sentence_handling():
    """Test various long sentence scenarios."""
    
    print("🔍 Testing Long Sentence Handling in Current RAG System")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Simple Long Sentence",
            "feedback": "long sentence",
            "sentence": "This is a very long sentence that contains multiple clauses and ideas that should probably be broken down into shorter, more manageable pieces for better readability and user comprehension."
        },
        {
            "name": "Run-on Sentence",
            "feedback": "fix run-on sentence", 
            "sentence": "The application starts then loads configuration then connects to database and displays interface and processes user input and generates reports and sends notifications."
        },
        {
            "name": "Complex Long Sentence",
            "feedback": "break up long sentence",
            "sentence": "When you configure the system settings, which include database connections, user permissions, and security protocols, you must ensure that all components are properly validated and tested before deployment."
        },
        {
            "name": "Multiple Clauses",
            "feedback": "sentence too long",
            "sentence": "The user clicks the button, and then the system processes the request, which triggers a validation check, and if successful, the data is saved to the database, and a confirmation message is displayed."
        },
        {
            "name": "Subordinate Clauses",
            "feedback": "long sentence issue",
            "sentence": "Although the system provides multiple configuration options that allow users to customize their experience, it can be overwhelming for new users who are not familiar with the interface."
        }
    ]
    
    print(f"Testing {len(test_cases)} long sentence scenarios...\n")
    
    successful_cases = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 Test {i}: {test_case['name']}")
        print(f"   Feedback: '{test_case['feedback']}'")
        print(f"   Original: \"{test_case['sentence'][:80]}...\"")
        
        try:
            response = requests.post(
                'http://localhost:5000/ai_suggestion',
                json={
                    'feedback': test_case['feedback'],
                    'sentence': test_case['sentence']
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                
                method = result.get('method', 'unknown')
                suggestion = result.get('suggestion', '')
                ai_answer = result.get('ai_answer', '')
                sources = result.get('sources', [])
                
                print(f"   ✅ Status: Success")
                print(f"   🔧 Method: {method}")
                
                # Show AI guidance if available
                if ai_answer and ai_answer.strip():
                    print(f"   💡 AI Guidance: \"{ai_answer[:100]}...\"")
                
                # Show improved sentence if available
                if suggestion and suggestion != "Please provide clearer text.":
                    print(f"   ✏️  Improved: \"{suggestion[:100]}...\"")
                
                # Show source rule if available
                if sources and sources[0].get('rule_id'):
                    rule_id = sources[0]['rule_id']
                    print(f"   📚 Rule Used: {rule_id}")
                
                # Check if it's using RAG (chromadb methods)
                if method.startswith('chromadb'):
                    print(f"   🎯 RAG Active: Yes")
                    successful_cases += 1
                else:
                    print(f"   ⚠️  RAG Active: No (using fallback)")
                    
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()  # Empty line between tests
    
    # Summary
    success_rate = (successful_cases / len(test_cases)) * 100
    
    print("📊 LONG SENTENCE HANDLING RESULTS:")
    print(f"   RAG-Enhanced Cases: {successful_cases}/{len(test_cases)} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("   🎉 EXCELLENT - RAG handles long sentences very well!")
    elif success_rate >= 60:
        print("   👍 GOOD - RAG handles most long sentence cases")
    else:
        print("   ⚠️ NEEDS IMPROVEMENT - Long sentence handling could be better")
    
    return success_rate

def analyze_long_sentence_kb_coverage():
    """Check what long sentence rules exist in the knowledge base."""
    
    print("\n🔍 KNOWLEDGE BASE COVERAGE FOR LONG SENTENCES:")
    print("=" * 55)
    
    # Query the knowledge base for long sentence related rules
    import chromadb
    from chromadb.config import Settings
    
    try:
        client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        collection = client.get_collection(name="docscanner_solutions")
        
        # Search for long sentence related rules
        search_queries = [
            "long sentence",
            "run-on sentence", 
            "break up sentence",
            "sentence length",
            "multiple clauses"
        ]
        
        print("📚 Searching knowledge base for long sentence rules:")
        
        found_rules = set()
        
        for query in search_queries:
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            
            if results['documents'][0]:
                print(f"\n🔍 Query: '{query}'")
                for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
                    rule_id = metadata.get('rule_id', 'unknown')
                    title = metadata.get('title', 'No title')
                    if rule_id not in found_rules:
                        print(f"   ✅ Found: {rule_id} - {title}")
                        found_rules.add(rule_id)
        
        print(f"\n📊 Total unique rules found: {len(found_rules)}")
        
        if found_rules:
            print("   Rules available for long sentence issues:")
            for rule_id in sorted(found_rules):
                print(f"   • {rule_id}")
        else:
            print("   ⚠️ No specific long sentence rules found in KB")
            
    except Exception as e:
        print(f"❌ Error querying knowledge base: {e}")

if __name__ == "__main__":
    # Test the current system
    success_rate = test_long_sentence_handling()
    
    # Analyze KB coverage
    analyze_long_sentence_kb_coverage()
    
    print(f"\n🎯 CONCLUSION:")
    print(f"The current RAG system handles long sentences with {success_rate:.1f}% success rate")
    if success_rate >= 80:
        print("✅ Long sentence handling is working well!")
    else:
        print("⚠️ Long sentence handling could use improvement")

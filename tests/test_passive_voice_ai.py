#!/usr/bin/env python3
"""Test the document-first AI system specifically for passive voice."""

import requests

def test_passive_voice_intelligent_analysis():
    """Test the intelligent analysis for the specific passive voice case."""
    
    print("🧪 Testing Intelligent Analysis for Passive Voice")
    print("=" * 50)
    
    # Test the exact case from the user's report
    test_case = {
        'text': 'A data source must be created.',
        'document_type': 'general',
        'context': 'passive voice conversion'
    }
    
    print(f"📝 Testing sentence: '{test_case['text']}'")
    print("📋 Expected: Should convert to active voice using uploaded knowledge")
    
    try:
        response = requests.post(
            'http://localhost:5000/analyze_intelligent',
            json=test_case
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analysis successful: {result.get('success', False)}")
            print(f"📊 Method: {result.get('method', 'unknown')}")
            print(f"🎯 Confidence: {result.get('confidence', 'unknown')}")
            print(f"💡 Suggestion: {result.get('analysis', 'No suggestion')}")
            print(f"📚 Explanation: {result.get('explanation', 'No explanation')}")
            
            # Check if it actually converted to active voice
            suggestion = result.get('analysis', '')
            if suggestion and suggestion != test_case['text']:
                print("✅ Successfully provided different suggestion")
                if 'you must create' in suggestion.lower() or 'create a data source' in suggestion.lower():
                    print("🎉 PERFECT! Used proper active voice conversion")
                else:
                    print("⚠️ Provided different text but may not be proper active voice conversion")
            else:
                print("❌ No conversion provided - returned same text")
                
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

def test_direct_rag_search():
    """Test direct RAG search for passive voice content."""
    
    print("\n🔍 Testing Direct RAG Search")
    print("=" * 35)
    
    # Test if we can search the knowledge base directly
    test_queries = [
        "must be created passive voice active voice",
        "passive voice detected convert active",
        "data source must be created active",
        "special cases passive voice"
    ]
    
    for query in test_queries:
        print(f"\n📝 Search query: '{query}'")
        try:
            # Use the search endpoint if available, or test via analysis
            response = requests.post(
                'http://localhost:5000/analyze_intelligent',
                json={
                    'text': query,
                    'document_type': 'search_test'
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Result: {result.get('analysis', 'No result')[:100]}...")
            else:
                print(f"   Error: {response.status_code}")
                
        except Exception as e:
            print(f"   Exception: {e}")

if __name__ == "__main__":
    test_passive_voice_intelligent_analysis()
    test_direct_rag_search()
#!/usr/bin/env python3
"""
Test the specific passive voice conversion with detailed debugging
"""

import requests
import json

def test_intelligent_analysis():
    print("🧪 Testing Enhanced Passive Voice Conversion")
    print("=" * 50)
    
    # Test sentence that should match the uploaded pattern
    test_sentence = "A data source must be created."
    
    print(f"📝 Input: '{test_sentence}'")
    print(f"🎯 Expected: 'You must create a data source.'")
    print()
    
    # Call the intelligent analysis endpoint
    try:
        response = requests.post(
            'http://localhost:5000/api/intelligent-analyze',
            json={
                'text': test_sentence,
                'method': 'contextual_rag'
            },
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success', False)}")
            print(f"📊 Method: {result.get('method', 'N/A')}")
            print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
            print(f"💡 Suggestion: {result.get('suggestion', 'N/A')}")
            print(f"📚 Explanation: {result.get('explanation', 'N/A')}")
            
            suggestion = result.get('suggestion', '').strip()
            if suggestion and suggestion != test_sentence:
                print("✅ CONVERSION SUCCESSFUL!")
            else:
                print("❌ NO CONVERSION - returned same text")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_direct_rag_search():
    print("\n🔍 Testing Direct RAG Search")
    print("=" * 30)
    
    # Test direct RAG search
    try:
        response = requests.post(
            'http://localhost:5000/rag/search',
            json={
                'query': 'A data source must be created special cases',
                'method': 'hybrid',
                'top_k': 3
            },
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"📊 Found {len(results.get('results', []))} results")
            
            for i, result in enumerate(results.get('results', [])[:2]):
                print(f"\nResult {i+1}:")
                content = result.get('content', '')[:200]
                print(f"Content: {content}...")
                
                # Look for conversion patterns in the content
                if 'data source must be created' in content.lower():
                    print("✅ Found target pattern in RAG results!")
                    
        else:
            print(f"❌ RAG Search Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ RAG Search failed: {e}")

if __name__ == "__main__":
    test_intelligent_analysis()
    test_direct_rag_search()
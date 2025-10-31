#!/usr/bin/env python3
"""
Test the passive voice conversion using the main analyze endpoint
"""

import requests
import json

def test_main_analyze_endpoint():
    print("🧪 Testing Main Analyze Endpoint for Passive Voice")
    print("=" * 50)
    
    test_sentence = "A data source must be created."
    
    print(f"📝 Input: '{test_sentence}'")
    print(f"🎯 Expected: Should convert using uploaded JSON knowledge")
    print()
    
    # Try the main analyze endpoint
    try:
        response = requests.post(
            'http://localhost:5000/analyze',
            files={'file': ('test.txt', test_sentence.encode('utf-8'), 'text/plain')},
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Look for passive voice issues
            issues = result.get('issues', [])
            print(f"📊 Found {len(issues)} issues")
            
            for i, issue in enumerate(issues):
                print(f"\nIssue {i+1}:")
                print(f"  Type: {issue.get('type', 'N/A')}")
                print(f"  Sentence: {issue.get('sentence', 'N/A')}")
                print(f"  Suggestion: {issue.get('suggestion', 'N/A')}")
                print(f"  Confidence: {issue.get('confidence', 'N/A')}")
                
                # Check if passive voice was detected and converted
                if 'passive' in issue.get('type', '').lower():
                    suggestion = issue.get('suggestion', '').strip()
                    if suggestion and suggestion != test_sentence:
                        print("✅ PASSIVE VOICE CONVERTED!")
                        if "You must create a data source" in suggestion:
                            print("✅ CONVERSION MATCHES UPLOADED KNOWLEDGE!")
                        else:
                            print("⚠️ Conversion doesn't match uploaded pattern")
                    else:
                        print("❌ No conversion provided")
                        
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_main_analyze_endpoint()
#!/usr/bin/env python3
"""
Test the enhanced passive voice patterns
"""

import requests

def test_problematic_sentences():
    print("🧪 Testing Problematic Passive Voice Sentences")
    print("=" * 55)
    
    test_cases = [
        {
            "input": "A data source must be created.",
            "expected": "You must create a data source."
        },
        {
            "input": "The available connectors are shown.",
            "expected": "The system shows the available connectors."
        },
        {
            "input": "The list of available tags is displayed.",
            "expected": "The system displays the list of available tags."
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: '{case['input']}'")
        print(f"🎯 Expected: '{case['expected']}'")
        
        try:
            response = requests.post(
                'http://localhost:5000/analyze_intelligent',
                json={'text': case['input']},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis = result.get('analysis', '').strip()
                
                print(f"💡 Got: '{analysis}'")
                
                # Check if we got raw JSON instead of converted text
                if analysis.startswith('#') or '{' in analysis[:50]:
                    print("❌ ISSUE: Got raw JSON/file content instead of conversion!")
                elif case['expected'] == analysis:
                    print("✅ PERFECT MATCH!")
                elif analysis != case['input']:
                    print("✅ CONVERTED (different than expected)")
                else:
                    print("❌ NO CONVERSION")
                    
                # Show full result structure for debugging
                print(f"📊 Method: {result.get('method', 'N/A')}")
                print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_problematic_sentences()
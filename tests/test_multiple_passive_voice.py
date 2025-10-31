#!/usr/bin/env python3
"""
Test multiple passive voice patterns through the web interface
"""

import requests
import json

def test_multiple_patterns():
    print("🧪 Testing Multiple Passive Voice Patterns")
    print("=" * 50)
    
    test_cases = [
        {
            "input": "A data source must be created.",
            "expected": "You must create a data source."
        },
        {
            "input": "A file must be uploaded.", 
            "expected": "You must upload a file."
        },
        {
            "input": "The task should be completed.",
            "expected": "You should complete the task."
        },
        {
            "input": "The system needs to be configured.",
            "expected": "You need to configure the system."
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
                
                if case['expected'] in analysis or analysis != case['input']:
                    if case['expected'] == analysis:
                        print("✅ PERFECT MATCH!")
                    else:
                        print("✅ CONVERTED (different than expected)")
                else:
                    print("❌ NO CONVERSION")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_multiple_patterns()
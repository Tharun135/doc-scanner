#!/usr/bin/env python3
"""
Test the intelligent analysis endpoint for passive voice conversion
"""

import requests
import json

def test_analyze_intelligent():
    print("🧪 Testing /analyze_intelligent Endpoint")
    print("=" * 45)
    
    test_sentence = "A data source must be created."
    
    print(f"📝 Input: '{test_sentence}'")
    print(f"🎯 Expected: 'You must create a data source.'")
    print()
    
    try:
        # Test the analyze_intelligent endpoint
        response = requests.post(
            'http://localhost:5000/analyze_intelligent',
            json={
                'text': test_sentence
            },
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Success: {result.get('success', False)}")
            
            # Check the analysis results
            if 'analysis' in result:
                analysis = result['analysis']
                print(f"� Analysis Result: {analysis}")
                
                # Check if conversion happened
                if isinstance(analysis, str):
                    if "You must create a data source" in analysis:
                        print("\n� PERFECT! Found expected conversion in analysis!")
                    elif analysis != test_sentence and len(analysis.strip()) > 0:
                        print(f"\n✅ SOME CONVERSION DETECTED: {analysis}")
                    else:
                        print(f"\n❌ NO CONVERSION - Analysis: {analysis}")
                else:
                    # Handle if it's a dict
                    suggestion = analysis.get('suggestion', '') if hasattr(analysis, 'get') else str(analysis)
                    if suggestion and suggestion != test_sentence:
                        print("\n✅ CONVERSION DETECTED!")
                        if "You must create a data source" in suggestion:
                            print("🎉 PERFECT! Matches uploaded JSON pattern!")
                        else:
                            print(f"⚠️ Different conversion: {suggestion}")
                    else:
                        print("\n❌ NO CONVERSION - Same text returned")
            else:
                print(f"📋 Full Response: {json.dumps(result, indent=2)}")
                
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analyze_intelligent()
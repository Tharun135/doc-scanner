#!/usr/bin/env python3
"""
Test the specific failing sentence: "Tags are added to the data source."
"""

import requests

def test_tags_sentence():
    print("🧪 Testing Specific Failing Sentence")
    print("=" * 45)
    
    test_sentence = "Tags are added to the data source."
    expected = "You add tags to the data source."
    
    print(f"📝 Input: '{test_sentence}'")
    print(f"🎯 Expected: '{expected}'")
    print()
    
    try:
        payload = {
            "sentence": test_sentence,
            "feedback": f"Avoid passive voice in sentence: '{test_sentence}'",
            "issue_type": "Passive Voice",
            "document_type": "technical",
            "writing_goals": ["clarity", "directness"],
            "option_number": 1
        }
        
        response = requests.post(
            'http://localhost:5000/ai_suggestion',
            json=payload,
            timeout=30
        )
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            suggestion = result.get('suggestion', '').strip()
            ai_answer = result.get('ai_answer', '').strip()
            method = result.get('method', 'N/A')
            confidence = result.get('confidence', 'N/A')
            
            print(f"💡 Suggestion: '{suggestion}'")
            print(f"🤖 AI Answer: '{ai_answer[:150]}{'...' if len(ai_answer) > 150 else ''}'")
            print(f"📊 Method: {method}")
            print(f"🎯 Confidence: {confidence}")
            
            # Check result
            if expected == suggestion:
                print("\n✅ PERFECT MATCH!")
            elif suggestion != test_sentence:
                print(f"\n✅ CONVERSION SUCCESS! (Different than expected)")
                print(f"   Expected: {expected}")
                print(f"   Got:      {suggestion}")
            else:
                print(f"\n❌ NO CONVERSION - returned original text")
                
            # Also test a few related patterns
            related_tests = [
                "Files are created in the folder.",
                "Settings are configured by the user.", 
                "Data is added to the database."
            ]
            
            print(f"\n🔄 Testing Related Patterns:")
            for related_sentence in related_tests:
                print(f"\n📝 Testing: '{related_sentence}'")
                
                related_payload = payload.copy()
                related_payload["sentence"] = related_sentence
                related_payload["feedback"] = f"Avoid passive voice in sentence: '{related_sentence}'"
                
                related_response = requests.post(
                    'http://localhost:5000/ai_suggestion',
                    json=related_payload,
                    timeout=15
                )
                
                if related_response.status_code == 200:
                    related_result = related_response.json()
                    related_suggestion = related_result.get('suggestion', '').strip()
                    
                    if related_suggestion != related_sentence:
                        print(f"   ✅ Converted: '{related_suggestion}'")
                    else:
                        print(f"   ❌ No conversion")
                else:
                    print(f"   ❌ Error: {related_response.status_code}")
                    
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text[:300]}...")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tags_sentence()
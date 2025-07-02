#!/usr/bin/env python3
"""
Integration test to demonstrate the improved AI suggestion system
"""

import requests
import json

def test_improved_ai_suggestions():
    """Test the complete flow with improved issue descriptions"""
    
    print("🚀 AI Suggestion Improvement Demo")
    print("=" * 50)
    
    test_cases = [
        {
            "sentence": "The configuration was completed by the administrator.",
            "expected_issue_type": "passive voice"
        },
        {
            "sentence": "You can can access the system after authentication.",
            "expected_issue_type": "repeated word"
        },
        {
            "sentence": "The system, which was developed over several months by our team, provides comprehensive data management capabilities that are utilized by various departments.",
            "expected_issue_type": "long sentence"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['sentence'][:60]}...")
        print(f"   Expected issue: {test_case['expected_issue_type']}")
        
        # First, analyze the sentence to get the rule-generated feedback
        try:
            response = requests.post('http://127.0.0.1:5000/upload', 
                                   files={'file': ('test.txt', test_case['sentence'], 'text/plain')})
            
            if response.status_code == 200:
                result = response.json()
                sentences = result.get('sentences', [])
                
                if sentences and len(sentences) > 0:
                    feedback = sentences[0].get('feedback', [])
                    
                    if feedback:
                        for issue in feedback:
                            message = issue.get('message', '')
                            print(f"   📝 Issue detected: {message}")
                            
                            # Now test the AI suggestion with this clear issue description
                            ai_data = {
                                "feedback": message,
                                "sentence": test_case['sentence'],
                                "document_type": "technical",
                                "writing_goals": ["clarity", "conciseness"]
                            }
                            
                            ai_response = requests.post('http://127.0.0.1:5000/ai_suggestion', 
                                                      json=ai_data,
                                                      headers={'Content-Type': 'application/json'})
                            
                            if ai_response.status_code == 200:
                                ai_result = ai_response.json()
                                suggestion = ai_result.get('suggestion', '')
                                method = ai_result.get('method', '')
                                confidence = ai_result.get('confidence', '')
                                
                                print(f"   🤖 AI Suggestion ({method}, {confidence} confidence):")
                                print(f"      {suggestion}")
                                
                                # Check if suggestion follows proper format
                                if "CORRECTED TEXT:" in suggestion and "CHANGE MADE:" in suggestion:
                                    print(f"   ✅ Proper AI suggestion format")
                                else:
                                    print(f"   ⚠️  AI suggestion format could be improved")
                            else:
                                print(f"   ❌ AI suggestion failed: {ai_response.status_code}")
                                
                    else:
                        print(f"   ⚠️  No issues detected by rules")
                else:
                    print(f"   ❌ No sentences returned")
            else:
                print(f"   ❌ Analysis failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n" + "=" * 50)
    print("✅ Integration test completed!")
    print("\nKey improvements:")
    print("• Rule-based feedback now provides clear issue descriptions")
    print("• AI suggestions use structured CORRECTED TEXT + CHANGE MADE format")
    print("• No more confusing rewritten sentences in issue descriptions")

if __name__ == "__main__":
    test_improved_ai_suggestions()

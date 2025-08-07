#!/usr/bin/env python3
"""
Test the AI suggestion response structure
"""
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

try:
    from ai_improvement import get_enhanced_ai_suggestion
    
    def test_response_structure():
        """Test that the AI suggestion returns proper structure."""
        
        print("🔍 Testing AI Suggestion Response Structure")
        print("=" * 60)
        
        test_cases = [
            {
                "feedback": "Convert to active voice: 'The Docker daemon does not generate logs when no applications are running.'",
                "sentence": "Docker logs are not generated when there are no active applications.",
                "name": "Passive Voice"
            },
            {
                "feedback": "Sentence too long - break into shorter parts",
                "sentence": "You can configure the Modbus TCP Connector to the field devices to consume the acquired data in the IED for value creation by using the Common Configurator.",
                "name": "Long Sentence"
            },
            {
                "feedback": "Avoid first person pronouns",
                "sentence": "We recommend using this approach for better results.",
                "name": "First Person"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case['name']}")
            print(f"Feedback: {test_case['feedback']}")
            print(f"Sentence: {test_case['sentence']}")
            print("-" * 40)
            
            try:
                result = get_enhanced_ai_suggestion(
                    feedback_text=test_case['feedback'],
                    sentence_context=test_case['sentence'],
                    document_type="technical",
                    writing_goals=['clarity', 'conciseness']
                )
                
                print(f"Result type: {type(result)}")
                print(f"Result is dict: {isinstance(result, dict)}")
                
                if isinstance(result, dict):
                    print(f"Keys: {list(result.keys())}")
                    print(f"Has 'suggestion': {'suggestion' in result}")
                    
                    if 'suggestion' in result:
                        suggestion = result['suggestion']
                        print(f"Suggestion type: {type(suggestion)}")
                        print(f"Suggestion exists: {bool(suggestion)}")
                        print(f"Suggestion length: {len(str(suggestion)) if suggestion else 0}")
                        print(f"First 100 chars: {str(suggestion)[:100]}...")
                        
                        # Check if all expected fields exist
                        expected_fields = ['suggestion', 'confidence', 'method']
                        for field in expected_fields:
                            exists = field in result
                            value = result.get(field, 'N/A')
                            print(f"  {field}: {exists} ({value})")
                        
                        print("✅ VALID: Response structure is correct")
                    else:
                        print("❌ INVALID: Missing 'suggestion' key")
                else:
                    print(f"❌ INVALID: Expected dict, got {type(result)}")
                    print(f"Raw result: {result}")
                    
            except Exception as e:
                print(f"❌ ERROR: {e}")
                import traceback
                traceback.print_exc()

    if __name__ == "__main__":
        test_response_structure()
        
except Exception as e:
    print(f"❌ Import Error: {e}")
    import traceback
    traceback.print_exc()

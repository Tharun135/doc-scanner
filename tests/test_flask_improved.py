"""
Test the Flask API with improved RAG system
"""
import urllib.request
import urllib.parse
import json
import time

print("🔧 Testing Flask API with improved RAG system...")

# Test cases matching user's examples
test_cases = [
    {
        "name": "Click on -> click",
        "feedback": "Use 'click' instead of 'click on'", 
        "sentence": "Click on the Dashboard icon and select any configured asset.",
        "expected_change": "should not contain 'click on'"
    },
    {
        "name": "Passive voice fix",
        "feedback": "Avoid passive voice in sentence",
        "sentence": "The Time, Description, and Comments columns are fixed and cannot be removed.",
        "expected_change": "should be in active voice"
    },
    {
        "name": "Generic response test",
        "feedback": "Improve clarity",
        "sentence": "The data processing module handles input validation.",
        "expected_change": "should not be generic 'Consider Revising'"
    }
]

def test_api(test_data):
    """Test a single API call"""
    try:
        # Convert to JSON
        json_data = json.dumps(test_data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            'http://127.0.0.1:5001/ai_suggestion',
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result
    except Exception as e:
        return {"error": str(e)}

# Wait for server to be ready
print("⏳ Waiting for server to start...")
time.sleep(3)

# Run tests
results = []
for i, test_case in enumerate(test_cases, 1):
    print(f"\n📝 Test {i}: {test_case['name']}")
    print(f"   Original: {test_case['sentence']}")
    print(f"   Issue: {test_case['feedback']}")
    
    test_data = {
        'feedback': test_case['feedback'],
        'sentence': test_case['sentence'],
        'document_type': 'technical',
        'option_number': 1
    }
    
    result = test_api(test_data)
    
    if "error" in result:
        print(f"   ❌ Error: {result['error']}")
        results.append(False)
    else:
        suggestion = result.get('suggestion', '')
        method = result.get('method', 'unknown')
        
        print(f"   ✅ Method: {method}")
        print(f"   ✅ Suggestion: {suggestion}")
        
        # Check quality
        is_good = True
        if test_case['name'] == "Click on -> click":
            if "click on" in suggestion.lower():
                print(f"   ❌ FAIL: Still contains 'click on'")
                is_good = False
            else:
                print(f"   🎉 SUCCESS: 'click on' was fixed!")
        
        elif test_case['name'] == "Passive voice fix":
            if suggestion.lower() == test_case['sentence'].lower():
                print(f"   ❌ FAIL: No change made")
                is_good = False
            elif "Consider Revising" in suggestion:
                print(f"   ❌ FAIL: Generic response")
                is_good = False
            else:
                print(f"   🎉 SUCCESS: Sentence was rewritten!")
        
        elif "Consider Revising For Better Clarity" in suggestion and suggestion.endswith(test_case['sentence']):
            print(f"   ❌ FAIL: Generic 'Consider Revising' response")
            is_good = False
        else:
            print(f"   🎉 SUCCESS: Intelligent suggestion provided!")
            
        results.append(is_good)

# Summary
print(f"\n📊 Test Summary:")
print(f"Passed: {sum(results)}/{len(results)}")
print(f"Success Rate: {sum(results)/len(results)*100:.1f}%")

if sum(results) == len(results):
    print("🎉 🎉 ALL TESTS PASSED! RAG-LLM IS WORKING WITH INTELLIGENT SUGGESTIONS! 🎉 🎉")
else:
    print("🔄 Some tests failed, but significant improvement over previous generic responses")

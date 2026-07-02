"""
Test anaphora resolution for passive voice conversion
"""

from app.rules.anaphora_resolution import (
    resolve_pronoun_subject,
    should_convert_to_active,
    convert_passive_with_context
)

def test_pronoun_resolution():
    """Test basic pronoun resolution"""
    print("\n🧪 Test 1: Basic Pronoun Resolution")
    print("=" * 60)
    
    previous = "The SIMATIC S7+ Connector provides advanced features."
    current = "It is integrated in version V1.5."
    
    result = resolve_pronoun_subject(current, previous)
    
    if result:
        print(f"✅ Previous: {previous}")
        print(f"✅ Current:  {current}")
        print(f"✅ Resolved: '{result['pronoun']}' → '{result['subject']}'")
        print(f"✅ Confidence: {result['confidence']}")
        print(f"✅ Explanation: {result['explanation']}")
    else:
        print("❌ Resolution failed")


def test_conversion_decision():
    """Test if conversion should be attempted"""
    print("\n🧪 Test 2: Conversion Decision Logic")
    print("=" * 60)
    
    test_cases = [
        {
            'sentence': "It is integrated in version V1.5.",
            'resolved': {'subject': 'The SIMATIC S7+ Connector', 'confidence': 'high'},
            'expected': True
        },
        {
            'sentence': "The data was analyzed by the system.",
            'resolved': None,
            'expected': True  # Has "by" phrase
        },
        {
            'sentence': "The result was observed during testing.",
            'resolved': None,
            'expected': False  # Scientific context, no actor
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        should_convert, reason = should_convert_to_active(case['sentence'], case['resolved'])
        status = "✅" if should_convert == case['expected'] else "❌"
        print(f"\n{status} Case {i}:")
        print(f"   Sentence: {case['sentence']}")
        print(f"   Should convert: {should_convert} (expected: {case['expected']})")
        print(f"   Reason: {reason}")


def test_full_conversion():
    """Test full passive to active conversion with context"""
    print("\n🧪 Test 3: Full Conversion with Context")
    print("=" * 60)
    
    test_cases = [
        {
            'previous': "The SIMATIC S7+ Connector provides advanced features.",
            'current': "It is integrated in version V1.5.",
            'name': "Example from user query"
        },
        {
            'previous': "The application handles multiple protocols.",
            'current': "This is configured through the settings panel.",
            'name': "Configuration context"
        },
        {
            'previous': "The system monitors network traffic.",
            'current': "It is updated every 5 seconds.",
            'name': "System behavior"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {case['name']}")
        print(f"   Previous: {case['previous']}")
        print(f"   Current:  {case['current']}")
        
        result = convert_passive_with_context(case['current'], case['previous'])
        
        if result:
            if result.get('conversion_required', True):
                print(f"   ✅ Converted: {result['suggestion']}")
                print(f"   📋 Explanation: {result['explanation']}")
                print(f"   🎯 Method: {result['method']}")
                print(f"   📊 Confidence: {result['confidence']}")
            else:
                print(f"   ⚠️  No conversion needed")
                print(f"   📋 Reason: {result['explanation']}")
        else:
            print(f"   ❌ Conversion failed")


def test_conversion_not_required():
    """Test cases where passive voice should be kept"""
    print("\n🧪 Test 4: Cases Where Passive is Preferred")
    print("=" * 60)
    
    test_cases = [
        {
            'previous': "The experiment was carefully designed.",
            'current': "The result was observed after 24 hours.",
            'name': "Scientific observation"
        },
        {
            'previous': "The requirements were documented.",
            'current': "It must be approved by management.",
            'name': "Approval requirement"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {case['name']}")
        print(f"   Previous: {case['previous']}")
        print(f"   Current:  {case['current']}")
        
        result = convert_passive_with_context(case['current'], case['previous'])
        
        if result and not result.get('conversion_required', True):
            print(f"   ✅ Correctly kept passive")
            print(f"   📋 Reason: {result['explanation']}")
        else:
            print(f"   ⚠️  System suggested conversion (may not be ideal)")


if __name__ == "__main__":
    print("🚀 Testing Anaphora Resolution System")
    print("=" * 60)
    
    try:
        test_pronoun_resolution()
        test_conversion_decision()
        test_full_conversion()
        test_conversion_not_required()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

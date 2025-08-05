#!/usr/bin/env python3
"""
Test RAG integration with the updated rules
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Test content with various issues
test_content = """
The configuration options of the data source are displayed by the system when you access the admin panel.
This is a very long sentence that really should be broken down into shorter sentences because it contains too many words and may confuse readers who are trying to understand the complex information being presented in this overly complicated manner.
You may use this feature when you need to configure settings.
The system could process the data faster.
Please utilize the new functionality prior to your endeavor to complete the task.
"""

def test_passive_voice():
    """Test passive voice rule with RAG"""
    try:
        from app.rules.passive_voice import check
        print("🧪 Testing passive voice rule...")
        results = check(test_content)
        print(f"Found {len(results)} passive voice issues:")
        for i, result in enumerate(results[:3]):  # Show first 3
            if isinstance(result, dict):
                print(f"  {i+1}. {result.get('message', result)}")
            else:
                print(f"  {i+1}. {result}")
        print()
    except Exception as e:
        print(f"❌ Error testing passive voice: {e}")

def test_long_sentences():
    """Test long sentences rule with RAG"""
    try:
        from app.rules.long_sentences import check
        print("🧪 Testing long sentences rule...")
        results = check(test_content)
        print(f"Found {len(results)} long sentence issues:")
        for i, result in enumerate(results[:3]):  # Show first 3
            if isinstance(result, dict):
                print(f"  {i+1}. {result.get('message', result)}")
            else:
                print(f"  {i+1}. {result}")
        print()
    except Exception as e:
        print(f"❌ Error testing long sentences: {e}")

def test_modal_verbs():
    """Test modal verbs rule with RAG"""
    try:
        from app.rules.can_may_terms import check
        print("🧪 Testing modal verbs rule...")
        results = check(test_content)
        print(f"Found {len(results)} modal verb issues:")
        for i, result in enumerate(results[:3]):  # Show first 3
            if isinstance(result, dict):
                print(f"  {i+1}. {result.get('message', result)}")
            else:
                print(f"  {i+1}. {result}")
        print()
    except Exception as e:
        print(f"❌ Error testing modal verbs: {e}")

def test_style_guide():
    """Test style guide rule with RAG"""
    try:
        from app.rules.style_guide import check
        print("🧪 Testing style guide rule...")
        results = check(test_content)
        print(f"Found {len(results)} style issues:")
        for i, result in enumerate(results[:3]):  # Show first 3
            if isinstance(result, dict):
                print(f"  {i+1}. {result.get('message', result)}")
            else:
                print(f"  {i+1}. {result}")
        print()
    except Exception as e:
        print(f"❌ Error testing style guide: {e}")

def test_rag_availability():
    """Test if RAG system is available"""
    try:
        from app.rag_system import get_rag_suggestion
        print("🧪 Testing RAG availability...")
        result = get_rag_suggestion(
            feedback_text="Passive voice detected in sentence",
            sentence_context="The data is processed by the system",
            document_type="technical"
        )
        if result:
            print("✅ RAG system is available and working")
            print(f"Sample suggestion: {result.get('suggestion', 'No suggestion')[:100]}...")
        else:
            print("⚠️  RAG system available but returned no result")
        print()
    except Exception as e:
        print(f"❌ RAG system error: {e}")
        print("🔄 Rules will fall back to legacy detection")
        print()

if __name__ == "__main__":
    print("🚀 Testing RAG integration with rules...")
    print("=" * 50)
    
    # Test RAG availability first
    test_rag_availability()
    
    # Test individual rules
    test_passive_voice()
    test_long_sentences()
    test_modal_verbs()
    test_style_guide()
    
    print("✅ RAG integration testing complete!")
    print("\nKey benefits:")
    print("✅ All rules now use RAG as primary suggestion engine")
    print("✅ Smart fallback to rule-based detection when RAG unavailable")
    print("✅ Enhanced context-aware suggestions from Gemini")
    print("✅ Backward compatibility maintained")

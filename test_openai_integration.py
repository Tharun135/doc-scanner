#!/usr/bin/env python3
"""
Test OpenAI integration directly
"""

import os
import sys
sys.path.append('.')

def test_openai_basic():
    """Test basic OpenAI functionality"""
    print("🧪 Testing OpenAI Integration")
    print("=" * 40)
    
    # Test 1: Import
    try:
        import openai
        print("✅ OpenAI package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenAI: {e}")
        return False
    
    # Test 2: Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OPENAI_API_KEY environment variable found")
        print("To fix: setx OPENAI_API_KEY \"your_api_key_here\"")
        return False
    else:
        print(f"✅ API key found: {api_key[:8]}...")
    
    # Test 3: Initialize client
    try:
        client = openai.OpenAI(api_key=api_key)
        print("✅ OpenAI client created successfully")
    except Exception as e:
        print(f"❌ Failed to create OpenAI client: {e}")
        return False
    
    # Test 4: Test API call
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Reply with just 'Hello'"}
            ],
            max_tokens=10
        )
        
        if response and response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            print(f"✅ API call successful: {content}")
            return True
        else:
            print("❌ Invalid response structure")
            return False
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

def test_ai_improvement():
    """Test the AI improvement system"""
    print("\n🔧 Testing AI Improvement System")
    print("=" * 40)
    
    try:
        from app.ai_improvement import get_enhanced_ai_suggestion
        print("✅ AI improvement module imported")
        
        # Test suggestion
        result = get_enhanced_ai_suggestion(
            feedback_text="This sentence contains passive voice",
            sentence_context="The document was created by the team.",
            document_type="technical",
            writing_goals=["clarity"]
        )
        
        print(f"✅ AI suggestion generated")
        print(f"📝 Method: {result.get('method', 'unknown')}")
        print(f"🎯 Confidence: {result.get('confidence', 'unknown')}")
        print(f"💬 Suggestion: {result.get('suggestion', 'No suggestion')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI improvement test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    basic_ok = test_openai_basic()
    if basic_ok:
        ai_ok = test_ai_improvement()
        if ai_ok:
            print("\n🎉 All tests passed! OpenAI integration is working.")
        else:
            print("\n⚠️ OpenAI works, but AI improvement system has issues.")
    else:
        print("\n❌ OpenAI basic test failed. Please set up API key.")

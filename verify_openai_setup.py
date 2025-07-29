#!/usr/bin/env python3
"""
OpenAI Setup Verification Script
Run this after setting your OPENAI_API_KEY to verify everything works
"""

import os
import sys
import requests
import json

def check_api_key():
    """Check if API key is set"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found!")
        print("📝 To fix this:")
        print("   1. Get your API key from: https://platform.openai.com/api-keys")
        print("   2. Run: setx OPENAI_API_KEY \"your_api_key_here\"")
        print("   3. Restart your terminal")
        print("   4. Run this script again")
        return False
    else:
        print(f"✅ API key found: {api_key[:20]}...")
        return True

def test_openai_direct():
    """Test OpenAI API directly"""
    print("\n🧪 Testing OpenAI API directly...")
    try:
        import openai
        api_key = os.getenv('OPENAI_API_KEY')
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'OpenAI is working!'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✅ OpenAI API test successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_app_endpoint():
    """Test the application's AI endpoint"""
    print("\n🔧 Testing application AI endpoint...")
    
    test_data = {
        "feedback": "This sentence contains passive voice",
        "sentence": "The document was created by the team.",
        "document_type": "technical",
        "writing_goals": ["clarity", "conciseness"]
    }
    
    try:
        response = requests.post(
            'http://localhost:5000/ai_suggestion',
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            method = result.get('method', 'unknown')
            suggestion = result.get('suggestion', 'No suggestion')
            
            print(f"✅ Endpoint test successful!")
            print(f"📋 Method used: {method}")
            print(f"💬 Suggestion preview: {suggestion[:100]}...")
            
            if method == 'openai_chatgpt':
                print("🎉 OpenAI integration is working perfectly!")
                return True
            elif method == 'smart_fallback':
                print("⚠️  Using fallback - OpenAI may not be configured properly")
                return False
            else:
                print(f"ℹ️  Using method: {method}")
                return True
        else:
            print(f"❌ Endpoint returned error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to localhost:5000 - is the app running?")
        print("💡 Start the app with: python run.py")
        return False
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
        return False

def main():
    print("🚀 OpenAI Integration Verification")
    print("=" * 50)
    
    # Step 1: Check API key
    if not check_api_key():
        return False
    
    # Step 2: Test OpenAI directly
    if not test_openai_direct():
        return False
    
    # Step 3: Test app endpoint
    endpoint_ok = test_app_endpoint()
    
    if endpoint_ok:
        print("\n🎉 All tests passed! Your OpenAI integration is working perfectly!")
        print("💡 You can now use AI suggestions in the application.")
    else:
        print("\n⚠️  OpenAI API works, but there may be an issue with the application integration.")
        print("💡 Try restarting the application.")
    
    return endpoint_ok

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🔍 Need help? Check the OPENAI_MIGRATION.md file for detailed instructions.")
        sys.exit(1)

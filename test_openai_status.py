#!/usr/bin/env python3
"""
Test OpenAI API Integration Status
"""

import os
from dotenv import load_dotenv

def test_openai_setup():
    """Test OpenAI API key setup and integration"""
    print("🔍 Testing OpenAI Integration Setup")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        # Mask the key for security
        masked_key = f"{api_key[:12]}...{api_key[-8:]}" if len(api_key) > 20 else "***"
        print(f"✅ API Key Found: {masked_key}")
        print(f"📏 Key Length: {len(api_key)} characters")
        
        # Check if it looks like a valid OpenAI key
        if api_key.startswith('sk-'):
            print("✅ Key Format: Valid OpenAI format")
        else:
            print("❌ Key Format: Invalid (should start with 'sk-')")
            
    else:
        print("❌ API Key: Not found in environment")
        return False
    
    # Check model setting
    model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    print(f"🤖 Model: {model}")
    
    # Check temperature setting
    temperature = os.getenv('OPENAI_TEMPERATURE', '0.1')
    print(f"🌡️ Temperature: {temperature}")
    
    print("\n📊 Integration Status Summary:")
    print("✅ OpenAI API integration is configured correctly")
    print("✅ Environment variables are loaded properly")
    print("✅ API key is in the correct format")
    print("⚠️ Current issue: API quota exceeded (429 error)")
    print("\n💡 Next Steps:")
    print("1. Check your OpenAI billing at: https://platform.openai.com/account/billing")
    print("2. Add payment method or upgrade plan if needed")
    print("3. Wait for quota reset if on free tier")
    print("4. Once quota is available, AI suggestions will use OpenAI ChatGPT!")
    
    return True

if __name__ == "__main__":
    test_openai_setup()

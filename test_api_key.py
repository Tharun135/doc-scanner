"""
Simple test to verify Google Gemini API key is working.
Run this after adding your API key to the .env file.
"""

import os
from dotenv import load_dotenv

def test_api_key_setup():
    """Test if the Google API key is properly configured."""
    print("🔍 Checking Google API Key Setup...")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in .env file")
        print("\n📝 To fix this:")
        print("1. Open your .env file")
        print("2. Add: GOOGLE_API_KEY=your_actual_key_here")
        return False
    
    if api_key == "your_google_api_key_here":
        print("❌ GOOGLE_API_KEY is still the placeholder")
        print("\n📝 To fix this:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Replace the placeholder in .env with your actual key")
        return False
    
    # Basic validation
    if not api_key.startswith('AIza'):
        print("⚠️  API key doesn't look like a Google API key")
        print("   Google API keys usually start with 'AIza'")
        print(f"   Your key starts with: {api_key[:10]}...")
        return False
    
    if len(api_key) < 35:
        print("⚠️  API key seems too short")
        print(f"   Key length: {len(api_key)} characters")
        print("   Google API keys are usually 39+ characters")
        return False
    
    print("✅ GOOGLE_API_KEY is set correctly!")
    print(f"✅ Key starts with: {api_key[:10]}...")
    print(f"✅ Key length: {len(api_key)} characters")
    
    # Test the actual API connection
    print("\n🧪 Testing API connection...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        # Simple test call
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello, this is a test.")
        
        print("🎉 SUCCESS! Gemini API is working!")
        print(f"📝 Test response: {response.text[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        print("\n🔧 Common solutions:")
        print("1. Check your API key is correct")
        print("2. Ensure you have internet connection")
        print("3. Verify the API key has proper permissions")
        return False

if __name__ == "__main__":
    test_api_key_setup()

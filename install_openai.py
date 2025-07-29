#!/usr/bin/env python3
"""
Quick installation script for OpenAI ChatGPT integration
"""

import os
import sys
import subprocess

def main():
    print("🚀 Doc-Scanner OpenAI Integration Setup")
    print("=" * 50)
    
    # Install OpenAI package
    print("📦 Installing OpenAI package...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "openai==1.54.4"], check=True)
        print("✅ OpenAI package installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install OpenAI package")
        return False
    
    # Check for API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("\n🔑 OpenAI API Key Setup Required:")
        print("1. Get your API key from: https://platform.openai.com/api-keys")
        print("2. Set environment variable:")
        print("   Windows: setx OPENAI_API_KEY \"your_api_key_here\"")
        print("   Linux/Mac: export OPENAI_API_KEY=\"your_api_key_here\"")
        print("3. Restart your terminal and run this script again")
        return False
    
    # Test API connection
    print("\n🧪 Testing OpenAI connection...")
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()
        print("✅ OpenAI API connection successful!")
        
        # Show available models
        gpt_models = [m.id for m in models.data if 'gpt' in m.id.lower()]
        print(f"📋 Available GPT models: {len(gpt_models)}")
        
    except Exception as e:
        print(f"❌ OpenAI API connection failed: {e}")
        return False
    
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 You can now start the application with: python run.py")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)

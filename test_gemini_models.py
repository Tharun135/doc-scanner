import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the API
api_key = os.getenv('GOOGLE_API_KEY')
print(f"Using API key: {api_key[:10]}...")

genai.configure(api_key=api_key)

# List available models
print("🔍 Available Gemini Models:")
print("=" * 50)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Display Name: {model.display_name}")
        print(f"   Description: {model.description}")
        print("-" * 30)

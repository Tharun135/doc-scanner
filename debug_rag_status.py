#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.append('.')

print("🔍 Debugging RAG System")
print("=" * 40)

# Step 1: Check RAG_ENABLED flag
try:
    from app.rules.rag_rule_helper import RAG_ENABLED, RAG_AVAILABLE
    print(f"✅ RAG_ENABLED: {RAG_ENABLED}")
    print(f"✅ RAG_AVAILABLE: {RAG_AVAILABLE}")
except Exception as e:
    print(f"❌ Error importing RAG flags: {e}")

# Step 2: Check dependencies
print("\n📦 Checking Dependencies:")
try:
    import dotenv
    print("✅ python-dotenv available")
except ImportError:
    print("❌ python-dotenv missing")

try:
    import google.generativeai
    print("✅ google-generativeai available")
except ImportError:
    print("❌ google-generativeai missing")

try:
    import langchain_google_genai
    print("✅ langchain-google-genai available")
except ImportError:
    print("❌ langchain-google-genai missing")

# Step 3: Check environment
print("\n🔑 Environment Configuration:")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print(f"✅ Google API key configured (length: {len(api_key)})")
else:
    print("❌ Google API key not found")

# Step 4: Test passive voice rule
print("\n🧪 Testing Passive Voice Rule:")
try:
    from app.rules.passive_voice import check
    content = '<p>The document was written by John.</p>'
    results = check(content)
    print(f"📊 Results: {len(results)} suggestions")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result}")
        # Check for RAG indicators
        if any(keyword in str(result).lower() for keyword in ['rag', 'gemini', 'enhanced']):
            print("     🟢 RAG-enhanced suggestion!")
        elif any(keyword in str(result).lower() for keyword in ['fallback', 'legacy']):
            print("     🟡 Using fallback method")
except Exception as e:
    print(f"❌ Error testing passive voice: {e}")

print("\n📋 Summary:")
print("If you see 'fallback' or 'legacy', RAG is not working.")
print("If you see 'RAG-enhanced' or 'gemini', RAG is active!")

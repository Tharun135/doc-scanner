"""
Test script to verify Gemini AI integration is working properly.
Run this after setting up your GOOGLE_API_KEY in the .env file.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ai_improvement import get_enhanced_ai_suggestion

def test_gemini_integration():
    """Test Gemini AI integration with various writing issues."""
    print("🔍 Testing Gemini AI Integration...")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Passive Voice",
            "feedback": "Passive voice detected",
            "sentence": "The document was written by the team"
        },
        {
            "name": "Long Sentence", 
            "feedback": "Long sentence detected (32 words)",
            "sentence": "This is a very long sentence that contains many clauses and ideas that should probably be broken into shorter, more digestible pieces for better readability."
        },
        {
            "name": "Modal Verb Issue",
            "feedback": "Modal verb usage: 'may' for permission",
            "sentence": "You may use this feature when needed"
        },
        {
            "name": "Grammar Issue",
            "feedback": "Subject-verb disagreement detected",
            "sentence": "The data are shows interesting patterns"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Issue: {test_case['feedback']}")
        print(f"Sentence: '{test_case['sentence']}'")
        print("-" * 40)
        
        try:
            result = get_enhanced_ai_suggestion(
                feedback_text=test_case['feedback'],
                sentence_context=test_case['sentence'],
                document_type="general"
            )
            
            print(f"✅ Method: {result.get('method', 'unknown')}")
            print(f"✅ Confidence: {result.get('confidence', 'unknown')}")
            print(f"✅ Suggestion: {result.get('suggestion', 'No suggestion')[:100]}...")
            
            gemini_answer = result.get('gemini_answer', '')
            if gemini_answer:
                print(f"🤖 Gemini Answer: {gemini_answer[:100]}...")
            else:
                print("❌ No Gemini answer generated")
                
            if result.get('method') == 'gemini_rag':
                print("🎉 SUCCESS: Using real Gemini AI!")
            elif result.get('method') == 'minimal_fallback':
                print("⚠️  FALLBACK: Gemini not available - check your API key")
            else:
                print(f"ℹ️  Method: {result.get('method')}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")
    
    # Check API key status
    print("\n🔑 API Key Status:")
    from dotenv import load_dotenv
    load_dotenv()
    
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if google_api_key and google_api_key != 'your_google_api_key_here':
        print("✅ GOOGLE_API_KEY is set")
        if len(google_api_key) > 20:
            print(f"✅ API key looks valid (length: {len(google_api_key)})")
        else:
            print("⚠️  API key seems too short")
    else:
        print("❌ GOOGLE_API_KEY not set or still placeholder")
        print("   Get your API key from: https://makersuite.google.com/app/apikey")
        print("   Add it to your .env file: GOOGLE_API_KEY=your_actual_key_here")

if __name__ == "__main__":
    test_gemini_integration()

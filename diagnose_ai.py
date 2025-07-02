#!/usr/bin/env python3
"""
Diagnostic script to check AI/LLM integration status
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_ollama_connection():
    """Test direct Ollama connection"""
    try:
        import ollama
        print("✅ Ollama package imported successfully")
        
        # Test listing models
        models = ollama.list()
        print(f"✅ Ollama connection successful")
        print(f"   Available models: {[model.model for model in models.models]}")
        
        # Test simple generation
        response = ollama.generate(
            model='mistral:latest',
            prompt='Say "Hello World" in active voice.',
            options={'temperature': 0.1, 'num_predict': 10}
        )
        
        if response and 'response' in response:
            print(f"✅ Mistral generation test successful")
            print(f"   Response: {response['response'].strip()}")
            return True
        else:
            print("❌ Mistral generation failed - no response")
            return False
            
    except ImportError as e:
        print(f"❌ Ollama package not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_passive_voice_module():
    """Test the passive voice module"""
    try:
        from app.rules.passive_voice import check, OLLAMA_AVAILABLE, convert_with_llm_api
        print("✅ Passive voice module imported successfully")
        print(f"   OLLAMA_AVAILABLE: {OLLAMA_AVAILABLE}")
        
        # Test the main check function
        test_sentence = "The document was created by the team."
        suggestions = check(test_sentence)
        
        if suggestions:
            print(f"✅ Passive voice detection working")
            print(f"   Test sentence: '{test_sentence}'")
            print(f"   Suggestions: {suggestions}")
            return True
        else:
            print(f"❌ No suggestions returned for: '{test_sentence}'")
            
            # Test LLM function directly
            llm_result = convert_with_llm_api(test_sentence)
            if llm_result:
                print(f"✅ Direct LLM conversion works: '{llm_result}'")
            else:
                print("❌ Direct LLM conversion also failed")
            return False
            
    except Exception as e:
        print(f"❌ Passive voice module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 AI Integration Diagnostics")
    print("=" * 50)
    
    print("\n1. Testing Ollama Connection...")
    ollama_ok = test_ollama_connection()
    
    print("\n2. Testing Passive Voice Module...")
    module_ok = test_passive_voice_module()
    
    print("\n" + "=" * 50)
    if ollama_ok and module_ok:
        print("✅ All tests passed! AI suggestions should be working.")
    else:
        print("❌ Some tests failed. AI suggestions may not be available.")
        print("\nPossible fixes:")
        print("- Restart Ollama service")
        print("- Check if Mistral model is properly loaded")
        print("- Check application logs for errors")

if __name__ == "__main__":
    main()

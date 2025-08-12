#!/usr/bin/env python3
"""
Debug script to test AI suggestion pipeline and identify issues.
"""

import sys
import os
import logging

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_ai_suggestion_pipeline():
    """Test the AI suggestion pipeline with sample data."""
    print("=== Testing AI Suggestion Pipeline ===\n")
    
    # Test cases
    test_cases = [
        {
            "feedback": "passive voice detected",
            "sentence": "The document was reviewed by the team.",
            "description": "Passive voice test"
        },
        {
            "feedback": "sentence too long",
            "sentence": "The new feature allows users to configure their settings, customize their preferences, and manage their data all in one centralized location.",
            "description": "Long sentence test"
        },
        {
            "feedback": "unclear reference above",
            "sentence": "This feature is described above.",
            "description": "Reference issue test"
        }
    ]
    
    try:
        # Import the AI improvement module
        from app.ai_improvement import get_enhanced_ai_suggestion
        print("✓ Successfully imported ai_improvement module")
        
        # Test each case
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}: {test_case['description']} ---")
            print(f"Feedback: {test_case['feedback']}")
            print(f"Sentence: {test_case['sentence']}")
            
            try:
                # Get the AI suggestion
                result = get_enhanced_ai_suggestion(
                    feedback_text=test_case['feedback'],
                    sentence_context=test_case['sentence'],
                    document_type="technical",
                    writing_goals=["clarity", "conciseness"],
                    document_content="Sample document content for testing."
                )
                
                print(f"✓ Result received")
                print(f"Method: {result.get('method', 'unknown')}")
                print(f"Confidence: {result.get('confidence', 'unknown')}")
                print(f"Suggestion: {result.get('suggestion', 'No suggestion')[:200]}...")
                
                # Check if it's actually AI-generated or rule-based
                if result.get('method') == 'llamaindex_ai':
                    print("✓ Using actual AI (LlamaIndex)")
                elif result.get('method') == 'llamaindex_rag':
                    print("✓ Using AI with RAG")
                elif result.get('method') == 'smart_fallback':
                    print("⚠ Using rule-based fallback")
                else:
                    print(f"? Unknown method: {result.get('method')}")
                    
            except Exception as e:
                print(f"✗ Error in test case {i}: {str(e)}")
                import traceback
                traceback.print_exc()
        
    except ImportError as e:
        print(f"✗ Failed to import ai_improvement: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_llamaindex_directly():
    """Test LlamaIndex AI system directly."""
    print("\n=== Testing LlamaIndex AI Directly ===\n")
    
    try:
        from app.llamaindex_ai import LlamaIndexAISuggestionEngine
        print("✓ Successfully imported LlamaIndexAISuggestionEngine")
        
        # Create engine instance
        ai_engine = LlamaIndexAISuggestionEngine(model_name="mistral")
        print(f"✓ Created AI engine")
        print(f"LlamaIndex available: {ai_engine.llamaindex_available}")
        print(f"Is initialized: {ai_engine.is_initialized}")
        print(f"Model name: {ai_engine.model_name}")
        
        if not ai_engine.is_initialized:
            print("⚠ AI engine not initialized - checking why...")
            # Try to test Ollama connection manually
            ai_engine._initialize_ollama()
            print(f"After manual init - Is initialized: {ai_engine.is_initialized}")
        
        if ai_engine.is_initialized:
            # Test a simple suggestion
            print("\n--- Testing direct AI suggestion ---")
            result = ai_engine.generate_contextual_suggestion(
                feedback_text="passive voice detected",
                sentence_context="The document was reviewed by the team.",
                document_type="technical"
            )
            
            print(f"Method: {result.get('method')}")
            print(f"Suggestion: {result.get('suggestion')[:200]}...")
            
            # Test if it's actually calling Ollama
            if result.get('method') in ['llamaindex_ai', 'llamaindex_rag']:
                print("✓ Successfully using AI")
            else:
                print("⚠ Falling back to rule-based")
        
    except Exception as e:
        print(f"✗ Error testing LlamaIndex directly: {e}")
        import traceback
        traceback.print_exc()

def test_ollama_connection():
    """Test Ollama connection and model availability."""
    print("\n=== Testing Ollama Connection ===\n")
    
    try:
        import requests
        
        # Test if Ollama is running
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama service is running")
            models = response.json().get("models", [])
            print(f"Available models: {[m['name'] for m in models]}")
        else:
            print(f"✗ Ollama service responded with status {response.status_code}")
            
        # Test if we can make a simple generation request
        test_prompt = {
            "model": "mistral",
            "prompt": "Fix this passive voice sentence: 'The document was reviewed by the team.'",
            "stream": False
        }
        
        response = requests.post("http://localhost:11434/api/generate", 
                               json=test_prompt, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✓ Ollama generation test successful")
            print(f"Response: {result.get('response', '')[:200]}...")
        else:
            print(f"✗ Ollama generation failed with status {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error testing Ollama: {e}")

if __name__ == "__main__":
    test_ollama_connection()
    test_llamaindex_directly() 
    test_ai_suggestion_pipeline()

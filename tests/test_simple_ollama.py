#!/usr/bin/env python3
"""
Simple Ollama RAG test with auto-detection of available models
"""

import sys
import subprocess
import json

# Add current directory to path
sys.path.append('.')

def get_available_models():
    """Get list of available Ollama models"""
    try:
        result = subprocess.run(["ollama", "list", "--json"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models_data = json.loads(result.stdout)
            models = [model['name'].split(':')[0] for model in models_data.get('models', [])]
            return models
        else:
            # Try without --json flag
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = [line.split()[0].split(':')[0] for line in lines if line.strip()]
                return models
    except Exception as e:
        print(f"Error getting models: {e}")
    
    return []

def test_ollama_rag_with_model(model_name):
    """Test Ollama RAG with a specific model"""
    print(f"🧪 Testing with model: {model_name}")
    print("-" * 30)
    
    try:
        sys.path.append('scripts')
        from ollama_rag_system import OllamaRAGSystem
        
        # Create system with specific model
        rag_system = OllamaRAGSystem(model=model_name)
        
        # Test connection
        status = rag_system.test_connection()
        print(f"Status: {status}")
        
        if status["status"] == "success":
            print("✅ RAG system working!")
            
            # Test actual suggestion
            test_result = rag_system.get_rag_suggestion(
                feedback_text="Passive voice detected",
                sentence_context="The document was written by John yesterday.",
                document_type="technical"
            )
            
            if test_result:
                print(f"✅ Suggestion generated!")
                print(f"Method: {test_result['method']}")
                print(f"Confidence: {test_result['confidence']}")
                print(f"Model: {test_result['model']}")
                print(f"Sources: {len(test_result.get('sources', []))}")
                print(f"Suggestion preview: {test_result['suggestion'][:150]}...")
                return True
            else:
                print("⚠️  No suggestion generated")
                return False
        else:
            print(f"❌ Connection failed: {status.get('reason', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Test Ollama RAG with available models"""
    print("🚀 Simple Ollama RAG Test")
    print("=" * 30)
    
    # Get available models
    models = get_available_models()
    print(f"Available models: {models}")
    
    if not models:
        print("❌ No models found. Install one with: ollama pull phi3:mini")
        return
    
    # Try models in order of preference
    preferred_order = ['mistral', 'phi3', 'llama3', 'tinyllama']
    
    # Sort models by preference
    def model_priority(model):
        for i, preferred in enumerate(preferred_order):
            if preferred in model.lower():
                return i
        return len(preferred_order)
    
    sorted_models = sorted(models, key=model_priority)
    print(f"Testing order: {sorted_models}")
    print()
    
    # Test each model until one works
    for model in sorted_models:
        if test_ollama_rag_with_model(model):
            print(f"\n🎉 SUCCESS with {model}!")
            print("Your Ollama RAG system is working!")
            break
        print()
    else:
        print("\n❌ No models worked. Check Ollama setup.")

if __name__ == "__main__":
    main()

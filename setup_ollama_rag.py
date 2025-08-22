#!/usr/bin/env python3
"""
Ollama RAG Setup and Test Script
This script will guide you through setting up Ollama + ChromaDB + LlamaIndex for DocScanner
"""

import subprocess
import sys
import os
import time
import requests

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python Dependencies")
    print("=" * 40)
    
    packages = [
        "llama-index-core",
        "llama-index-llms-ollama", 
        "llama-index-vector-stores-chroma",
        "llama-index-embeddings-ollama",
        "chromadb",
        "ollama"
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            return False
    
    print("✅ All Python dependencies installed!")
    return True

def check_ollama_server():
    """Check if Ollama server is running"""
    print("\n🔍 Checking Ollama Server")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ Ollama server is running (version: {version_info.get('version', 'unknown')})")
            return True
        else:
            print("❌ Ollama server responded with error")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama server is not running")
        print("💡 Start it with: ollama serve")
        return False

def check_ollama_models():
    """Check available Ollama models"""
    print("\n🤖 Checking Available Models")
    print("=" * 40)
    
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models = result.stdout.strip()
            print("Available models:")
            print(models)
            
            # Check for recommended models
            recommended = ["llama3", "mistral", "phi3"]
            available_recommended = []
            
            for model in recommended:
                if model in models.lower():
                    available_recommended.append(model)
            
            if available_recommended:
                print(f"✅ Recommended models available: {available_recommended}")
                return available_recommended[0]  # Return first available
            else:
                print("⚠️  No recommended models found")
                print("💡 Download a model with: ollama pull llama3")
                return None
        else:
            print("❌ Could not list Ollama models")
            return None
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama CLI not found or timed out")
        print("💡 Install Ollama from: https://ollama.ai")
        return None

def test_ollama_rag():
    """Test the Ollama RAG system"""
    print("\n🧪 Testing Ollama RAG Integration")
    print("=" * 40)
    
    try:
        # Import and test our Ollama RAG system
        sys.path.append(os.path.dirname(__file__))
        from ollama_rag_system import OllamaRAGSystem
        
        # Create system instance
        rag_system = OllamaRAGSystem()
        
        # Test connection
        status = rag_system.test_connection()
        print(f"Connection test: {status}")
        
        if status["status"] == "success":
            print("✅ Ollama RAG system working!")
            
            # Test actual suggestion
            test_result = rag_system.get_rag_suggestion(
                feedback_text="Passive voice detected",
                sentence_context="The document was written by John.",
                document_type="technical"
            )
            
            if test_result:
                print("\n📝 Sample RAG Suggestion:")
                print(f"Method: {test_result['method']}")
                print(f"Confidence: {test_result['confidence']}")
                print(f"Suggestion: {test_result['suggestion'][:200]}...")
                print("✅ Full RAG pipeline working!")
                return True
            else:
                print("⚠️  RAG system initialized but no suggestion generated")
                return False
        else:
            print(f"❌ Connection test failed: {status.get('reason', 'Unknown error')}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def setup_guide():
    """Interactive setup guide"""
    print("🚀 DocScanner Ollama RAG Setup")
    print("=" * 40)
    print()
    
    print("This will set up a local RAG system with:")
    print("• Ollama (Local LLM)")
    print("• ChromaDB (Vector Store)")  
    print("• LlamaIndex (RAG Framework)")
    print()
    
    # Step 1: Install Python dependencies
    install_deps = input("Install Python dependencies? (y/n): ").lower().startswith('y')
    if install_deps:
        if not install_dependencies():
            print("❌ Dependency installation failed. Exiting.")
            return False
    
    # Step 2: Check Ollama server
    if not check_ollama_server():
        print("\n💡 Ollama Setup Instructions:")
        print("1. Download Ollama: https://ollama.ai")
        print("2. Install and start: ollama serve")
        print("3. Download a model: ollama pull llama3")
        print("4. Re-run this script")
        return False
    
    # Step 3: Check models
    available_model = check_ollama_models()
    if not available_model:
        print("\n💡 Download a model first:")
        print("ollama pull llama3")
        return False
    
    # Step 4: Test RAG system
    if test_ollama_rag():
        print("\n🎉 Setup Complete!")
        print("Your DocScanner now has local RAG capabilities:")
        print("• No API keys needed")
        print("• Complete privacy") 
        print("• Zero ongoing costs")
        print("• Fast local inference")
        return True
    else:
        print("\n❌ Setup incomplete. Check errors above.")
        return False

def quick_test():
    """Quick test without setup"""
    print("🔍 Quick Ollama RAG Test")
    print("=" * 25)
    
    # Check if dependencies exist
    try:
        import chromadb
        print("✅ ChromaDB available")
    except ImportError:
        print("❌ ChromaDB not installed")
        return False
    
    try:
        from llama_index.core import VectorStoreIndex
        print("✅ LlamaIndex available")
    except ImportError:
        print("❌ LlamaIndex not installed")
        return False
    
    # Test Ollama
    if check_ollama_server():
        model = check_ollama_models()
        if model:
            print(f"✅ Ready to use model: {model}")
            return test_ollama_rag()
    
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_test()
    else:
        setup_guide()

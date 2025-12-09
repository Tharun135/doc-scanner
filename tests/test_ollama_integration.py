#!/usr/bin/env python3
"""
Test the Ollama RAG integration with DocScanner
This tests the complete pipeline: Rule detection → RAG enhancement → Suggestion
"""

import sys
import os

# Add current directory to path
sys.path.append('.')

def test_current_rag_status():
    """Test current RAG system status"""
    print("🔍 Current RAG System Status")
    print("=" * 40)
    
    try:
        from app.rules.rag_rule_helper import RAG_AVAILABLE, RAG_ENABLED, RAG_TYPE
        print(f"RAG_AVAILABLE: {RAG_AVAILABLE}")
        print(f"RAG_ENABLED: {RAG_ENABLED}")
        print(f"RAG_TYPE: {RAG_TYPE}")
        
        if RAG_AVAILABLE:
            print("✅ RAG system is functional")
            return True
        else:
            print("❌ RAG system not available")
            return False
            
    except Exception as e:
        print(f"❌ Error checking RAG: {e}")
        return False

def test_ollama_installation():
    """Test if Ollama is installed and running"""
    print("\n🤖 Ollama Installation Check")
    print("=" * 40)
    
    import subprocess
    import requests
    
    # Check if Ollama CLI is available
    try:
        result = subprocess.run(["ollama", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Ollama CLI installed: {result.stdout.strip()}")
        else:
            print("❌ Ollama CLI not responding")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Ollama CLI not found")
        print("💡 Install from: https://ollama.ai")
        return False
    
    # Check if Ollama server is running
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ Ollama server running (version: {version_info.get('version', 'unknown')})")
        else:
            print("❌ Ollama server error")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama server not running")
        print("💡 Start with: ollama serve")
        return False
    
    # Check available models
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models = result.stdout.strip()
            print("📋 Available models:")
            print(models if models else "  No models installed")
            
            if "llama3" in models.lower() or "mistral" in models.lower() or "phi3" in models.lower():
                print("✅ Suitable model found")
                return True
            else:
                print("⚠️  No suitable model found")
                print("💡 Download with: ollama pull llama3")
                return False
        else:
            print("❌ Could not list models")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Model list timed out")
        return False

def test_dependencies():
    """Test if required Python packages are installed"""
    print("\n📦 Python Dependencies Check")
    print("=" * 40)
    
    required = [
        ("chromadb", "ChromaDB"),
        ("llama_index.core", "LlamaIndex Core"),
        ("llama_index.llms.ollama", "LlamaIndex Ollama LLM"),
        ("llama_index.vector_stores.chroma", "LlamaIndex ChromaDB"),
    ]
    
    missing = []
    
    for package, name in required:
        try:
            __import__(package)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name}")
            missing.append(package)
    
    if missing:
        print(f"\n💡 Install missing packages:")
        install_cmd = "pip install " + " ".join([
            "chromadb",
            "llama-index-core", 
            "llama-index-llms-ollama",
            "llama-index-vector-stores-chroma",
            "llama-index-embeddings-ollama"
        ])
        print(install_cmd)
        return False
    
    print("✅ All dependencies installed")
    return True

def test_ollama_rag_system():
    """Test the Ollama RAG system directly"""
    print("\n🧪 Testing Ollama RAG System")
    print("=" * 40)
    
    try:
        sys.path.append('scripts')
        from ollama_rag_system import OllamaRAGSystem, test_ollama_rag
        
        # Run the built-in test
        print("Running built-in test...")
        test_ollama_rag()
        return True
        
    except Exception as e:
        print(f"❌ Ollama RAG test failed: {e}")
        return False

def test_rule_integration():
    """Test RAG integration with rules"""
    print("\n🔧 Testing Rule Integration")
    print("=" * 40)
    
    try:
        from app.rules.rag_rule_helper import check_with_rag
        
        # Test with a simple rule
        test_content = '<p>The document was written by John yesterday.</p>'
        
        # Mock rule patterns for passive voice
        rule_patterns = {
            'detect_function': lambda content: [
                {
                    'type': 'passive_voice',
                    'issue': 'Passive voice detected: "was written"',
                    'sentence': 'The document was written by John yesterday.',
                    'position': [0, 45],
                    'context': 'technical_writing'
                }
            ]
        }
        
        fallback_suggestions = [
            "Convert passive voice to active voice: 'John wrote the document yesterday.'"
        ]
        
        print(f"Testing content: {test_content}")
        results = check_with_rag(
            content=test_content,
            rule_patterns=rule_patterns,
            rule_name="passive_voice",
            fallback_suggestions=fallback_suggestions
        )
        
        print(f"📊 Results: {len(results)} suggestions")
        for i, result in enumerate(results):
            print(f"  {i+1}. {result}")
            
            # Check for RAG indicators
            if isinstance(result, dict):
                method = result.get('method', 'unknown')
                print(f"      Method: {method}")
                if 'ollama' in method.lower():
                    print("      🟢 Ollama RAG working!")
                elif 'rag' in method.lower():
                    print(f"      🟡 RAG working ({method})")
                else:
                    print(f"      🟡 Using fallback ({method})")
            elif isinstance(result, str):
                if 'ollama' in result.lower():
                    print("      🟢 Ollama RAG working!")
                elif 'rag' in result.lower():
                    print("      🟡 RAG working")
                else:
                    print("      🟡 Using fallback")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Rule integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests and provide setup guidance"""
    print("🚀 DocScanner Ollama RAG Integration Test")
    print("=" * 50)
    print()
    
    results = {
        "rag_status": test_current_rag_status(),
        "dependencies": test_dependencies(),
        "ollama": test_ollama_installation(),
    }
    
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    if all(results.values()):
        print("\n🎉 All prerequisites met! Testing full integration...")
        
        # Test the actual systems
        ollama_rag_works = test_ollama_rag_system()
        rule_integration_works = test_rule_integration()
        
        if ollama_rag_works and rule_integration_works:
            print("\n🏆 SUCCESS: Ollama RAG fully integrated!")
            print("Your DocScanner now has:")
            print("  🏠 Local LLM processing")
            print("  ⚡ Fast vector search")  
            print("  🔒 Complete privacy")
            print("  💰 Zero ongoing costs")
        else:
            print("\n⚠️  Integration partially working - check errors above")
            
    else:
        print("\n🛠️  Setup needed. Follow these steps:")
        
        if not results["dependencies"]:
            print("\n1. Install Python dependencies:")
            print("   pip install llama-index-core llama-index-llms-ollama llama-index-vector-stores-chroma chromadb llama-index-embeddings-ollama")
        
        if not results["ollama"]:
            print("\n2. Install and setup Ollama:")
            print("   • Download: https://ollama.ai")
            print("   • Start server: ollama serve")
            print("   • Download model: ollama pull llama3")
        
        print("\n3. Re-run this test: python test_ollama_integration.py")

if __name__ == "__main__":
    main()

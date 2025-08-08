"""
Performance Bottleneck Analysis - Identify slow loading issues
"""

import sys
import os
import time

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def analyze_loading_performance():
    """Analyze what's causing slow loading times."""
    print("🔍 ANALYZING LOADING PERFORMANCE BOTTLENECKS")
    print("=" * 60)
    
    total_time = 0
    
    # Test 1: Basic rule imports
    print("\n📦 Testing rule imports...")
    start_time = time.time()
    
    try:
        from app.rules import technical_terms
        import_time = time.time() - start_time
        total_time += import_time
        print(f"   ✅ technical_terms import: {import_time:.3f}s")
    except Exception as e:
        print(f"   ❌ technical_terms import failed: {e}")
    
    # Test 2: spaCy loading
    print("\n🧠 Testing spaCy model loading...")
    start_time = time.time()
    
    try:
        from app.rules.spacy_utils import get_nlp_model
        nlp = get_nlp_model()
        spacy_time = time.time() - start_time
        total_time += spacy_time
        print(f"   ✅ spaCy model load: {spacy_time:.3f}s")
    except Exception as e:
        print(f"   ❌ spaCy model load failed: {e}")
    
    # Test 3: RAG system initialization
    print("\n🤖 Testing RAG/AI system loading...")
    start_time = time.time()
    
    try:
        from app.rules.smart_rag_manager import get_rag_status
        status = get_rag_status()
        rag_time = time.time() - start_time
        total_time += rag_time
        print(f"   ✅ RAG system load: {rag_time:.3f}s")
        print(f"   📊 AI Status: {status.get('ai_engine_initialized', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ RAG system load failed: {e}")
    
    # Test 4: ChromaDB initialization
    print("\n🗄️ Testing ChromaDB loading...")
    start_time = time.time()
    
    try:
        import chromadb
        client = chromadb.PersistentClient(path="./chroma_db")
        chroma_time = time.time() - start_time
        total_time += chroma_time
        print(f"   ✅ ChromaDB load: {chroma_time:.3f}s")
    except Exception as e:
        print(f"   ❌ ChromaDB load failed: {e}")
    
    # Test 5: Ollama connection
    print("\n🦙 Testing Ollama connection...")
    start_time = time.time()
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        ollama_time = time.time() - start_time
        total_time += ollama_time
        
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"   ✅ Ollama connection: {ollama_time:.3f}s")
            print(f"   📋 Available models: {len(models)}")
            for model in models[:3]:  # Show first 3 models
                print(f"      - {model.get('name', 'Unknown')}")
        else:
            print(f"   ⚠️ Ollama responding but error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ollama connection failed: {e}")
    
    # Test 6: Simple rule execution
    print("\n⚡ Testing rule execution...")
    start_time = time.time()
    
    try:
        test_content = "This password should be entered by the user. JSON and HTML files."
        from app.rules.technical_terms import check
        suggestions = check(test_content)
        rule_time = time.time() - start_time
        total_time += rule_time
        print(f"   ✅ Rule execution: {rule_time:.3f}s")
        print(f"   📝 Suggestions: {len(suggestions)}")
    except Exception as e:
        print(f"   ❌ Rule execution failed: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"📊 TOTAL LOADING TIME: {total_time:.3f}s")
    
    # Identify bottlenecks
    print(f"\n🎯 PERFORMANCE RECOMMENDATIONS:")
    if total_time > 10:
        print(f"   🔴 SLOW: {total_time:.1f}s is too slow for good UX")
        print(f"   💡 Target: <2s for good performance")
    elif total_time > 5:
        print(f"   🟡 MODERATE: {total_time:.1f}s is acceptable but can improve")
    else:
        print(f"   🟢 GOOD: {total_time:.1f}s is reasonable")
    
    return total_time

if __name__ == "__main__":
    analyze_loading_performance()

"""
Minimal Performance Test - Test individual components in isolation
"""

import time
import sys
import os

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_isolated_components():
    """Test each component in isolation to find the bottleneck."""
    print("🔬 ISOLATED COMPONENT TESTING")
    print("=" * 50)
    
    # Test 1: Just import the rule module without any RAG
    print("\n1️⃣ Testing bare rule import...")
    start_time = time.time()
    
    try:
        # Import with minimal dependencies
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "technical_terms", 
            "d:/doc-scanner/app/rules/technical_terms.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        import_time = time.time() - start_time
        print(f"   ✅ Bare import: {import_time:.3f}s")
        
        # Test the rule function
        start_time = time.time()
        suggestions = module.check("JSON and HTML files.")
        exec_time = time.time() - start_time
        print(f"   ✅ Rule execution: {exec_time:.3f}s")
        print(f"   📝 Suggestions: {len(suggestions)}")
        
    except Exception as e:
        print(f"   ❌ Bare import failed: {e}")
    
    # Test 2: Import with minimal smart RAG (no heavy deps)
    print("\n2️⃣ Testing minimal smart RAG...")
    start_time = time.time()
    
    try:
        # Create a minimal version that doesn't load heavy components
        from app.rules.smart_rag_manager import get_cache_stats
        stats = get_cache_stats()
        minimal_time = time.time() - start_time
        print(f"   ✅ Minimal smart RAG: {minimal_time:.3f}s")
        print(f"   📊 Stats: {stats}")
        
    except Exception as e:
        print(f"   ❌ Minimal smart RAG failed: {e}")
    
    # Test 3: Check what's causing the delay in regular import
    print("\n3️⃣ Testing regular import with timing...")
    
    components = [
        ("BeautifulSoup", "from bs4 import BeautifulSoup"),
        ("regex", "import re"),
        ("html", "import html"),
        ("spacy_utils", "from app.rules.spacy_utils import get_nlp_model"),
        ("smart_rag_manager", "from app.rules.smart_rag_manager import get_smart_rag_suggestion"),
    ]
    
    for name, import_stmt in components:
        start_time = time.time()
        try:
            exec(import_stmt)
            comp_time = time.time() - start_time
            status = "🟢" if comp_time < 1 else "🟡" if comp_time < 5 else "🔴"
            print(f"   {status} {name}: {comp_time:.3f}s")
        except Exception as e:
            print(f"   ❌ {name}: FAILED - {e}")

if __name__ == "__main__":
    test_isolated_components()

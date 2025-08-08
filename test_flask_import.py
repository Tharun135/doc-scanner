"""
Test what happens when we import the Flask app vs rule directly
"""

import time
import sys
import os

def test_flask_app_import():
    """Test importing the Flask app to see if that's causing the delay."""
    print("🔍 TESTING FLASK APP IMPORT TIMING")
    print("=" * 50)
    
    # Test 1: Import just the app module
    start_time = time.time()
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        import app
        elapsed = time.time() - start_time
        print(f"✅ Flask app import: {elapsed:.3f}s")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Flask app import failed ({elapsed:.3f}s): {e}")
    
    # Test 2: Import rule through importlib (like the app does)
    start_time = time.time()
    try:
        import importlib.util
        rules_dir = os.path.join(os.path.dirname(__file__), 'app', 'rules')
        spec = importlib.util.spec_from_file_location(
            "technical_terms_clean", 
            os.path.join(rules_dir, "technical_terms_clean.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        elapsed = time.time() - start_time
        print(f"✅ Importlib import: {elapsed:.3f}s")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Importlib import failed ({elapsed:.3f}s): {e}")
    
    # Test 3: Direct import from rules directory
    start_time = time.time()
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'rules'))
        import technical_terms_clean
        elapsed = time.time() - start_time
        print(f"✅ Direct rules import: {elapsed:.3f}s")
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Direct rules import failed ({elapsed:.3f}s): {e}")

if __name__ == "__main__":
    test_flask_app_import()

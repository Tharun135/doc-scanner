"""
Test importing ONLY the clean rule first, before any other imports
"""

import time
import sys
import os

def test_clean_rule_first():
    """Test importing the clean rule FIRST, before any Flask or other imports."""
    print("🧪 TESTING CLEAN RULE IMPORT FIRST")
    print("=" * 50)
    
    # Test 1: Import clean rule directly (no Flask)
    print("\n1️⃣ Direct clean rule import (no Flask)...")
    start_time = time.time()
    
    try:
        # Add ONLY the rules directory
        rules_path = os.path.join(os.path.dirname(__file__), 'app', 'rules')
        sys.path.insert(0, rules_path)
        
        import technical_terms_clean
        elapsed = time.time() - start_time
        print(f"   ✅ Direct clean import: {elapsed:.3f}s")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ Direct clean import failed ({elapsed:.3f}s): {e}")
    
    # Test 2: Clear modules and try Flask import
    print("\n2️⃣ Clearing modules and testing Flask import...")
    
    # Clear ALL imported modules related to our app
    modules_to_clear = [mod for mod in sys.modules.keys() if 'technical_terms' in mod or 'app.' in mod]
    for mod in modules_to_clear:
        del sys.modules[mod]
    
    start_time = time.time()
    try:
        # Add app directory
        app_path = os.path.join(os.path.dirname(__file__), 'app')
        if app_path not in sys.path:
            sys.path.append(app_path)
        
        from app.rules.technical_terms_clean import check
        elapsed = time.time() - start_time
        print(f"   📊 Flask clean import: {elapsed:.3f}s")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ Flask clean import failed ({elapsed:.3f}s): {e}")

if __name__ == "__main__":
    test_clean_rule_first()

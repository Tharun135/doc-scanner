"""
Test Clean Rule Performance - TRUE ISOLATED TEST
"""

import time
import sys
import os

def test_true_isolated_performance():
    """Test importing rules in truly isolated way."""
    print("🔬 TESTING TRULY ISOLATED PERFORMANCE")
    print("=" * 50)
    
    # Test 1: Add only rules directory to path (no app directory)
    print("\n1️⃣ Testing ISOLATED clean rule import...")
    start_time = time.time()
    
    try:
        # Add ONLY the rules directory to path
        rules_path = os.path.join(os.path.dirname(__file__), 'app', 'rules')
        if rules_path not in sys.path:
            sys.path.insert(0, rules_path)
        
        # Import directly from rules directory
        import technical_terms_clean
        import_time = time.time() - start_time
        print(f"   ✅ Isolated import: {import_time:.3f}s")
        
        # Test execution
        start_time = time.time()
        test_content = "JSON, HTML and api files need proper formatting."
        suggestions = technical_terms_clean.check(test_content)
        exec_time = time.time() - start_time
        print(f"   ✅ Isolated execution: {exec_time:.3f}s")
        print(f"   📝 Suggestions: {len(suggestions)}")
        for suggestion in suggestions[:3]:
            print(f"      - {suggestion}")
        
    except Exception as e:
        print(f"   ❌ Isolated test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Import through app system for comparison
    print("\n2️⃣ Testing through Flask app system...")
    start_time = time.time()
    
    try:
        # Add app directory to path
        app_path = os.path.join(os.path.dirname(__file__), 'app')
        if app_path not in sys.path:
            sys.path.append(app_path)
        
        # Remove the module if already imported to force re-import
        if 'app.rules.technical_terms_clean' in sys.modules:
            del sys.modules['app.rules.technical_terms_clean']
        
        from app.rules.technical_terms_clean import check
        import_time = time.time() - start_time
        print(f"   📊 Flask app import: {import_time:.3f}s")
        
        start_time = time.time()
        suggestions = check(test_content)
        exec_time = time.time() - start_time
        print(f"   📊 Flask app execution: {exec_time:.3f}s")
        print(f"   📝 Suggestions: {len(suggestions)}")
        
    except Exception as e:
        print(f"   ❌ Flask app test failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n🎯 PERFORMANCE COMPARISON:")
    print("   If isolated import is fast but Flask app import is slow,")
    print("   the issue is in Flask app module initialization")

if __name__ == "__main__":
    test_true_isolated_performance()

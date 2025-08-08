"""
Test Clean Rule Performance - Test rule without any AI dependencies
"""

import time
import sys
import os

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_clean_rule_performance():
    """Test the completely clean rule performance."""
    print("🧪 TESTING CLEAN RULE PERFORMANCE")
    print("=" * 50)
    
    # Test 1: Clean rule import
    print("\n1️⃣ Testing clean rule import...")
    start_time = time.time()
    
    try:
        from app.rules.technical_terms_clean import check
        import_time = time.time() - start_time
        print(f"   ✅ Clean import: {import_time:.3f}s")
        
        # Test execution
        start_time = time.time()
        test_content = "JSON, HTML and api files need proper formatting."
        suggestions = check(test_content)
        exec_time = time.time() - start_time
        print(f"   ✅ Clean execution: {exec_time:.3f}s")
        print(f"   📝 Suggestions: {len(suggestions)}")
        for suggestion in suggestions[:3]:
            print(f"      - {suggestion}")
        
    except Exception as e:
        print(f"   ❌ Clean rule failed: {e}")
    
    # Test 2: Compare with original rule
    print("\n2️⃣ Testing original rule import...")
    start_time = time.time()
    
    try:
        from app.rules.technical_terms import check as check_original
        import_time = time.time() - start_time
        print(f"   📊 Original import: {import_time:.3f}s")
        
        start_time = time.time()
        suggestions = check_original(test_content)
        exec_time = time.time() - start_time
        print(f"   📊 Original execution: {exec_time:.3f}s")
        print(f"   📝 Suggestions: {len(suggestions)}")
        
    except Exception as e:
        print(f"   ❌ Original rule failed: {e}")
    
    print(f"\n🎯 CONCLUSION:")
    print(f"   If clean import is fast but original is slow,")
    print(f"   the issue is in the dependency chain.")

if __name__ == "__main__":
    test_clean_rule_performance()

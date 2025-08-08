"""
Test importing clean rule WITHOUT Flask app context
"""

import time
import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_direct_import():
    """Test importing the clean rule directly without Flask context."""
    print("🔍 TESTING DIRECT IMPORT (No Flask)")
    print("=" * 40)
    
    start_time = time.time()
    
    try:
        # Import directly without Flask app
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app', 'rules'))
        import technical_terms_clean
        
        elapsed = time.time() - start_time
        print(f"✅ Direct import successful: {elapsed:.3f}s")
        
        # Test the rule execution
        start_exec = time.time()
        test_text = "Make sure to use json and html properly in your api calls."
        result = technical_terms_clean.check(test_text)
        exec_time = time.time() - start_exec
        
        print(f"✅ Rule execution: {exec_time:.3f}s")
        print(f"📊 Total time: {elapsed + exec_time:.3f}s")
        
        if elapsed > 5:
            print(f"\n🔴 STILL SLOW - Issue is in the rule file itself")
            print(f"    Need to investigate what's in technical_terms_clean.py")
        else:
            print(f"\n🟢 FAST - Issue was Flask app context")
            
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_import()

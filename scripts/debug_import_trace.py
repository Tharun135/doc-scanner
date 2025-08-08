"""
Debug Import Tracing - Find what's causing the slow import
"""

import time
import sys
import os
import traceback

# Enable import tracing
original_import = __builtins__.__import__

def trace_import(name, globals=None, locals=None, fromlist=(), level=0):
    """Trace all imports and their timing."""
    start_time = time.time()
    try:
        result = original_import(name, globals, locals, fromlist, level)
        elapsed = time.time() - start_time
        
        # Only print slow imports (>1 second)
        if elapsed > 1.0:
            print(f"🐌 SLOW IMPORT: {name} ({elapsed:.3f}s)")
        elif elapsed > 0.1:
            print(f"⚠️  MEDIUM: {name} ({elapsed:.3f}s)")
        
        return result
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ FAILED: {name} ({elapsed:.3f}s) - {e}")
        raise

def test_with_import_tracing():
    """Test import with detailed tracing to find the bottleneck."""
    print("🕵️ IMPORT TRACING - FINDING THE BOTTLENECK")
    print("=" * 60)
    
    # Enable import tracing
    __builtins__.__import__ = trace_import
    
    try:
        print("\n📌 Starting Flask app import with tracing...")
        start_time = time.time()
        
        # Add app to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
        
        # This is the slow import
        from app.rules.technical_terms_clean import check
        
        elapsed = time.time() - start_time
        print(f"\n✅ TOTAL IMPORT TIME: {elapsed:.3f}s")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ IMPORT FAILED ({elapsed:.3f}s): {e}")
        traceback.print_exc()
    finally:
        # Restore original import
        __builtins__.__import__ = original_import

if __name__ == "__main__":
    test_with_import_tracing()

"""
Minimal System Test - Test basic Python imports to identify system issues
"""

import time

def test_basic_imports():
    """Test basic imports to identify system bottlenecks."""
    print("⚡ TESTING BASIC SYSTEM IMPORTS")
    print("=" * 40)
    
    basic_imports = [
        ("time", "import time"),
        ("os", "import os"),
        ("sys", "import sys"),
        ("re", "import re"),
        ("json", "import json"),
        ("html", "import html"),
        ("BeautifulSoup", "from bs4 import BeautifulSoup"),
    ]
    
    total_time = 0
    
    for name, import_stmt in basic_imports:
        start_time = time.time()
        try:
            exec(import_stmt)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            if elapsed > 5:
                status = "🔴 VERY SLOW"
            elif elapsed > 1:
                status = "🟡 SLOW"
            else:
                status = "🟢 OK"
                
            print(f"   {status} {name}: {elapsed:.3f}s")
        except Exception as e:
            print(f"   ❌ {name}: FAILED - {e}")
    
    print(f"\n📊 Total basic imports: {total_time:.3f}s")
    
    if total_time > 20:
        print(f"\n🚨 SYSTEM ISSUE DETECTED!")
        print(f"   Basic imports should take <1s total")
        print(f"   Possible causes:")
        print(f"   - Antivirus scanning Python files")
        print(f"   - Network timeouts during imports")
        print(f"   - Disk I/O performance issues")
        print(f"   - Python environment corruption")
    elif total_time > 5:
        print(f"\n⚠️ MODERATE SYSTEM SLOWDOWN")
        print(f"   Consider checking system performance")
    else:
        print(f"\n✅ System imports are normal")
        print(f"   Issue is likely in our application code")

if __name__ == "__main__":
    test_basic_imports()

#!/usr/bin/env python3
"""
Fresh test of the OllamaRewriter with updated timeouts
"""
# Force clear the module cache
import sys
import os

# Remove cached modules
modules_to_remove = [mod for mod in sys.modules.keys() if 'app.rewriter' in mod or mod.startswith('app.rewriter')]
for mod in modules_to_remove:
    del sys.modules[mod]

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now import fresh
from app.rewriter.ollama_rewriter import OllamaRewriter

def test_fresh_rewriter():
    print("🧪 Testing Fresh OllamaRewriter (no cache)")
    print("=" * 50)
    
    # Create rewriter instance
    rewriter = OllamaRewriter()
    print(f"Timeouts configured: {rewriter.timeouts}")
    
    # Test text
    original_text = "The implementation of advanced methodologies necessitates comprehensive understanding of complex organizational dynamics."
    print(f"\nOriginal text: {original_text}")
    print(f"Length: {len(original_text)} characters")
    
    try:
        print("\n🔄 Testing rewriter...")
        result = rewriter.rewrite_document(original_text, mode='simplicity')
        
        print(f"\n✅ Success: {result['success']}")
        print(f"📝 Rewritten text: {result['rewritten_text']}")
        
        # Check if text was actually changed
        if result['rewritten_text'] != original_text:
            print("🎉 SUCCESS: Text was actually rewritten!")
            print(f"📊 Improvement: {result['improvements']}")
        else:
            print("⚠️ WARNING: Rewritten text is identical to original")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fresh_rewriter()

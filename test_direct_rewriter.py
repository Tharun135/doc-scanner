#!/usr/bin/env python3
"""
Direct test of the OllamaRewriter class to verify our fixes work
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rewriter.ollama_rewriter import OllamaRewriter

def test_direct_rewriter():
    print("🧪 Testing OllamaRewriter Directly")
    print("=" * 50)
    
    # Test text
    original_text = "The implementation of advanced methodologies necessitates comprehensive understanding of complex organizational dynamics."
    print(f"Original text: {original_text}")
    print(f"Length: {len(original_text)} characters")
    
    # Create rewriter instance
    rewriter = OllamaRewriter()
    
    try:
        print("\n🔄 Testing rewriter...")
        result = rewriter.rewrite_document(original_text)
        
        print(f"\n✅ Success: {result['success']}")
        print(f"📝 Rewritten text: {result['rewritten_text']}")
        print(f"📊 Improvements: {result['improvements']}")
        
        # Check if text was actually changed
        if result['rewritten_text'] != original_text:
            print("🎉 SUCCESS: Text was actually rewritten!")
        else:
            print("⚠️ WARNING: Rewritten text is identical to original")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_rewriter()

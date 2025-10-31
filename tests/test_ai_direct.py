import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔧 Testing AI improvement function directly...")

try:
    # Import the function directly - this should trigger our debug prints
    print("🔧 About to import from ai_improvement...")
    from app.ai_improvement import get_enhanced_ai_suggestion
    print("🔧 Import successful, calling function...")
    
    result = get_enhanced_ai_suggestion(
        feedback_text="passive voice",
        sentence_context="This is a passive voice sentence that was written.",
        document_type="general",
        option_number=1
    )
    
    print(f"🔧 Result: {result}")
    print(f"🔧 Method: {result.get('method', 'unknown')}")
    
except Exception as e:
    print(f"🔧 Error: {e}")
    import traceback
    traceback.print_exc()

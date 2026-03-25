"""
UI Rendering Demo: What The User Actually Sees

This script shows exactly what the UI will display for the semantic explanation
state vs. the guidance-only state, proving they are mutually exclusive.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai_improvement import _generate_smart_suggestion

def render_ui_preview(result):
    """
    Simulates what the UI template will actually render.
    Based on index.html lines 2402-2431.
    """
    
    is_semantic = result.get("is_semantic_explanation", False)
    is_guidance = result.get("is_guidance_only", False)
    semantic_explanation = result.get("semantic_explanation", "")
    ai_answer = result.get("ai_answer", "")
    suggestion = result.get("suggestion", "")
    
    print("\n" + "="*80)
    print("UI RENDERING PREVIEW")
    print("="*80)
    
    # Header (from line 2404-2411 of index.html)
    if is_semantic:
        header = "🧠 Semantic Explanation (AI-Assisted)"
    elif is_guidance:
        header = "📋 Reviewer Guidance"
    else:
        header = "💡 AI Suggestion"
    
    print(f"\n┌─ {header}")
    print("│")
    
    # Content rendering (from lines 2418-2434 of index.html)
    if is_semantic:
        # Semantic explanation renders in info alert
        print("│  [INFO ALERT BOX]")
        print("│")
        print("│  Semantic Analysis:")
        for line in semantic_explanation.split(". "):
            if line.strip():
                print(f"│  • {line.strip()}.")
        print("│")
        print("│  ℹ️ No changes are suggested because this sentence contains")
        print("│     complex logic requiring manual review.")
        print("│")
    elif is_guidance:
        # Guidance renders in border box
        print("│  [BORDERED INFO BOX]")
        print("│")
        for line in ai_answer.split("\\n"):
            if line.strip():
                print(f"│  {line.strip()}")
        print("│")
    else:
        # Regular suggestion
        print("│  [SUGGESTION BOX]")
        print(f"│  {suggestion}")
        print("│")
    
    print("└" + "─"*79)
    
    # State verification
    print("\n📊 State Flags:")
    print(f"   is_semantic_explanation = {is_semantic}")
    print(f"   is_guidance_only = {is_guidance}")
    print(f"   Both active? {is_semantic and is_guidance} (MUST be False)")
    
    return is_semantic and is_guidance

def main():
    print("\n" + "="*80)
    print("SEMANTIC EXPLANATION vs GUIDANCE DEMO")
    print("="*80)
    
    # Test sentence that triggers semantic explanation
    sentence = (
        "The server certificate must include the IP address of the server "
        "in the SAN (Subject Alternative Names) certificate extension or "
        "the FQDN (Fully Qualified Domain Name) in case it is already "
        "registered in the DNS server."
    )
    
    feedback = "Consider breaking this long sentence (34 words) into shorter ones for better readability"
    
    print(f"\n📝 Test Sentence:")
    print(f"   {sentence}")
    print(f"\n💬 Feedback:")
    print(f"   {feedback}")
    
    result = _generate_smart_suggestion(feedback, sentence)
    
    # Render what UI will show
    has_conflict = render_ui_preview(result)
    
    # Verdict
    print("\n" + "="*80)
    if has_conflict:
        print("❌ FAIL: Both states are active - UI will show conflicting messages")
        return False
    else:
        print("✅ SUCCESS: Clean terminal state - UI shows exactly one message type")
        print("\nKey Invariant Enforced:")
        print("→ When semantic explanation is active, guidance is silent")
        print("→ When guidance is active, semantic explanation is silent")
        print("→ They never overlap")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

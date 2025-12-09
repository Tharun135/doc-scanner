#!/usr/bin/env python3
"""
Debug why AI suggestions are still copy-pasting original sentences
"""
import sys
sys.path.append('app')

from app.services.enrichment import enrich_issue_with_solution

def debug_ai_suggestions():
    print("🐛 DEBUGGING: Why AI suggestions copy-paste original sentences")
    print("=" * 70)
    
    # Test the exact case that's failing
    test_cases = [
        {
            "message": "Avoid passive voice in sentence: 'Tags are only defined for sensors.'",
            "context": "Tags are only defined for sensors.",
            "issue_type": "Passive Voice"
        },
        {
            "message": "Avoid passive voice in sentence: 'A data source has already been created.'",
            "context": "A data source has already been created.",
            "issue_type": "Passive Voice"
        }
    ]
    
    for i, issue in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {issue['issue_type']}")
        print(f"📝 Original: {issue['context']}")
        print(f"⚠️  Feedback: {issue['message']}")
        
        try:
            # Call the enrichment function directly
            enriched = enrich_issue_with_solution(issue.copy())
            
            original = issue['context']
            suggestion = enriched.get('proposed_rewrite', '')
            solution_text = enriched.get('solution_text', '')
            method = enriched.get('method', 'unknown')
            sources = enriched.get('sources', [])
            
            print(f"🔧 Method: {method}")
            print(f"💡 Solution Text: {solution_text[:100]}...")
            print(f"✨ Proposed Rewrite: {suggestion}")
            
            # Analyze what went wrong
            if suggestion == original:
                print("❌ PROBLEM: Suggestion identical to original!")
                print("🔍 Root cause analysis:")
                
                # Check if LLM was attempted
                if "llm" in method:
                    print("   - LLM was attempted but probably failed")
                elif "rag" in method:
                    print("   - Using RAG system, but rewrite generation failed")
                else:
                    print("   - Using fallback system only")
                
                # Check what the _force_change function should have done
                print("   - _force_change function should have modified this")
                print("   - But it's still returning the original - bug in _force_change!")
                
            elif "Revise for clarity:" in suggestion or "Improve clarity:" in suggestion:
                print("⚠️  PROBLEM: Using generic fallback instead of meaningful rewrite")
            else:
                print("✅ SUCCESS: Meaningful suggestion generated")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎯 DIAGNOSIS:")
    print("The issue is likely in one of these areas:")
    print("1. _force_change() not properly detecting identical suggestions")
    print("2. LLM system failing silently and returning original")
    print("3. Pattern matching in _create_deterministic_rewrite() not working")
    print("4. ChromaDB returning the original sentence as the 'improved' version")

if __name__ == "__main__":
    debug_ai_suggestions()

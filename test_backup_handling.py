#!/usr/bin/env python3
"""
Test the improved backup/back up handling.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.ai_improvement import EnhancedAISuggestionEngine
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

def test_backup_handling():
    """Test the improved backup/back up suggestions."""
    print("🧪 TESTING IMPROVED BACKUP/BACK UP HANDLING")
    print("=" * 60)
    
    engine = EnhancedAISuggestionEngine()
    
    test_cases = [
        {
            "name": "Correct noun usage - should NOT change",
            "feedback": "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.",
            "sentence": "Both options support backup files from the system"
        },
        {
            "name": "Incorrect verb usage - should change to 'back up'",
            "feedback": "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.",
            "sentence": "Remember to backup your data regularly"
        },
        {
            "name": "Another correct noun usage",
            "feedback": "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.",
            "sentence": "The backup system creates daily snapshots"
        },
        {
            "name": "Another incorrect verb usage",
            "feedback": "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.",
            "sentence": "You should backup all important documents"
        },
        {
            "name": "Correct adjective usage",
            "feedback": "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.",
            "sentence": "Create a backup strategy for your organization"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Original: {test_case['sentence']}")
        print(f"Feedback: {test_case['feedback']}")
        
        try:
            result = engine.generate_smart_fallback_suggestion(
                test_case['feedback'], 
                test_case['sentence']
            )
            
            print(f"✅ Result:")
            print(f"   Suggestion: {result['suggestion']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Method: {result['method']}")
            
            # Check if it contains corrected text
            if "CORRECTED TEXT:" in result['suggestion']:
                lines = result['suggestion'].split('\n')
                corrected_line = [line for line in lines if line.startswith("CORRECTED TEXT:")][0]
                corrected_text = corrected_line.replace("CORRECTED TEXT:", "").strip().strip('"')
                print(f"   ✨ Corrected Text: {corrected_text}")
                
                # Analyze the result
                original = test_case['sentence']
                if corrected_text == original:
                    print(f"   📝 Analysis: No change made (correct)")
                elif "back up" in corrected_text and "backup" in original:
                    print(f"   📝 Analysis: Changed 'backup' to 'back up' (verb form)")
                else:
                    print(f"   📝 Analysis: Other change made")
                    
                # Check if the decision was correct
                is_noun_usage = any(pattern in original.lower() for pattern in [
                    "backup files", "backup system", "backup strategy", "backup data",
                    "support backup", "create backup", "the backup"
                ])
                
                is_verb_usage = any(pattern in original.lower() for pattern in [
                    "to backup", "should backup", "backup your", "backup all",
                    "remember to backup", "need to backup"
                ])
                
                if is_noun_usage and corrected_text == original:
                    print(f"   ✅ CORRECT: Properly identified noun/adjective usage")
                elif is_verb_usage and "back up" in corrected_text:
                    print(f"   ✅ CORRECT: Properly converted to verb form")
                elif is_noun_usage and corrected_text != original:
                    print(f"   ❌ INCORRECT: Should not have changed noun/adjective usage")
                elif is_verb_usage and "back up" not in corrected_text:
                    print(f"   ❌ INCORRECT: Should have converted to verb form")
                else:
                    print(f"   ⚠️  UNCLEAR: Manual review needed")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_backup_handling()

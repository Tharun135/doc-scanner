"""
Test script to verify AI suggestions use simple present tense.
Run this to confirm the fix is working correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.document_first_ai import DocumentFirstAIEngine

def test_simple_present_tense():
    """Test that AI suggestions use simple present tense."""
    
    print("=" * 80)
    print("TESTING AI SUGGESTION TENSE COMPLIANCE")
    print("=" * 80)
    print()
    
    # Test cases
    test_cases = [
        {
            "name": "Modal Verb Removal",
            "feedback": "Modal verbs may weaken procedural clarity",
            "sentence": "You can backup and restore the configurations of all connectors, including all created tags.",
            "avoid_phrases": ["has been", "have been", "it is imperative", "should be ensured"],
            "expect_verbs": ["back up", "restore", "backup", "restores"]
        },
        {
            "name": "Passive Voice Conversion",
            "feedback": "Passive voice detected",
            "sentence": "The available connectors are shown by the application.",
            "avoid_phrases": ["has been", "have been", "were shown"],
            "expect_verbs": ["displays", "shows", "display", "show"]
        },
        {
            "name": "Long Sentence Split",
            "feedback": "Sentence too long",
            "sentence": "You can create a new asset with all required parameters and settings that have been configured.",
            "avoid_phrases": ["has been", "have been", "have configured", "has configured"],
            "expect_verbs": ["create", "creates", "configure", "configures"]
        }
    ]
    
    engine = DocumentFirstAIEngine()
    
    if engine.document_count == 0:
        print("⚠️  WARNING: No documents in knowledge base")
        print("The AI will use fallback mode (Ollama LLM)")
        print()
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'=' * 80}")
        print(f"Feedback: {test['feedback']}")
        print(f"Original: {test['sentence']}")
        print()
        
        try:
            result = engine.generate_document_first_suggestion(
                feedback_text=test['feedback'],
                sentence_context=test['sentence'],
                document_type="technical"
            )
            
            suggestion = result.get('suggestion', '')
            method = result.get('method', 'unknown')
            confidence = result.get('confidence', 'unknown')
            
            print(f"Method: {method}")
            print(f"Confidence: {confidence}")
            print(f"AI Suggestion: {suggestion}")
            print()
            
            # Check for violations
            violations = []
            for phrase in test['avoid_phrases']:
                if phrase.lower() in suggestion.lower():
                    violations.append(f"❌ Contains forbidden phrase: '{phrase}'")
            
            # Check if any expected verbs are present (at least one should be)
            has_expected_verb = any(verb.lower() in suggestion.lower() for verb in test['expect_verbs'])
            
            if violations:
                print("VIOLATIONS FOUND:")
                for v in violations:
                    print(f"  {v}")
                print("❌ TEST FAILED")
                failed += 1
            elif not has_expected_verb:
                print(f"⚠️  WARNING: None of the expected verbs found: {test['expect_verbs']}")
                print("❌ TEST FAILED")
                failed += 1
            else:
                print("✅ TEST PASSED - Uses simple present tense")
                passed += 1
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            print(traceback.format_exc())
            failed += 1
    
    # Summary
    print()
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {len(test_cases)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print()
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! AI suggestions use simple present tense.")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED. Please review the AI prompt configuration.")
        return 1

if __name__ == "__main__":
    exit_code = test_simple_present_tense()
    sys.exit(exit_code)

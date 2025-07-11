#!/usr/bin/env python3
"""
Comprehensive test for backup/back up handling
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.ai_improvement import EnhancedAISuggestionEngine

def test_backup_comprehensive():
    """Comprehensive test for backup/back up cases"""
    ai = EnhancedAISuggestionEngine()
    
    test_cases = [
        # Cases where "backup" should NOT change (noun/adjective usage)
        {
            "sentence": "Both options support backup files from the",
            "feedback": "Use 'back up' as a verb: 'back up your files' instead of 'backup your files'.",
            "should_change": False,
            "description": "Noun usage: backup files"
        },
        {
            "sentence": "The backup process takes several hours",
            "feedback": "backup terminology",
            "should_change": False,
            "description": "Noun usage: backup process"
        },
        {
            "sentence": "Create a backup copy of the database",
            "feedback": "backup vs back up",
            "should_change": False,
            "description": "Adjective usage: backup copy"
        },
        {
            "sentence": "We provide backup and restore functionality",
            "feedback": "backup terminology",
            "should_change": False,
            "description": "Noun usage: backup and restore"
        },
        
        # Cases where "backup" SHOULD change to "back up" (verb usage)
        {
            "sentence": "Remember to backup your files regularly",
            "feedback": "Use 'back up' as a verb",
            "should_change": True,
            "description": "Verb usage: to backup"
        },
        {
            "sentence": "Please backup the database before proceeding",
            "feedback": "backup terminology",
            "should_change": True,
            "description": "Verb usage: imperative backup"
        },
        {
            "sentence": "You should backup your data weekly",
            "feedback": "backup vs back up",
            "should_change": True,
            "description": "Verb usage: should backup"
        },
        {
            "sentence": "Don't forget to backup all critical files",
            "feedback": "backup terminology",
            "should_change": True,
            "description": "Verb usage: to backup"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"=== Test Case {i}: {test_case['description']} ===")
        print(f"Sentence: '{test_case['sentence']}'")
        print(f"Feedback: '{test_case['feedback']}'")
        print(f"Expected: {'Should change' if test_case['should_change'] else 'Should NOT change'}")
        
        result = ai.generate_contextual_suggestion(test_case['feedback'], test_case['sentence'])
        
        # Check if the suggestion indicates a change was made
        suggestion = result['suggestion']
        changed = "back up" in suggestion and test_case['sentence'] not in suggestion
        
        print(f"Result: {'Changed' if changed else 'No change'}")
        print(f"Method: {result['method']}")
        print(f"Suggestion: {suggestion}")
        
        # Verify correctness
        if test_case['should_change'] == changed:
            print("✅ CORRECT")
        else:
            print("❌ INCORRECT")
        
        print("-" * 60)

if __name__ == "__main__":
    test_backup_comprehensive()

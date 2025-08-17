#!/usr/bin/env python3
"""
Final comprehensive test of the improved formatting rule
"""

from app.rules.formatting_fixed import check as check_formatting

def final_comprehensive_test():
    print("=== FINAL COMPREHENSIVE TEST ===\n")
    
    test_cases = [
        # Should be ALLOWED (list-like content)
        {
            "text": "The WinCC Unified Runtime app must be running .",
            "expected": "ALLOW",
            "category": "User's example 1"
        },
        {
            "text": "A project must be added as described in Add Project .",
            "expected": "ALLOW", 
            "category": "User's example 2"
        },
        {
            "text": "Download the software .",
            "expected": "ALLOW",
            "category": "Action instruction"
        },
        {
            "text": "The application will start automatically .",
            "expected": "ALLOW",
            "category": "Technical description"
        },
        
        # Should be FLAGGED (conversational/narrative text)
        {
            "text": "Hello , world",
            "expected": "FLAG",
            "category": "Greeting with comma error"
        },
        {
            "text": "I think , therefore I am .",
            "expected": "FLAG",
            "category": "Philosophical statement"
        },
        {
            "text": "The meeting ended early . Everyone left.",
            "expected": "FLAG",
            "category": "Narrative text"
        },
        {
            "text": "What ? This should be flagged.",
            "expected": "FLAG",
            "category": "Question with error"
        },
        
        # Edge cases
        {
            "text": "This is wrong . It's not a list item.",
            "expected": "FLAG",
            "category": "Regular sentence starting with 'This'"
        },
    ]
    
    print("Testing individual sentences:\n")
    
    correct_count = 0
    total_count = len(test_cases)
    
    for i, case in enumerate(test_cases, 1):
        text = case["text"]
        expected = case["expected"]
        category = case["category"]
        
        results = check_formatting(text)
        space_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
        
        is_flagged = len(space_issues) > 0
        actual = "FLAG" if is_flagged else "ALLOW"
        
        is_correct = (actual == expected)
        status = "✅" if is_correct else "❌"
        
        print(f"{i:2d}. {status} {category}")
        print(f"    Text: '{text}'")
        print(f"    Expected: {expected}, Actual: {actual}")
        
        if is_flagged:
            print(f"    Issues: {len(space_issues)}")
            for issue in space_issues:
                print(f"      - '{issue['text']}' at {issue['start']}-{issue['end']}")
        
        if is_correct:
            correct_count += 1
        
        print()
    
    accuracy = (correct_count / total_count) * 100
    print("=" * 50)
    print(f"RESULTS: {correct_count}/{total_count} correct ({accuracy:.1f}% accuracy)")
    
    if accuracy >= 90:
        print("✅ EXCELLENT: Rule is working very well!")
    elif accuracy >= 80:
        print("✅ GOOD: Rule is working well with minor issues")
    else:
        print("❌ NEEDS IMPROVEMENT: Rule needs further refinement")

if __name__ == "__main__":
    final_comprehensive_test()

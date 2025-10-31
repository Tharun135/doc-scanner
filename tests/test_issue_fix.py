#!/usr/bin/env python3
"""
Test script specifically for the reported issue: 'ie/d/j/simatic/v1/slmp1/dp/r//default'
"""

import sys
import os

# Add the current directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

from app.rules.grammar_rules import check

def test_specific_issue():
    """Test the exact issue reported by the user"""
    
    # The exact text from the issue
    test_text = "ie/d/j/simatic/v1/slmp1/dp/r//default"
    
    print("Testing specific issue...")
    print("=" * 50)
    print(f"Input text: '{test_text}'")
    
    # Run the grammar check
    suggestions = check(test_text)
    
    # Filter for capital letter suggestions
    capital_suggestions = [s for s in suggestions if "Start sentences with a capital letter" in s]
    
    print(f"Total suggestions: {len(suggestions)}")
    print(f"Capital letter suggestions: {len(capital_suggestions)}")
    
    if capital_suggestions:
        print("❌ ISSUE STILL EXISTS - Capital letter suggestions found:")
        for suggestion in capital_suggestions:
            print(f"  - {suggestion}")
        return False
    else:
        print("✅ ISSUE FIXED - No capital letter suggestions for technical code!")
        
        # Print any other suggestions that might exist
        if suggestions:
            print("\nOther suggestions (non-capital related):")
            for suggestion in suggestions:
                print(f"  - {suggestion}")
        else:
            print("No suggestions at all - perfect!")
        
        return True

def test_similar_technical_codes():
    """Test similar technical codes to ensure robustness"""
    
    technical_codes = [
        "ie/d/j/simatic/v1/slmp1/dp/r//default",
        "api/v2/auth/login",
        "src/main/java/com/example",
        "config/database/production.yml",
        "lib/utils/string-helpers.js",
        "docs/api/reference/endpoints",
        "app/models/user/profile.rb",
    ]
    
    print("\nTesting similar technical codes...")
    print("=" * 50)
    
    all_passed = True
    
    for code in technical_codes:
        suggestions = check(code)
        capital_suggestions = [s for s in suggestions if "Start sentences with a capital letter" in s]
        
        if capital_suggestions:
            print(f"❌ '{code}' - Still triggers capital letter rule")
            all_passed = False
        else:
            print(f"✅ '{code}' - Correctly excluded")
    
    return all_passed

if __name__ == "__main__":
    print("Capital Letter Rule Fix - Issue Verification")
    print("=" * 60)
    
    issue_fixed = test_specific_issue()
    similar_codes_work = test_similar_technical_codes()
    
    print("\n" + "=" * 60)
    if issue_fixed and similar_codes_work:
        print("🎉 SUCCESS: The issue has been completely resolved!")
        print("Technical codes are now properly excluded from capital letter checks.")
    else:
        print("❌ The fix needs more work - some cases still fail.")

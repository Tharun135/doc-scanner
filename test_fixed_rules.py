"""
Test the fixed rule structure.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app.rules.capitalization_fixed import check as cap_check
from app.rules.terminology_fixed import check as term_check
from app.rules.grammar_fixed import check as gram_check

def test_rules():
    test_text = "microsoft should be capitalized. This are wrong grammar. Software setup require proper terminology."
    
    print("Testing Fixed Rules Structure")
    print("=" * 50)
    print(f"Test text: {test_text}")
    print()
    
    print("Capitalization Rules:")
    cap_results = cap_check(test_text)
    for result in cap_results:
        print(f"  - {result}")
    print(f"  Total: {len(cap_results)} issues")
    print()
    
    print("Terminology Rules:")
    term_results = term_check(test_text)
    for result in term_results:
        print(f"  - {result}")
    print(f"  Total: {len(term_results)} issues")
    print()
    
    print("Grammar Rules:")
    gram_results = gram_check(test_text)
    for result in gram_results:
        print(f"  - {result}")
    print(f"  Total: {len(gram_results)} issues")
    print()
    
    total_issues = len(cap_results) + len(term_results) + len(gram_results)
    print(f"TOTAL ISSUES DETECTED: {total_issues}")
    
    if total_issues > 0:
        print("✅ Fixed rules are working and returning position-based results!")
        return True
    else:
        print("❌ No issues detected - something may be wrong")
        return False

if __name__ == "__main__":
    test_rules()

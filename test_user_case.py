"""Quick test to verify the user's specific case is fixed"""
from app.rules.simple_present_normalization import is_non_sentential, check

# Test cases
test_cases = [
    ("Configuring KEPware server with certificates", True, "User's original case"),
    ("Installing the software", True, "Gerund phrase title"),
    ("System Configuration", True, "Noun phrase title"),
    ("The system configured the server.", False, "Complete past-tense sentence"),
    ("Click the Configure button to open the settings.", False, "Complete imperative sentence"),
    ("Setup Prerequisites", True, "Short noun phrase"),
]

print("Testing non-sentential detection:")
print("=" * 80)

all_passed = True
for text, expected_is_title, description in test_cases:
    is_title = is_non_sentential(text)
    status = "✓" if is_title == expected_is_title else "✗"
    expected_str = "TITLE" if expected_is_title else "SENTENCE"
    actual_str = "TITLE" if is_title else "SENTENCE"
    
    print(f"{status} {description}")
    print(f"  Text: '{text}'")
    print(f"  Expected: {expected_str:10s} | Actual: {actual_str:10s}")
    
    if is_title == expected_is_title:
        # Also test that check() returns no issues for titles
        if is_title:
            issues = check(text)
            if len(issues) == 0:
                print(f"  ✓ check() correctly returns no issues for title")
            else:
                print(f"  ✗ check() incorrectly flagged title: {issues}")
                all_passed = False
    else:
        all_passed = False
    
    print()

print("=" * 80)
print(f"Overall: {'PASSED' if all_passed else 'FAILED'}")

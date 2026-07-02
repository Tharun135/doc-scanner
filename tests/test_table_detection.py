"""
Test script to verify table row detection in long_sentence rule.
"""

from app.rules.long_sentence import _is_table_row, check

# Test cases
test_cases = [
    # Table rows (should return True)
    {
        "text": "| | 150K | 286.6 (57.32%) | Integrated with backend | 30670 |",
        "expected": True,
        "description": "Performance metrics table row"
    },
    {
        "text": "| 300K | 232.4 (46.48%) | Integrated with backend | 66720 |",
        "expected": True,
        "description": "Table row with data"
    },
    {
        "text": "| Name | Age | City | Country |",
        "expected": True,
        "description": "Table header"
    },
    {
        "text": "| --- | --- | --- | --- |",
        "expected": True,
        "description": "Table separator"
    },
    {
        "text": "| :--- | :---: | ---: |",
        "expected": True,
        "description": "Table separator with alignment"
    },
    
    # Normal sentences (should return False)
    {
        "text": "This is a normal sentence without any table markers.",
        "expected": False,
        "description": "Regular sentence"
    },
    {
        "text": "The value is | important, but this is not a table.",
        "expected": False,
        "description": "Sentence with one pipe"
    },
    {
        "text": "You can use the | operator in programming | to perform bitwise operations.",
        "expected": False,
        "description": "Sentence with two pipes (tech content)"
    },
    {
        "text": "Consider breaking this long sentence (85 words) into shorter ones for better readability.",
        "expected": False,
        "description": "Long sentence warning text"
    },
]

print("=" * 80)
print("TABLE ROW DETECTION TEST")
print("=" * 80)
print()

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    result = _is_table_row(test["text"])
    status = "✅ PASS" if result == test["expected"] else "❌ FAIL"
    
    if result == test["expected"]:
        passed += 1
    else:
        failed += 1
    
    print(f"Test {i}: {test['description']}")
    print(f"  Text: {test['text'][:60]}{'...' if len(test['text']) > 60 else ''}")
    print(f"  Expected: {test['expected']}, Got: {result}")
    print(f"  {status}")
    print()

print("=" * 80)
print(f"RESULTS: {passed}/{len(test_cases)} passed, {failed}/{len(test_cases)} failed")
print("=" * 80)
print()

# Test with actual content containing a table
print("=" * 80)
print("INTEGRATION TEST - Full Content with Table")
print("=" * 80)
print()

test_content = """
# Performance Results

Here are the test results:

| Tokens | Latency (% overhead) | Status | Time (ms) |
| --- | --- | --- | --- |
| 150K | 286.6 (57.32%) | Integrated with backend | 30670 |
| 300K | 232.4 (46.48%) | Integrated with backend | 66720 |
| 400K | 285.3 (57.06%) | Integrated with backend | 78000 |
| 500K | 296.4 (59.28%) | Integrated with backend | 114000 |

This demonstrates that the system performance degrades significantly as the token count increases.
"""

suggestions = check(test_content)

print("Content checked:")
print(test_content)
print()
print(f"Suggestions found: {len(suggestions)}")
for i, suggestion in enumerate(suggestions, 1):
    print(f"  {i}. {suggestion}")
print()

if len(suggestions) == 0:
    print("✅ SUCCESS: No table rows were flagged as long sentences!")
elif any("85 words" in s or "table" in s.lower() for s in suggestions):
    print("❌ FAIL: Table rows are still being flagged as long sentences")
else:
    print("✅ PARTIAL SUCCESS: Some suggestions found, but not from tables")

print()
print("=" * 80)

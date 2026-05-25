import requests
import re
import sys
import os

# 1. Test the regex extraction logic directly
print("Testing Regex Extraction Logic...")
feedback_text = 'Use lowercase in headings except for the first word and proper nouns. Words to lowercase: Common, Configurator. Suggested: "Launching common configurator on IEM"'
match = re.search(r'(?:Suggested|Suggestion|Replace with):\s*"(.*?)"', feedback_text, re.IGNORECASE)
if match:
    print("Regex Success! Extracted suggestion:", match.group(1))
    assert match.group(1) == "Launching common configurator on IEM"
else:
    print("Regex Failed to extract suggestion!")
    sys.exit(1)

# 2. Test live server suggestion
print("\nTesting Live API Suggestion...")
url = "http://127.0.0.1:5000/ai_suggestion"
data = {
    "sentence": "Launching Common Configurator on IEM",
    "issue_type": "SG-HE-002",
    "feedback": feedback_text
}

try:
    r = requests.post(url, json=data, timeout=60)
    print("Status Code:", r.status_code)
    print("Response JSON:")
    import json
    res = r.json()
    print(json.dumps(res, indent=2))
    if res.get("suggestion"):
        print("API Suggestion Success!")
    else:
        print("API Suggestion Failed!")
except Exception as e:
    print("Error:", e)

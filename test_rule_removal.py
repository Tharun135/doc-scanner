import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Test the document structure rules
from app.rules.document_structure import check

# Test content that would previously trigger both rules
test_content = """
<h1>This Is Title Case</h1>
<h2>This is sentence case</h2>
<h3>Another Title Case Heading</h3>

<p>This is some content.</p>




<p>Content after excessive blank lines.</p>
"""

print("🧪 Testing document structure rules after removal...")
print("=" * 50)

results = check(test_content)
print(f"Number of suggestions: {len(results)}")

for i, suggestion in enumerate(results, 1):
    print(f"{i}. {suggestion}")

if not results:
    print("✅ No suggestions found - rules successfully removed!")
else:
    # Check if the removed rules are still present
    removed_rules_found = []
    for suggestion in results:
        if "Mixed capitalization in headings" in suggestion:
            removed_rules_found.append("Mixed capitalization rule")
        if "Excessive blank lines" in suggestion:
            removed_rules_found.append("Excessive blank lines rule")
    
    if removed_rules_found:
        print(f"❌ These rules are still active: {removed_rules_found}")
    else:
        print("✅ Removed rules are no longer active!")
        print("ℹ️ Other document structure rules are still working as expected.")

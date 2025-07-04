import sys
sys.path.append('d:/doc-scanner')
from app.rules.can_may_terms import check

# Test the fixed rule with various "may" sentences
test_content = """
Loading the tags may take some time depending on the size of the export file.
You may access the settings page.
The process may require additional permissions.
Users may download files from this location.
This may vary depending on your configuration.
The operation may take several minutes to complete.
"""

results = check(test_content)
print("Rule check results:")
for i, result in enumerate(results):
    print(f"{i+1}. {result}")
    print()

if not results:
    print("✅ No issues detected - the fix is working!")
else:
    print(f"Found {len(results)} issues")

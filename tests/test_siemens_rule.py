import sys
sys.path.insert(0, '.')
from app.rules.siemens_style_rules import check

test_text = (
    "There is a configuration file that should be reviewed before proceeding. "
    "It is important to verify all settings before you begin. "
    "Furthermore, you should ensure that all dependencies are available. "
    "The process is simply a matter of copying files. "
    "Please click Save to store the configuration. "
    "Therefore, the deployment cant be completed without this step. "
    "The last version of the software is available for download."
)

result = check(test_text)
print("Issues found:", len(result))
for item in result:
    print("  [" + item["decision_type"] + "] " + item["message"])
    print("  Sentence: " + item["text"][:80])
    print()

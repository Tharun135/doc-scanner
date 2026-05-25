import os
import sys
import shutil

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Delete existing test cache if exists to ensure clean run
test_cache_db = os.path.join(os.getcwd(), 'style_suggestion_cache.db')
if os.path.exists(test_cache_db):
    try:
        os.remove(test_cache_db)
        print("Cleared existing style_suggestion_cache.db")
    except Exception as e:
        print(f"Could not clear cache DB: {e}")

from app.services.style_guide_service import (
    try_deterministic_rewrite, 
    get_cached_suggestion, 
    set_cached_suggestion,
    generate_style_suggestion
)

# Test 1: Contractions
sent1 = "Don't click Cancel if you aren't sure."
res1 = try_deterministic_rewrite(sent1, "contraction", "Avoid contractions.")
print("=== Test 1 (Contraction) ===")
print("Original:", sent1)
print("Result:", res1)
assert res1 is not None
assert "Do not" in res1["suggestion"]
assert "are not" in res1["suggestion"]

# Test 2: Click on
sent2 = "Click on the button to save."
res2 = try_deterministic_rewrite(sent2, "ui_labeling", "Avoid click on.")
print("\n=== Test 2 (Click on) ===")
print("Original:", sent2)
print("Result:", res2)
assert res2 is not None
assert "Click the button" in res2["suggestion"]

# Test 3: Filler word (simply)
sent3 = "Simply select the menu option."
res3 = try_deterministic_rewrite(sent3, "filler", "Avoid simply.")
print("\n=== Test 3 (Filler) ===")
print("Original:", sent3)
print("Result:", res3)
assert res3 is not None
assert "Select the menu option" in res3["suggestion"]

# Test 4: Persistent Caching
print("\n=== Test 4 (Caching) ===")
test_result = {
    "issue": "test_issue",
    "explanation": "Test explanation",
    "suggestion": "Test suggestion",
    "ai_answer": "Test Model",
    "confidence": "high",
    "prompt_version": "test_version"
}
set_cached_suggestion("Test sentence.", "test_type", "test_msg", test_result)
cached_res = get_cached_suggestion("Test sentence.", "test_type", "test_msg")
print("Cached Retrieval:", cached_res)
assert cached_res is not None
assert cached_res["suggestion"] == "Test suggestion"

print("\nAll tests passed successfully!")

"""
Test cases for TABLE rules (table formatting)
Rule expansion: 28 → 35
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.rules.matcher import apply_rules
from app.rules.loader import load_rules

def rule_hit(rule_id, text):
    """Check if a specific rule is triggered by text"""
    rules = load_rules()
    violations = apply_rules(text, rules)
    return any(v['rule_id'] == rule_id for v in violations)

def test_empty_cell():
    """TABLE_001: Empty table cell"""
    table = "| Value | Speed |\n|       | 1500  |"
    assert rule_hit("TABLE_001", table), "Should detect empty cell"

def test_merged_cells():
    """TABLE_002: Merged cells"""
    snippet = "<td colspan='2'>Header</td>"
    assert rule_hit("TABLE_002", snippet), "Should detect merged cells"

if __name__ == "__main__":
    print("Testing TABLE rules...")
    
    test_empty_cell()
    print("✅ TABLE_001: Empty cell - PASS")
    
    test_merged_cells()
    print("✅ TABLE_002: Merged cells - PASS")
    
    print("\n✅ All TABLE rule tests passed!")

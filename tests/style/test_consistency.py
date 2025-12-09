"""
Test cases for CONSIST rules (consistency)
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

def test_ui_verb_inconsistency():
    """CONSIST_001: UI verb capitalization inconsistency"""
    text = "Click Save. then select Exit."
    assert rule_hit("CONSIST_001", text), "Should detect inconsistent UI verb"

if __name__ == "__main__":
    print("Testing CONSIST rules...")
    
    test_ui_verb_inconsistency()
    print("✅ CONSIST_001: UI verb inconsistency - PASS")
    
    print("\n✅ All CONSIST rule tests passed!")

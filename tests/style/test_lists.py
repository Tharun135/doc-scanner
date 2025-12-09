"""
Test cases for LIST rules (procedure formatting)
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

def test_list_fusion():
    """LIST_001: Multiple actions in single step"""
    sentence = "Click Save and then restart."
    assert rule_hit("LIST_001", sentence), "Should detect multiple actions"

def test_colon_before_steps():
    """LIST_002: Colon before numbered steps"""
    text = "Steps:\n1. Click Save."
    assert rule_hit("LIST_002", text), "Should detect colon before steps"

if __name__ == "__main__":
    print("Testing LIST rules...")
    
    test_list_fusion()
    print("✅ LIST_001: Multiple actions - PASS")
    
    test_colon_before_steps()
    print("✅ LIST_002: Colon before steps - PASS")
    
    print("\n✅ All LIST rule tests passed!")

"""
Test cases for TRANS rules (translation constraints)
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

def test_idiom_detection():
    """TRANS_001: Idiom detection"""
    sentence = "At the end of the day, the device restarts."
    assert rule_hit("TRANS_001", sentence), "Should detect idiom"

def test_ambiguity_multiple():
    """TRANS_002: Ambiguous quantity"""
    sentence = "The device supports multiple modes."
    assert rule_hit("TRANS_002", sentence), "Should detect vague quantity"

if __name__ == "__main__":
    print("Testing TRANS rules...")
    
    test_idiom_detection()
    print("✅ TRANS_001: Idiom detection - PASS")
    
    test_ambiguity_multiple()
    print("✅ TRANS_002: Ambiguous quantity - PASS")
    
    print("\n✅ All TRANS rule tests passed!")

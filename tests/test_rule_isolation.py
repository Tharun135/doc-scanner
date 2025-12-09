#!/usr/bin/env python3
"""
Test script to isolate which rule is causing the 'No test named match' error.
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_individual_rules():
    """Test each rule individually to find the one causing the error."""
    
    # Import the rules
    try:
        sys.path.append('app')
        from rules import grammar_rules, passive_voice, long_sentence, consistency_rules, style_rules, terminology_rules, vague_terms
        
        rule_modules = [
            ('grammar_rules', grammar_rules),
            ('passive_voice', passive_voice),
            ('long_sentence', long_sentence),
            ('consistency_rules', consistency_rules),
            ('style_rules', style_rules),
            ('terminology_rules', terminology_rules),
            ('vague_terms', vague_terms)
        ]
        
        test_sentence = "The data can be processed by the system."
        
        print(f"Testing sentence: '{test_sentence}'")
        print("="*60)
        
        for rule_name, rule_module in rule_modules:
            print(f"\nTesting {rule_name}...")
            try:
                result = rule_module.check(test_sentence)
                print(f"  ✅ {rule_name}: Success - {len(result) if result else 0} suggestions")
            except Exception as e:
                print(f"  ❌ {rule_name}: ERROR - {e}")
                print(f"     Error type: {type(e).__name__}")
                if "No test named" in str(e) and "match" in str(e):
                    print(f"  🚨 FOUND THE CULPRIT! {rule_name} is causing the 'No test named match' error!")
                    import traceback
                    traceback.print_exc()
                    return rule_name
        
        print("\n✅ All rules tested - no 'No test named match' error found in individual tests")
        return None
        
    except Exception as e:
        print(f"❌ Error in test setup: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    culprit = test_individual_rules()
    if culprit:
        print(f"\n🎯 The error is coming from the {culprit} rule!")
    else:
        print(f"\n🤔 Error not found in individual rule tests - might be in rule interactions or analysis pipeline")
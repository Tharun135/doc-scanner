#!/usr/bin/env python3
"""
Debug script to isolate which rule causes the 'No test named match' error
This script tests each rule individually to find the source of the error.
"""
import os
import sys
import traceback

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_individual_rule_import(rule_name):
    """Test importing a single rule module"""
    try:
        print(f"\n🔧 Testing import of {rule_name}...")
        
        # Import the rule module
        rule_module = __import__(f'rules.{rule_name}', fromlist=[rule_name])
        print(f"✅ Successfully imported {rule_name}")
        
        # Check if it has a check function
        if hasattr(rule_module, 'check'):
            print(f"✅ {rule_name} has check function")
            
            # Try to call the check function with test data
            print(f"🔧 Testing check function of {rule_name}...")
            test_text = "This is a test sentence for validation."
            
            # Create a minimal doc-like object for spaCy rules
            class MockDoc:
                def __init__(self, text):
                    self.text = text
                    
            mock_doc = MockDoc(test_text)
            
            # Call the check function
            result = rule_module.check(mock_doc)
            print(f"✅ {rule_name}.check() executed successfully, returned: {type(result)}")
            
        else:
            print(f"⚠️ {rule_name} does not have check function")
            
    except Exception as e:
        print(f"❌ Error with {rule_name}: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        return False
    
    return True

def main():
    print("🔧 Debug: Testing individual rules for 'No test named match' error")
    print("=" * 60)
    
    # List of rule files to test (without .py extension)
    rule_files = [
        'consistency_rules',
        'grammar_rules', 
        'long_sentence',
        'passive_voice',
        'style_rules',
        'terminology_rules',
        'vague_terms'
    ]
    
    successful_rules = []
    failed_rules = []
    
    for rule_name in rule_files:
        success = test_individual_rule_import(rule_name)
        if success:
            successful_rules.append(rule_name)
        else:
            failed_rules.append(rule_name)
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY:")
    print(f"✅ Successful rules: {len(successful_rules)}")
    for rule in successful_rules:
        print(f"   - {rule}")
    
    print(f"❌ Failed rules: {len(failed_rules)}")
    for rule in failed_rules:
        print(f"   - {rule}")
    
    if failed_rules:
        print(f"\n🎯 Focus investigation on: {failed_rules}")
    else:
        print(f"\n🤔 All rules imported successfully - error might be elsewhere")

if __name__ == "__main__":
    main()
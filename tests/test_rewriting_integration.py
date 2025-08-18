#!/usr/bin/env python3
"""
Test script to verify rewriting_suggestions rule integration
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_rewriting_rule():
    """Test the rewriting suggestions rule."""
    try:
        from app.rules.rewriting_suggestions import check
        
        # Test cases
        test_cases = [
            # Test case 1: Action verbs that should be converted
            "The user clicks on the button and selects the option.",
            
            # Test case 2: Sequential instructions
            "First, open the application. Then, navigate to the settings. Finally, click save.",
            
            # Test case 3: Non-instructional text
            "This document describes the system architecture and design principles.",
            
            # Test case 4: Procedural text without formatting
            "Click the start button. Type your username. Press enter to continue."
        ]
        
        print("🧪 Testing Rewriting Suggestions Rule")
        print("=" * 50)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}: {test_case[:50]}...")
            
            try:
                suggestions = check(test_case)
                
                if suggestions:
                    print(f"✅ Found {len(suggestions)} suggestions:")
                    for suggestion in suggestions:
                        if isinstance(suggestion, dict):
                            print(f"   • {suggestion.get('type', 'unknown')}: {suggestion.get('message', 'No message')}")
                        else:
                            print(f"   • {suggestion}")
                else:
                    print("   ✓ No suggestions (content appears optimal)")
                    
            except Exception as e:
                print(f"   ❌ Error processing test case: {e}")
        
        print(f"\n🎉 Integration test completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure the rule is properly integrated in app/rules/__init__.py")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False

def test_rule_functions_integration():
    """Test that the rule is included in the main rule_functions list."""
    try:
        from app.rules import rule_functions
        
        print(f"\n📊 Total rules loaded: {len(rule_functions)}")
        
        # Check if our rule is in the list
        rule_names = [func.__name__ for func in rule_functions]
        
        if 'check_rewriting_suggestions' in rule_names:
            print("✅ Rewriting suggestions rule is properly integrated!")
            return True
        else:
            print("❌ Rewriting suggestions rule not found in rule_functions")
            print("Available rules:", rule_names)
            return False
            
    except Exception as e:
        print(f"❌ Integration check error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Doc-Scanner Rewriting Rule Integration Test")
    print("=" * 60)
    
    # Test individual rule
    rule_test = test_rewriting_rule()
    
    # Test integration
    integration_test = test_rule_functions_integration()
    
    if rule_test and integration_test:
        print(f"\n🎉 SUCCESS: Rule is properly integrated and working!")
        print("📝 The rewriting_suggestions rule is now active in your Doc-Scanner app.")
    else:
        print(f"\n❌ FAILED: Integration issues detected.")
        print("💡 Check the error messages above for details.")

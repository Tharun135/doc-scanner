#!/usr/bin/env python3
"""
Debug why list items are still being flagged for space before punctuation
"""

def test_full_application_flow():
    """Test the complete application flow to see where the issue comes from"""
    
    # Test text with list items that have spaces before punctuation
    test_text = """Prerequisites:
- The WinCC Unified Runtime app must be running .
- A project must be added as described in Add Project .
- The system must be configured properly ."""
    
    print("=== TESTING FULL APPLICATION FLOW ===")
    print(f"Test text:\n{test_text}\n")
    
    # Test 1: Direct formatting rule check
    print("1. TESTING DIRECT FORMATTING RULE:")
    try:
        from app.rules.formatting_fixed import check as check_formatting
        format_results = check_formatting(test_text)
        space_issues = [r for r in format_results if "space before punctuation" in r.get('message', '')]
        
        print(f"   Direct formatting check found {len(space_issues)} space issues:")
        for issue in space_issues:
            print(f"   - '{issue['text']}' at {issue['start']}-{issue['end']}")
        
        if not space_issues:
            print("   ✅ No space before punctuation issues found in direct check!")
        
    except Exception as e:
        print(f"   ❌ Error in direct formatting check: {e}")
    
    print()
    
    # Test 2: All rules check
    print("2. TESTING ALL RULES:")
    try:
        from app.rules import rule_functions
        all_issues = []
        
        for rule_func in rule_functions:
            try:
                results = rule_func(test_text)
                all_issues.extend(results)
            except Exception as e:
                print(f"   Error in rule {rule_func.__name__}: {e}")
        
        space_issues = [r for r in all_issues if "space before punctuation" in r.get('message', '')]
        print(f"   All rules found {len(space_issues)} space issues:")
        for issue in space_issues:
            print(f"   - '{issue['text']}' at {issue['start']}-{issue['end']}")
        
        if not space_issues:
            print("   ✅ No space before punctuation issues found in all rules!")
            
    except Exception as e:
        print(f"   ❌ Error in all rules check: {e}")
    
    print()
    
    # Test 3: Web endpoint simulation
    print("3. TESTING WEB ENDPOINT SIMULATION:")
    try:
        import requests
        import json
        
        # Try to simulate the web request
        data = {
            'content': test_text,
            'options': {
                'include_ai_suggestions': False
            }
        }
        
        # Note: This would need the server running, so let's just show what we'd test
        print("   Would test POST to /analyze with this data:")
        print(f"   {json.dumps(data, indent=2)}")
        
    except Exception as e:
        print(f"   Note: Web endpoint test would require running server")
    
    print()
    
    # Test 4: Check for other formatting functions
    print("4. CHECKING FOR OTHER FORMATTING FUNCTIONS:")
    try:
        import app.rules.formatting_fixed as formatting_module
        
        # List all functions in the formatting module
        functions = [name for name in dir(formatting_module) if callable(getattr(formatting_module, name)) and not name.startswith('_')]
        print(f"   Functions in formatting module: {functions}")
        
        # Check if there are multiple check functions
        if hasattr(formatting_module, 'check_formatting'):
            print("   ⚠️  Found additional 'check_formatting' function!")
        
    except Exception as e:
        print(f"   Error checking formatting module: {e}")

def test_sentence_processing():
    """Test how the application processes individual sentences"""
    
    print("\n=== TESTING SENTENCE PROCESSING ===")
    
    # Individual sentences that might be processed separately
    sentences = [
        "Prerequisites:",
        "The WinCC Unified Runtime app must be running .",
        "A project must be added as described in Add Project .",
        "The system must be configured properly ."
    ]
    
    print("Testing individual sentences:")
    
    for i, sentence in enumerate(sentences, 1):
        print(f"\nSentence {i}: '{sentence}'")
        
        try:
            from app.rules.formatting_fixed import check as check_formatting
            results = check_formatting(sentence)
            space_issues = [r for r in results if "space before punctuation" in r.get('message', '')]
            
            if space_issues:
                print(f"   ❌ FLAGGED: {len(space_issues)} space issues")
                for issue in space_issues:
                    print(f"      - '{issue['text']}' at {issue['start']}-{issue['end']}")
            else:
                print(f"   ✅ CLEAN: No space issues")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_full_application_flow()
    test_sentence_processing()

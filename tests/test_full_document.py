#!/usr/bin/env python3

import sys
sys.path.append('d:/doc-scanner')

# Simulate full document processing
def test_full_document():
    # Create a test document that contains the problematic sentence
    test_document = """# Test Document

If the files chosen for upload consume more than 90% of the available space, an error message appears, warning that there may not be enough storage space to accommodate the selected files.

This is another sentence with no issues.
"""

    print("Testing full document processing:\n")
    print("Document content:")
    print(test_document)
    print("=" * 60)
    
    # Test with markdown conversion (like the app does)
    try:
        import markdown
        html_content = markdown.markdown(test_document)
        print("HTML content:")
        print(html_content)
        print("=" * 60)
        
        # Test the cross_references rule
        from app.rules.cross_references import check
        suggestions = check(html_content)
        print("Cross-references rule suggestions:")
        for suggestion in suggestions:
            print(f"  - {suggestion}")
        print()
        
        # Test all rules to see if something else is triggering
        print("Testing all rules to find the culprit:")
        
        # Load and test each rule
        import os
        import importlib
        
        rules_folder = 'd:/doc-scanner/app/rules'
        rule_files = [f for f in os.listdir(rules_folder) if f.endswith('.py') and f != '__init__.py']
        
        for rule_file in rule_files:
            module_name = rule_file[:-3]
            try:
                module = importlib.import_module(f'app.rules.{module_name}')
                if hasattr(module, 'check'):
                    rule_suggestions = module.check(html_content)
                    if rule_suggestions:
                        for suggestion in rule_suggestions:
                            if 'URL' in suggestion or 'clickable' in suggestion:
                                print(f"  FOUND: {rule_file} -> {suggestion}")
            except Exception as e:
                print(f"  Error testing {rule_file}: {e}")
                
    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Other error: {e}")

if __name__ == "__main__":
    test_full_document()

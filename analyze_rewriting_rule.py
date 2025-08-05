#!/usr/bin/env python3
"""
Analyze the rewriting suggestions rule to understand when it triggers
"""

import re

def analyze_rewriting_rule():
    """Analyze when the instructional content message is triggered."""
    
    print("🔍 ANALYZING: 'This appears to be instructional content' Rule")
    print("=" * 70)
    
    # The exact logic from rewriting_suggestions.py
    def _is_instruction_text(text):
        """Check if text appears to be instructional."""
        instruction_indicators = [
            'click', 'select', 'open', 'navigate', 'enter', 'choose', 'press',
            'go to', 'access', 'configure', 'set up', 'install', 'download'
        ]
        
        text_lower = text.lower()
        return sum(1 for indicator in instruction_indicators if indicator in text_lower) >= 2

    def _has_step_formatting(text):
        """Check if text already has step formatting."""
        step_patterns = [
            r'^\s*\d+\.',  # 1. 2. 3.
            r'^\s*[•\-\*]',  # • - *
            r'Step \d+',  # Step 1, Step 2
            r'\d+\)',  # 1) 2) 3)
        ]
        
        lines = text.split('\n')
        formatted_lines = 0
        
        for line in lines:
            if any(re.search(pattern, line, re.MULTILINE) for pattern in step_patterns):
                formatted_lines += 1
        
        # If more than 1/3 of lines are formatted, consider it already formatted
        return formatted_lines > len(lines) / 3
    
    # Test cases to understand the rule
    test_cases = [
        {
            "name": "Instruction text without formatting",
            "content": "To access the system, click on the login button and enter your credentials. Select the appropriate role from the dropdown."
        },
        {
            "name": "Instruction text with formatting",
            "content": "1. Click on the login button\n2. Enter your credentials\n3. Select the appropriate role"
        },
        {
            "name": "Regular documentation",
            "content": "The system provides comprehensive security features. Users can authenticate using various methods."
        },
        {
            "name": "NOTE template",
            "content": "> **NOTE**! This feature requires admin privileges to access the configuration settings."
        },
        {
            "name": "Mixed content with instructions",
            "content": "The application is designed for ease of use. To get started, open the main menu and navigate to the settings page. Choose your preferred options."
        }
    ]
    
    print("\n📋 TEST CASES:")
    print("-" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print(f"Content: {repr(test_case['content'])}")
        
        is_instruction = _is_instruction_text(test_case['content'])
        has_formatting = _has_step_formatting(test_case['content'])
        
        print(f"Is instruction text: {is_instruction}")
        print(f"Has step formatting: {has_formatting}")
        
        # This is the exact condition from the rule
        would_trigger = is_instruction and not has_formatting
        
        if would_trigger:
            print("🚨 WOULD TRIGGER: 'This appears to be instructional content. Consider organizing as clear, numbered steps.'")
        else:
            print("✅ Would NOT trigger the warning")
    
    print(f"\n📖 RULE EXPLANATION:")
    print("-" * 70)
    print("The rule triggers when:")
    print("1. ✅ Text contains 2+ instruction words: click, select, open, navigate, enter, choose, press, etc.")
    print("2. ✅ Text does NOT have step formatting (numbered lists, bullets, etc.)")
    print("\nTo avoid this warning:")
    print("• Format instructions as numbered steps (1. 2. 3.)")
    print("• Use bullet points (• - *)")
    print("• Use 'Step 1', 'Step 2' format")
    print("• Or remove instruction words if it's not meant to be a procedure")

if __name__ == "__main__":
    analyze_rewriting_rule()

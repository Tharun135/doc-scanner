#!/usr/bin/env python3

import re

def test_fixed_format_logic():
    """Test the fixed formatAISuggestion logic"""
    
    test_cases = [
        # Should NOT be treated as KEY:VALUE (normal suggestions)
        "The following requirement must be met:",
        "The Following Requirement Must Be Met:",
        "When you deploy a project, the metadata is published.",
        "Click the Save button to continue:",
        
        # SHOULD be treated as KEY:VALUE (structured output)
        "IMPROVED: The system requires the following:",
        "SUGGESTION: Click the Save button",
        "CORRECTED: Use active voice here",
        "ACTIVE_VOICE: The system handles this automatically",
        
        # Edge cases
        "VERY_LONG_KEY_THAT_SHOULD_BE_REJECTED: This should not match",
        "SHORT: Good",
        "not_caps: This should not match"
    ]
    
    print("🔧 Testing Fixed formatAISuggestion Logic")
    print("=" * 70)
    
    for test_case in test_cases:
        print(f"\nInput: '{test_case}'")
        
        # New restrictive regex: /^([A-Z][A-Z_]+):\s+(.+)$/
        match = re.match(r'^([A-Z][A-Z_]+):\s+(.+)$', test_case)
        
        if match and len(match.group(1)) <= 20:
            key = match.group(1)
            value = match.group(2)
            # Apply title case transformation
            key_formatted = key.replace('_', ' ')
            key_formatted = re.sub(r'\b([a-z])', lambda m: m.group(1).upper(), key_formatted)
            print(f"  ✅ MATCHED as KEY:VALUE - '{key}' -> '{key_formatted}' : '{value}'")
        else:
            print(f"  → Normal text (no formatting)")

if __name__ == "__main__":
    test_fixed_format_logic()

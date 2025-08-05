#!/usr/bin/env python3
"""
Test that the exclamation mark rule is completely removed
"""

import requests

def test_exclamation_rule_removed():
    """Test that no exclamation mark warnings appear."""
    
    url = "http://127.0.0.1:5000/upload"
    
    # Test content with many exclamation marks (should NOT trigger warning anymore)
    test_content = """
> **NOTE**! This is important information!

This document has excessive exclamation marks! They are everywhere! 
So many exclamation marks! This is amazing! Fantastic! Incredible!

> **WARNING**! Be very careful! This is critical!
"""
    
    print("Testing that exclamation mark rule is removed...")
    print("Content with many exclamation marks:")
    print(test_content)
    print()
    
    files = {
        'file': ('test_exclamations.md', test_content, 'text/markdown')
    }
    
    try:
        response = requests.post(url, files=files, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Upload successful!")
            
            # Look for ANY exclamation mark warnings
            exclamation_warnings = []
            total_feedback = 0
            
            for sentence in result.get('sentences', []):
                total_feedback += len(sentence.get('feedback', []))
                for feedback in sentence.get('feedback', []):
                    message = feedback.get('message', '')
                    if 'exclamation' in message.lower():
                        exclamation_warnings.append(message)
            
            print(f"Total feedback items: {total_feedback}")
            
            if exclamation_warnings:
                print(f"❌ Still found exclamation warnings:")
                for warning in exclamation_warnings:
                    print(f"   • {warning}")
                return False
            else:
                print(f"✅ NO exclamation warnings found - rule successfully removed!")
                return True
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_exclamation_rule_removed()

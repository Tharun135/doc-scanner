#!/usr/bin/env python3
"""
Debug the procedural context detection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def debug_procedural_context():
    """Debug why some sentences aren't detected as procedural."""
    try:
        from app.rules.rewriting_suggestions import _is_procedural_context
        
        test_sentences = [
            ["The user opens the dialog window."],
            ["Open the dialog window."],
            ["First, the user Opens the application."],
            ["The user opens the menu and selects an option."]
        ]
        
        print("🔍 Debugging Procedural Context Detection")
        print("=" * 50)
        
        for sentences in test_sentences:
            print(f"📝 Sentence: '{sentences[0]}'")
            
            is_procedural = _is_procedural_context(sentences)
            print(f"   🎯 Is procedural: {is_procedural}")
            
            # Check what procedural indicators are present
            procedural_indicators = [
                'to', 'in order to', 'navigate', 'menu', 'button', 'field', 'dialog',
                'window', 'tab', 'panel', 'option', 'setting', 'configuration'
            ]
            
            combined_text = ' '.join(sentences).lower()
            found_indicators = [indicator for indicator in procedural_indicators if indicator in combined_text]
            
            if found_indicators:
                print(f"   ✅ Found indicators: {found_indicators}")
            else:
                print(f"   ❌ No procedural indicators found")
                print(f"   📝 Text: '{combined_text}'")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_procedural_context()

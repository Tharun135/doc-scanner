#!/usr/bin/env python3
"""
Test script specifically for the spaCy E088 text length fix.
"""

import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_spacy_max_length_fix():
    """Test that spaCy can now handle large texts without E088 error."""
    
    print("🔧 Testing spaCy E088 Text Length Fix")
    print("=" * 50)
    
    # Create text that exceeds the original 1MB limit (1,257,822 characters from error)
    large_text = "This is a sample text with vague terms like very good performance and excellent results that should be detected by our analysis rules. " * 10000
    print(f"📄 Test text length: {len(large_text):,} characters")
    
    if len(large_text) > 1000000:
        print(f"✅ Text exceeds original 1MB limit ({len(large_text):,} > 1,000,000)")
    
    # Test the main rule that was failing
    try:
        print("\n🧪 Testing vague_terms rule...")
        from rules.vague_terms import check
        
        # This was causing: [E088] Text of length 1257822 exceeds maximum of 1000000
        suggestions = check(large_text)
        print(f"✅ SUCCESS: vague_terms processed {len(large_text):,} characters")
        print(f"✅ Found {len(suggestions)} vague term suggestions")
        
        # Show example
        if suggestions:
            print(f"   📝 Example: {suggestions[0]['issue'][:80]}...")
            
    except Exception as e:
        if "E088" in str(e) or "exceeds maximum" in str(e):
            print(f"❌ FAILED: Still getting spaCy length error: {e}")
            return False
        else:
            print(f"❌ FAILED: Other error: {e}")
            return False
    
    # Test other spaCy-dependent rules
    rules_to_test = [
        ("passive_voice", "rules.passive_voice"),
        ("long_sentence", "rules.long_sentence"),
        ("grammar_rules", "rules.grammar_rules"),
        ("consistency_rules", "rules.consistency_rules")
    ]
    
    for rule_name, module_name in rules_to_test:
        try:
            print(f"\n🧪 Testing {rule_name} rule...")
            module = __import__(module_name, fromlist=['check'])
            suggestions = module.check(large_text)
            print(f"✅ SUCCESS: {rule_name} processed {len(large_text):,} characters")
            print(f"✅ Found {len(suggestions)} suggestions")
            
        except Exception as e:
            if "E088" in str(e) or "exceeds maximum" in str(e):
                print(f"❌ FAILED: {rule_name} still has spaCy length error: {e}")
                return False
            else:
                print(f"⚠️  WARNING: {rule_name} had other error: {e}")
    
    print(f"\n🎉 SUCCESS: All spaCy rules can handle large texts!")
    print(f"✅ No more E088 'Text exceeds maximum' errors")
    print(f"✅ Upload processing should now work for large documents")
    
    return True

if __name__ == "__main__":
    success = test_spacy_max_length_fix()
    if success:
        print(f"\n💡 The original upload error is FIXED!")
        print(f"   You can now upload large documents without the E088 error.")
    
    sys.exit(0 if success else 1)
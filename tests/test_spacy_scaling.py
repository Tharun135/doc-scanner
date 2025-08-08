"""
Test if the delay scales with number of spaCy imports
"""

import time
import sys
import os
import importlib

def test_spacy_scaling():
    """Test if import time scales with number of spaCy-importing rules."""
    print("📊 TESTING SPACY IMPORT SCALING")
    print("=" * 50)
    
    # Add paths
    sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))
    rules_path = os.path.join(os.path.dirname(__file__), 'app', 'rules')
    sys.path.insert(0, rules_path)
    
    # Test importing rules one by one
    spacy_rules = [
        'accessibility_terms',
        'ai_bot_terms',
        'cloud_computing_terms',
        'computer_device_terms',
        'technical_terms_clean'  # This one should be fast (no spaCy)
    ]
    
    print("\n🔍 Testing individual rule imports:")
    total_time = 0
    
    for i, rule_name in enumerate(spacy_rules, 1):
        print(f"\n{i}️⃣ Importing {rule_name}...")
        start_time = time.time()
        
        try:
            # Import through app system (like load_rules does)
            module = importlib.import_module(f'app.rules.{rule_name}')
            elapsed = time.time() - start_time
            total_time += elapsed
            
            if 'clean' in rule_name:
                expected = "🟢 FAST (no spaCy)"
            else:
                expected = "🐌 SLOW (has spaCy)"
                
            print(f"   {expected}: {elapsed:.3f}s")
            
        except Exception as e:
            elapsed = time.time() - start_time
            total_time += elapsed
            print(f"   ❌ FAILED ({elapsed:.3f}s): {e}")
    
    print(f"\n📊 CUMULATIVE ANALYSIS:")
    print(f"   Total time for {len(spacy_rules)} rules: {total_time:.3f}s")
    print(f"   Average per rule: {total_time/len(spacy_rules):.3f}s")
    
    if total_time > 15:
        print(f"\n🚨 SCALING CONFIRMED!")
        print(f"   Each spaCy import adds ~6s delay")
        print(f"   With 45+ rules = 45 × 6s = 270s+ total!")
    
    # Test clean rule timing specifically
    print(f"\n🧪 Clean rule detailed timing:")
    start_time = time.time()
    try:
        # Force reimport of clean rule
        if 'app.rules.technical_terms_clean' in sys.modules:
            del sys.modules['app.rules.technical_terms_clean']
        
        from app.rules.technical_terms_clean import check
        elapsed = time.time() - start_time
        print(f"   Clean rule import: {elapsed:.3f}s")
        
        if elapsed > 5:
            print(f"   🔴 Clean rule is also slow - there's another issue!")
        else:
            print(f"   ✅ Clean rule is fast - spaCy is the issue!")
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ Clean rule failed ({elapsed:.3f}s): {e}")

if __name__ == "__main__":
    test_spacy_scaling()

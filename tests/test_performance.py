#!/usr/bin/env python3

"""
Test document analysis performance before and after spaCy optimization.
"""

import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_analysis_performance():
    """Test document analysis speed."""
    
    # Sample document content
    test_content = """
    The json configuration file contains data for the application. 
    The report was written by the development team above.
    Use the xml format to store settings properly.
    The selected configuration files are updated.
    This is a very long sentence that could be broken into shorter parts which would make it easier to read and understand for the users.
    We recommend that you save the .html file carefully.
    You may now proceed to configure the application settings.
    """
    
    print("⏱️  TESTING DOCUMENT ANALYSIS PERFORMANCE")
    print("=" * 60)
    print(f"📄 Test content: {len(test_content)} characters")
    print(f"📝 Test sentences: {test_content.count('.')}")
    print()
    
    # Test individual rule performance
    rule_times = {}
    
    try:
        # Test technical_terms (now optimized)
        print("🔧 Testing technical_terms rule...")
        start_time = time.time()
        from app.rules.technical_terms import check as check_technical
        suggestions = check_technical(test_content)
        technical_time = time.time() - start_time
        rule_times['technical_terms (optimized)'] = technical_time
        print(f"   Time: {technical_time:.3f}s, Suggestions: {len(suggestions)}")
        
        # Test style_formatting (now optimized)
        print("🔧 Testing style_formatting rule...")
        start_time = time.time()
        from app.rules.style_formatting import check as check_style
        suggestions = check_style(test_content)
        style_time = time.time() - start_time
        rule_times['style_formatting (optimized)'] = style_time
        print(f"   Time: {style_time:.3f}s, Suggestions: {len(suggestions)}")
        
        # Test passive_voice (now optimized)
        print("🔧 Testing passive_voice rule...")
        start_time = time.time()
        from app.rules.passive_voice import check as check_passive
        suggestions = check_passive(test_content)
        passive_time = time.time() - start_time
        rule_times['passive_voice (optimized)'] = passive_time
        print(f"   Time: {passive_time:.3f}s, Suggestions: {len(suggestions)}")
        
        # Test an unoptimized rule for comparison
        print("🔧 Testing unoptimized rule (long_sentences)...")
        start_time = time.time()
        from app.rules.long_sentences import check as check_long
        suggestions = check_long(test_content)
        long_time = time.time() - start_time
        rule_times['long_sentences (unoptimized)'] = long_time
        print(f"   Time: {long_time:.3f}s, Suggestions: {len(suggestions)}")
        
    except Exception as e:
        print(f"❌ Error testing rules: {e}")
        return
    
    print(f"\n{'='*60}")
    print("📊 PERFORMANCE COMPARISON:")
    
    total_optimized = 0
    total_unoptimized = 0
    
    for rule_name, rule_time in rule_times.items():
        status = "🟢" if "optimized" in rule_name else "🔴"
        print(f"   {status} {rule_name}: {rule_time:.3f}s")
        
        if "optimized" in rule_name:
            total_optimized += rule_time
        else:
            total_unoptimized += rule_time
    
    print(f"\n📈 ANALYSIS:")
    print(f"   Optimized rules total: {total_optimized:.3f}s")
    print(f"   Unoptimized rules total: {total_unoptimized:.3f}s")
    
    if total_unoptimized > 0:
        speedup = total_unoptimized / total_optimized if total_optimized > 0 else float('inf')
        print(f"   Speed improvement: {speedup:.1f}x faster")
    
    print(f"\n💡 EXTRAPOLATION FOR FULL DOCUMENT:")
    estimated_full_optimized = total_optimized * 37  # 37 total rules
    estimated_full_unoptimized = total_unoptimized * 37
    
    print(f"   Estimated time with all rules optimized: {estimated_full_optimized:.1f}s")
    print(f"   Estimated time with all rules unoptimized: {estimated_full_unoptimized:.1f}s") 
    print(f"   Potential time savings: {estimated_full_unoptimized - estimated_full_optimized:.1f}s")

if __name__ == "__main__":
    test_analysis_performance()

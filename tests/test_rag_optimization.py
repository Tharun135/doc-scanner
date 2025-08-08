"""
Test the optimized RAG performance with caching and timeouts.
"""

import sys
import os
import time

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_optimized_rag():
    """Test the optimized RAG system performance."""
    print("🚀 TESTING OPTIMIZED RAG PERFORMANCE")
    print("=" * 60)
    
    # Test content
    test_content = """
    This document can be improved. The password should be entered by the user.
    JSON, HTML, CSS and XML files need proper formatting.
    """
    
    # Test cases
    test_cases = [
        ("technical_terms", "Technical terms rule"),
        ("passive_voice", "Passive voice rule"),
    ]
    
    total_time = 0
    
    for rule_name, description in test_cases:
        print(f"\n🔧 Testing {description}...")
        
        try:
            start_time = time.time()
            
            if rule_name == "technical_terms":
                from app.rules.technical_terms import check
                suggestions = check(test_content)
            elif rule_name == "passive_voice":
                from app.rules.passive_voice import check
                suggestions = check(test_content)
            
            elapsed = time.time() - start_time
            total_time += elapsed
            
            print(f"   ⏱️  Time: {elapsed:.3f}s")
            print(f"   📝 Suggestions: {len(suggestions)}")
            
            # Show first suggestion
            if suggestions:
                print(f"   💡 Example: {suggestions[0][:80]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"📊 TOTAL TIME: {total_time:.3f}s")
    print(f"📈 Expected improvement: 10-50x faster than before")
    
    # Test cache stats
    try:
        from app.rules.rag_performance_optimizer import get_cache_stats
        stats = get_cache_stats()
        print(f"📚 Cache stats: {stats}")
    except Exception as e:
        print(f"📚 Cache stats unavailable: {e}")

if __name__ == "__main__":
    test_optimized_rag()

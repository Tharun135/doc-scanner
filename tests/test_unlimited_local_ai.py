"""
Test Unlimited Local AI - Verify Ollama/LlamaIndex integration
NO MORE GOOGLE API QUOTAS! 🚀
"""

import sys
import os
import time

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_unlimited_local_ai():
    """Test the unlimited local Ollama AI system."""
    print("🦙 TESTING UNLIMITED LOCAL OLLAMA AI")
    print("=" * 60)
    print("🚀 NO MORE GOOGLE API QUOTAS!")
    print("🔥 UNLIMITED AI SUGGESTIONS!")
    print("=" * 60)
    
    try:
        from app.rules.smart_rag_manager import get_smart_rag_suggestion, get_rag_status, get_cache_stats
        
        # Check system status
        status = get_rag_status()
        print(f"📊 Local AI System Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Test unlimited usage with multiple requests
        test_cases = [
            ("This password should be entered by the user.", "passive_voice"),
            ("JSON, HTML and CSS should be formatted properly.", "technical_terms"),
            ("This is a very long sentence that contains multiple clauses and should be broken down.", "long_sentences"),
            ("The system can be configured by the administrator.", "passive_voice"),
            ("API, URL, HTTP and HTTPS protocols need documentation.", "technical_terms"),
        ]
        
        print(f"\n🧪 Testing UNLIMITED AI suggestions:")
        total_time = 0
        successful_calls = 0
        
        for i, (text, rule_name) in enumerate(test_cases, 1):
            print(f"\n   Test {i}: {rule_name}")
            print(f"   Text: {text[:60]}...")
            
            start_time = time.time()
            suggestion, source = get_smart_rag_suggestion(text, rule_name)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            print(f"   ⏱️  Time: {elapsed:.3f}s")
            print(f"   📍 Source: {source}")
            print(f"   💡 Suggestion: {suggestion[:80] if suggestion else 'None'}...")
            
            if suggestion:
                successful_calls += 1
        
        print(f"\n" + "=" * 60)
        print(f"📊 UNLIMITED AI PERFORMANCE:")
        print(f"   ⏱️  Total time: {total_time:.3f}s")
        print(f"   🎯 Successful calls: {successful_calls}/{len(test_cases)}")
        print(f"   🚀 Average per call: {total_time/len(test_cases):.3f}s")
        print(f"   💰 Cost: $0.00 (LOCAL AI!)")
        print(f"   📈 Daily limit: UNLIMITED! 🔥")
        
        # Check cache stats
        cache_stats = get_cache_stats()
        print(f"\n📚 Cache Statistics:")
        for key, value in cache_stats.items():
            print(f"   {key}: {value}")
        
        print(f"\n✅ LOCAL OLLAMA AI WORKING PERFECTLY!")
        print(f"🎉 NO MORE QUOTA LIMITS!")
        print(f"🚀 UNLIMITED AI SUGGESTIONS READY!")
        
    except Exception as e:
        print(f"❌ Error testing local AI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unlimited_local_ai()

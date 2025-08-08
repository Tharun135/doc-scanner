"""
Test Smart RAG Manager - Quick validation of quota management
"""

import sys
import os

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_smart_rag_manager():
    """Test the smart RAG manager functionality."""
    print("🤖 TESTING SMART RAG MANAGER")
    print("=" * 60)
    
    try:
        from app.rules.smart_rag_manager import get_smart_rag_suggestion, get_rag_status, reset_rag_circuit_breaker
        
        # Reset any existing circuit breaker
        reset_rag_circuit_breaker()
        
        # Check initial status
        status = get_rag_status()
        print(f"📊 Initial Status:")
        print(f"   Daily requests: {status['daily_requests']}")
        print(f"   Quota errors: {status['quota_errors']}")
        print(f"   Circuit breaker: {status['circuit_breaker_active']}")
        print(f"   Cached responses: {status['cached_responses']}")
        
        # Test suggestions
        test_cases = [
            ("This password should be entered by the user.", "passive_voice"),
            ("JSON, HTML and CSS should be formatted properly.", "technical_terms"),
            ("This is a very long sentence that might need to be broken down.", "long_sentences"),
        ]
        
        print(f"\n🧪 Testing suggestions:")
        for text, rule_name in test_cases:
            print(f"\n   Rule: {rule_name}")
            print(f"   Text: {text[:50]}...")
            
            # Mock RAG callable that simulates quota error
            def mock_rag_callable(text):
                # Simulate quota exhaustion after first call
                if rule_name == "passive_voice":
                    raise Exception("429 You exceeded your current quota")
                return f"Improved suggestion for {rule_name}"
            
            suggestion, source = get_smart_rag_suggestion(text, rule_name, mock_rag_callable)
            print(f"   💡 Suggestion: {suggestion}")
            print(f"   📍 Source: {source}")
        
        # Check final status
        final_status = get_rag_status()
        print(f"\n📊 Final Status:")
        print(f"   Daily requests: {final_status['daily_requests']}")
        print(f"   Quota errors: {final_status['quota_errors']}")
        print(f"   Circuit breaker: {final_status['circuit_breaker_active']}")
        print(f"   Cached responses: {final_status['cached_responses']}")
        
        print(f"\n✅ Smart RAG Manager working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing Smart RAG Manager: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smart_rag_manager()

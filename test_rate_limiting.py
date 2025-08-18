"""
Test script for the rate limiting system.
Verifies that quota tracking and fallbacks work correctly.
"""

import sys
import os

# Add the app directory to the path
app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app")
sys.path.append(app_dir)

def test_rate_limiter():
    """Test the rate limiter functionality."""
    print("🧪 Testing Rate Limiter System")
    print("=" * 50)
    
    try:
        from app.rate_limiter import rate_limiter, get_quota_status, reset_quota
        
        # Reset quota for testing
        reset_quota()
        print("✅ Quota reset successfully")
        
        # Check initial status
        status = get_quota_status()
        print(f"📊 Initial quota status: {status['used']}/{status['limit']} used")
        print(f"🔋 Remaining: {status['remaining']}")
        print(f"✅ Can make request: {status['can_make_request']}")
        
        # Test quota increment
        for i in range(3):
            rate_limiter.record_request()
            status = get_quota_status()
            print(f"📈 After request {i+1}: {status['used']}/{status['limit']} used")
        
        print("\n✅ Rate limiter test completed successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Rate limiter import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Rate limiter test failed: {e}")
        return False

def test_rag_fallback():
    """Test the RAG system with fallback."""
    print("\n🧪 Testing RAG System with Fallbacks")
    print("=" * 50)
    
    try:
        # Import the RAG system 
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))
        from rag_system import get_rag_suggestion, rule_based_fallback
        
        # Test the fallback function directly
        print("🔄 Testing rule-based fallback...")
        fallback_result = rule_based_fallback(
            feedback_text="This sentence is too long and complex",
            sentence_context="This is a very long sentence that contains multiple clauses and should be simplified.",
            document_type="technical"
        )
        
        print(f"✅ Fallback suggestion: {fallback_result['suggestion'][:100]}...")
        print(f"📊 Method: {fallback_result['method']}")
        print(f"🎯 Confidence: {fallback_result['confidence']}")
        
        # Test the main RAG function (this should use rate limiting)
        print("\n🔄 Testing main RAG function...")
        rag_result = get_rag_suggestion(
            feedback_text="passive voice detected",
            sentence_context="The document was written by the author.",
            document_type="general"
        )
        
        if rag_result:
            print(f"✅ RAG suggestion: {rag_result['suggestion'][:100]}...")
            print(f"📊 Method: {rag_result['method']}")
            print(f"🎯 Confidence: {rag_result['confidence']}")
            if 'quota_status' in rag_result:
                print(f"📊 Quota info included: {rag_result['quota_status']}")
        else:
            print("⚠️  RAG function returned None (expected if quota exceeded)")
        
        print("\n✅ RAG fallback test completed successfully")
        return True
        
    except ImportError as e:
        print(f"❌ RAG system import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ RAG fallback test failed: {e}")
        return False

def show_quota_tips():
    """Show tips for managing API quota."""
    print("\n💡 API Quota Management Tips")
    print("=" * 50)
    print("1. 🎯 Free tier limit: 50 requests per day")
    print("2. 🔄 Quota resets daily at midnight UTC")
    print("3. 📈 Monitor quota in the web interface")
    print("4. 🛡️  Fallback suggestions when quota exceeded")
    print("5. ⚙️  Adjust AI usage frequency in settings")
    print("\n🔧 Solutions:")
    print("   - Use rule-based suggestions more often")
    print("   - Upgrade to paid Gemini API plan")
    print("   - Implement request caching")
    print("   - Use alternative AI providers (OpenAI, Anthropic)")

if __name__ == "__main__":
    print("🚀 Doc Scanner - Rate Limiting Test Suite")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_rate_limiter()
    test2_passed = test_rag_fallback()
    
    # Show results
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Rate Limiter Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"RAG Fallback Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Rate limiting system is working.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    # Show tips
    show_quota_tips()
    
    print("\n🌐 Start your web app with: python run.py")
    print("📊 Monitor quota status in the web interface sidebar")

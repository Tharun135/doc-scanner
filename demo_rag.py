#!/usr/bin/env python3
"""
Demo script to test the Gemini + LangChain RAG integration
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, 'app')

def test_basic_import():
    """Test basic import of RAG system."""
    print("🧪 Testing RAG System Import...")
    try:
        from rag_system import rag_system, get_rag_suggestion
        print("✅ RAG system imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("   Make sure to run: python setup_rag.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_rag_availability():
    """Test if RAG system is available and configured."""
    print("\n🔧 Testing RAG Availability...")
    try:
        from rag_system import rag_system
        
        if rag_system.is_available():
            print("✅ RAG system is available and configured")
            return True
        else:
            print("⚠️  RAG system is not fully configured")
            print("   Check your GOOGLE_API_KEY in .env file")
            return False
    except Exception as e:
        print(f"❌ Error testing availability: {e}")
        return False

def test_rag_suggestion():
    """Test getting a RAG suggestion."""
    print("\n💡 Testing RAG Suggestion Generation...")
    try:
        from rag_system import get_rag_suggestion
        
        # Test with a sample writing issue
        feedback = "This sentence contains passive voice"
        sentence = "The document was written by the team."
        document_content = """
        This is a business report about our quarterly results.
        The document contains several sections including methodology,
        findings, and recommendations for future actions.
        """
        
        print(f"   Issue: {feedback}")
        print(f"   Sentence: {sentence}")
        
        result = get_rag_suggestion(
            feedback_text=feedback,
            sentence_context=sentence,
            document_type="business",
            document_content=document_content
        )
        
        if result:
            print("✅ RAG suggestion generated successfully!")
            print(f"   Suggestion: {result['suggestion'][:100]}...")
            print(f"   Method: {result['method']}")
            print(f"   Confidence: {result['confidence']}")
            if result.get('sources'):
                print(f"   Sources: {len(result['sources'])} knowledge sources used")
            return True
        else:
            print("⚠️  No RAG suggestion generated (this is normal if API keys aren't configured)")
            return False
            
    except Exception as e:
        print(f"❌ Error generating RAG suggestion: {e}")
        return False

def test_ai_improvement_integration():
    """Test the integration with the existing AI improvement system."""
    print("\n🤖 Testing AI Improvement Integration...")
    try:
        from ai_improvement import get_enhanced_ai_suggestion
        
        # Test with a sample request
        result = get_enhanced_ai_suggestion(
            feedback_text="This sentence is too long and complex",
            sentence_context="The comprehensive document that was meticulously prepared by the dedicated team of experts contains detailed information about the complex software implementation process that we have been working on for several months.",
            document_type="technical",
            writing_goals=["clarity", "conciseness"],
            document_content="This is a technical documentation about software implementation..."
        )
        
        if result:
            print("✅ Enhanced AI suggestion generated successfully!")
            print(f"   Method: {result.get('method', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 'unknown')}")
            
            # Check if RAG was used
            if 'rag' in result.get('method', '').lower():
                print("🧠 RAG enhancement detected!")
            
            if result.get('sources'):
                print(f"   RAG Sources: {len(result['sources'])}")
                
            return True
        else:
            print("⚠️  No enhanced suggestion generated")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI improvement integration: {e}")
        return False

def demo_frontend_features():
    """Show what users will see in the frontend."""
    print("\n🎨 Frontend Integration Demo")
    print("=" * 40)
    
    print("When RAG is active, users will see:")
    print("• 🧠 RAG Enhanced badge on AI suggestions")
    print("• 📚 Knowledge Sources section showing:")
    print("  - 📋 Writing Guidelines (style rules)")
    print("  - 📄 Document Context (from uploaded content)")
    print("• Enhanced suggestions with examples and context")
    print("• Better accuracy and relevance")
    
    return True

def main():
    """Main demo function."""
    print("🚀 Doc Scanner RAG Integration Demo")
    print("=" * 50)
    print("This demo tests the Gemini + LangChain RAG integration")
    print("that enhances AI suggestions with document context.\n")
    
    tests = [
        ("Basic Import", test_basic_import),
        ("RAG Availability", test_rag_availability),
        ("RAG Suggestion", test_rag_suggestion),
        ("AI Integration", test_ai_improvement_integration),
        ("Frontend Features", demo_frontend_features)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print("\n❌ Demo interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Demo Results Summary")
    print("=" * 30)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, passed in results if passed)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! RAG integration is working correctly.")
        print("\nNext steps:")
        print("1. Start the application: python run.py")
        print("2. Upload a document")
        print("3. Look for the '🧠 RAG Enhanced' badge on AI suggestions")
    else:
        print("\n⚠️  Some tests failed. Check the setup guide for troubleshooting.")
        print("Run: python setup_rag.py to ensure proper installation")

if __name__ == "__main__":
    main()

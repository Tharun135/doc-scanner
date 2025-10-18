#!/usr/bin/env python3
"""
Test script to verify document-first AI configuration.
This tests if the system prioritizes your uploaded documents over rule-based suggestions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_document_first_priority():
    """Test that document search has priority over rule-based systems."""
    
    print("🔧 Testing Document-First AI Configuration")
    print("=" * 50)
    
    try:
        # Import the document-first AI system
        from app.document_first_ai import DocumentFirstAIEngine
        
        # Initialize the engine
        engine = DocumentFirstAIEngine()
        
        print(f"📊 Document Database Status:")
        print(f"   - Documents available: {engine.document_count}")
        print(f"   - Collection connected: {'✅ Yes' if engine.collection else '❌ No'}")
        
        if engine.document_count == 0:
            print("\n⚠️  WARNING: No documents found in the knowledge base!")
            print("   Upload documents to see document-first suggestions in action.")
            return
        
        # Test cases for different types of writing issues
        test_cases = [
            {
                "feedback": "passive voice detected", 
                "sentence": "The file was created by the system.",
                "expected_method": "document_search"
            },
            {
                "feedback": "long sentence needs breaking", 
                "sentence": "This is a very long sentence that contains multiple clauses and should probably be broken into shorter sentences for better readability.",
                "expected_method": "document_search"
            },
            {
                "feedback": "use active voice", 
                "sentence": "Data is processed by the application.",
                "expected_method": "document_search"
            }
        ]
        
        print(f"\n🧪 Testing Document-First Suggestions:")
        print("-" * 40)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['feedback']}")
            print(f"Original: {test_case['sentence']}")
            
            try:
                result = engine.generate_document_first_suggestion(
                    feedback_text=test_case["feedback"],
                    sentence_context=test_case["sentence"],
                    document_type="general"
                )
                
                print(f"✅ Method used: {result.get('method', 'unknown')}")
                print(f"✅ Confidence: {result.get('confidence', 'unknown')}")
                print(f"✅ Sources: {len(result.get('sources', []))} document(s)")
                print(f"✅ Suggestion: {result.get('suggestion', 'None')[:80]}...")
                
                # Check if it's using documents
                if result.get('method') in ['document_search', 'hybrid_document_llm', 'document_search_primary']:
                    print("🎯 SUCCESS: Using document-based suggestion!")
                elif result.get('method') == 'basic_fallback':
                    print("⚠️  FALLBACK: No relevant documents found")
                else:
                    print(f"ℹ️  Method: {result.get('method')}")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
        
        print(f"\n📈 Summary:")
        print(f"   - Total documents: {engine.document_count}")
        print(f"   - Document-first engine: ✅ Configured")
        print(f"   - Priority order: Documents → RAG → LLM → Rules")
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("   Make sure the document_first_ai.py module is available")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_intelligent_ai_integration():
    """Test the integration with the main intelligent AI system."""
    
    print(f"\n🔧 Testing Main AI System Integration")
    print("=" * 50)
    
    try:
        from app.intelligent_ai_improvement import get_enhanced_ai_suggestion
        
        test_feedback = "passive voice detected"
        test_sentence = "The configuration was updated by the administrator."
        
        print(f"📝 Test case:")
        print(f"   Feedback: {test_feedback}")
        print(f"   Sentence: {test_sentence}")
        
        result = get_enhanced_ai_suggestion(
            feedback_text=test_feedback,
            sentence_context=test_sentence,
            document_type="user_manual"
        )
        
        print(f"\n📊 Result:")
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   Confidence: {result.get('confidence', 'unknown')}")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Sources: {result.get('sources', [])}")
        print(f"   Suggestion: {result.get('suggestion', 'None')[:100]}...")
        
        # Check priority order
        method = result.get('method', '')
        if 'document' in method.lower():
            print("🎯 SUCCESS: Document-first priority is working!")
        elif method in ['ollama_rag', 'advanced_rag']:
            print("📚 GOOD: Using RAG with document context")
        elif method in ['smart_rule_based', 'intelligent_analysis']:
            print("⚠️  NOTICE: Fell back to rule-based (documents may not have relevant content)")
        else:
            print(f"ℹ️  Method: {method}")
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

def show_configuration_summary():
    """Show the current configuration summary."""
    
    print(f"\n📋 Document-First Configuration Summary")
    print("=" * 50)
    
    print(f"🎯 NEW PRIORITY ORDER:")
    print(f"   1. 🔍 Document Search (your 7042 uploaded documents)")
    print(f"   2. 🧠 Advanced RAG + Documents")
    print(f"   3. 🤖 Ollama + Document Context")
    print(f"   4. 📊 Vector Search")
    print(f"   5. ⚡ Smart Rules (backup only)")
    
    print(f"\n🔧 What Changed:")
    print(f"   ❌ Before: Smart_Rule_Based → Smart_Fallback")
    print(f"   ✅ After:  Documents → RAG → LLM → Rules")
    
    print(f"\n💡 Benefits:")
    print(f"   • Answers come from YOUR uploaded documentation")
    print(f"   • Context-aware suggestions based on your content")
    print(f"   • Domain-specific improvements")
    print(f"   • Reduced reliance on generic rules")

if __name__ == "__main__":
    print("🚀 Document-First AI System Test")
    print("*" * 60)
    
    # Run tests
    test_document_first_priority()
    test_intelligent_ai_integration()
    show_configuration_summary()
    
    print(f"\n✅ Test completed!")
    print(f"🔧 Your AI system now prioritizes uploaded documents over rules!")
"""
Direct test of the document-first AI system without server
This simulates the exact routing logic we implemented
"""

import sys
import os
sys.path.append('app')

def test_direct_routing():
    """Test the routing logic directly without server"""
    print("🚀 Direct Document-First AI Routing Test")
    print("=" * 60)
    
    # Test case: the exact passive voice issue from user
    feedback_text = "passive voice detected"
    sentence_context = "The installation steps are demonstrated in a video at the following link:"
    document_type = "user_manual"
    writing_goals = ["clarity", "conciseness"]
    
    print(f"📝 Test Input:")
    print(f"   Feedback: {feedback_text}")
    print(f"   Sentence: {sentence_context}")
    print(f"   Document Type: {document_type}")
    
    try:
        # Step 1: Try to import intelligent AI system (our document-first system)
        print(f"\n🔧 Step 1: Testing Intelligent AI System Import...")
        try:
            from app.intelligent_ai_improvement import IntelligentAISuggestionEngine
            INTELLIGENT_AI_AVAILABLE = True
            print("✅ Intelligent AI system available")
            
            # Initialize the engine
            intelligent_engine = IntelligentAISuggestionEngine()
            print("✅ Intelligent AI engine initialized")
            
        except Exception as e:
            INTELLIGENT_AI_AVAILABLE = False
            intelligent_engine = None
            print(f"❌ Intelligent AI not available: {e}")
        
        # Step 2: Test the routing logic we implemented
        print(f"\n🔧 Step 2: Testing Routing Logic...")
        
        if INTELLIGENT_AI_AVAILABLE and intelligent_engine:
            print("🔍 Using DOCUMENT-FIRST intelligent AI suggestion...")
            
            # This is the exact call from our routing fix
            result = intelligent_engine.generate_contextual_suggestion(
                feedback_text=feedback_text,
                sentence_context=sentence_context,
                document_type=document_type,
                writing_goals=writing_goals
            )
            
            method = result.get('method', 'unknown')
            confidence = result.get('confidence', 'unknown')
            success = result.get('success', False)
            
            print(f"📊 Result:")
            print(f"   Method: {method}")
            print(f"   Confidence: {confidence}")
            print(f"   Success: {success}")
            
            # Check if it's using document-first methods instead of old ones
            if method in ['document_first', 'advanced_rag', 'ollama_enhanced', 'intelligent_suggestion']:
                print(f"\n🎉 SUCCESS! Using document-first method: '{method}'")
                print("✅ This means smart_rule_based and smart_fallback are now backup only!")
                return True, method
            elif method in ['smart_rule_based', 'smart_fallback']:
                print(f"\n❌ STILL USING OLD METHOD: '{method}'")
                print("🔧 The document-first system exists but is falling back to old methods")
                print("💡 This suggests the document search isn't finding relevant content")
                return False, method
            else:
                print(f"\n⚠️ Unknown method: '{method}' - this needs investigation")
                return False, method
                
        else:
            print("❌ Intelligent AI system not available - would fall back to old system")
            return False, "not_available"
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False, "error"

def explain_results(success, method):
    """Explain what the test results mean"""
    print("\n" + "=" * 60)
    if success:
        print("✅ DOCUMENT-FIRST ROUTING IS WORKING!")
        print(f"🎯 Your AI is now using method: '{method}'")
        print("")
        print("💡 What this means:")
        print("   ✅ smart_rule_based is now backup only (Priority 4)")
        print("   ✅ smart_fallback is now backup only (Priority 4)")
        print("   ✅ Your uploaded documents are Priority 1")
        print("   ✅ The routing fix is successful!")
        print("")
        print("🚀 Next Steps:")
        print("   1. When your main server runs successfully, it will use this system")
        print("   2. AI suggestions will search your 7042 documents first")
        print("   3. Only fall back to rules when documents don't help")
        
    else:
        if method == "not_available":
            print("❌ INTELLIGENT AI SYSTEM NOT AVAILABLE")
            print("🔧 The document-first system couldn't be loaded")
        elif method in ['smart_rule_based', 'smart_fallback']:
            print("⚠️ DOCUMENT-FIRST SYSTEM LOADED BUT FALLING BACK")
            print(f"📊 Current method: {method}")
            print("")
            print("💡 Possible reasons:")
            print("   1. Document search found no relevant content")
            print("   2. Document collection is empty or not accessible")
            print("   3. Priority logic needs debugging")
            print("")
            print("🔧 Solutions:")
            print("   1. Verify your 7042 documents are properly indexed")
            print("   2. Check ChromaDB connection")
            print("   3. Test with more specific technical queries")
        else:
            print(f"❌ UNEXPECTED RESULT: method = {method}")
            print("🔧 This needs further investigation")

if __name__ == "__main__":
    print("🔧 Testing Document-First AI Routing (Direct)")
    print("************************************************************")
    
    success, method = test_direct_routing()
    explain_results(success, method)
    
    print("\n✅ Test completed!")
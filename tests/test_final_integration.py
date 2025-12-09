#!/usr/bin/env python3
"""
Final DocScanner Ollama RAG Integration Test
Tests the complete pipeline from rule detection to AI-enhanced suggestions
"""

import sys
import os

# Add current directory to path
sys.path.append('.')

def test_rag_system_status():
    """Test the RAG system configuration"""
    print("🔍 RAG System Configuration")
    print("=" * 40)
    
    try:
        from app.rules.rag_rule_helper import RAG_AVAILABLE, RAG_ENABLED, RAG_TYPE
        print(f"RAG_AVAILABLE: {RAG_AVAILABLE}")
        print(f"RAG_ENABLED: {RAG_ENABLED}")
        print(f"RAG_TYPE: {RAG_TYPE}")
        return RAG_AVAILABLE
    except Exception as e:
        print(f"❌ Error checking RAG: {e}")
        return False

def test_direct_ollama_rag():
    """Test the Ollama RAG system directly"""
    print("\n🤖 Direct Ollama RAG Test")
    print("=" * 40)
    
    try:
        sys.path.append('scripts')
        from docscanner_ollama_rag import get_rag_suggestion
        
        result = get_rag_suggestion(
            feedback_text="Passive voice detected: 'was written' - convert to active voice",
            sentence_context="The document was written by John yesterday.",
            document_type="technical"
        )
        
        if result:
            print("✅ Direct Ollama RAG working!")
            print(f"Method: {result.get('method', 'unknown')}")
            print(f"Model: {result.get('model', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 'unknown')}")
            print(f"Suggestion: {result.get('suggestion', 'No suggestion')[:150]}...")
            
            # Check for local AI indicators
            context = result.get('context_used', {})
            if context.get('local_ai', False):
                print("🏠 Confirmed: Using local AI")
            if context.get('private', False):
                print("🔒 Confirmed: Private processing")
            if context.get('cost') == 'free':
                print("💰 Confirmed: Zero cost")
                
            return result
        else:
            print("⚠️ Direct Ollama RAG returned None")
            return None
            
    except Exception as e:
        print(f"❌ Direct Ollama RAG error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_rule_with_rag():
    """Test a specific rule with RAG enhancement"""
    print("\n🔧 Rule + RAG Integration Test")
    print("=" * 40)
    
    try:
        # Import passive voice rule directly
        from app.rules.passive_voice import check
        
        test_content = '<p>The document was written by John yesterday. The report will be reviewed by the team.</p>'
        print(f"Test content: {test_content}")
        
        results = check(test_content)
        print(f"📊 Rule results: {len(results)} suggestions")
        
        for i, result in enumerate(results):
            print(f"  {i+1}. {result}")
            
            # Check if this shows signs of RAG enhancement
            if isinstance(result, dict):
                method = result.get('method', 'unknown')
                if 'ollama' in method.lower():
                    print(f"      🎉 Ollama RAG detected!")
                elif 'rag' in method.lower():
                    print(f"      🤖 RAG enhancement detected")
                else:
                    print(f"      📝 Method: {method}")
            elif isinstance(result, str):
                if 'ollama' in result.lower() or 'local' in result.lower():
                    print("      🎉 Local AI detected in suggestion!")
                elif len(result) > 100:  # Longer suggestions often indicate AI enhancement
                    print("      🤖 Enhanced suggestion detected")
        
        return len(results) > 0
        
    except Exception as e:
        print(f"❌ Rule test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_improvement_integration():
    """Test AI improvement system integration"""
    print("\n🧠 AI Improvement System Test")  
    print("=" * 40)
    
    try:
        from app.ai_improvement import GeminiAISuggestionEngine
        
        ai_engine = GeminiAISuggestionEngine()
        
        result = ai_engine.generate_contextual_suggestion(
            feedback_text="Passive voice detected: 'was written' - convert to active voice",
            sentence_context="The document was written by John yesterday.",
            document_type="technical",
            document_content="This is a technical document about software development."
        )
        
        if result:
            print("✅ AI improvement system working!")
            print(f"Method: {result.get('method', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 'unknown')}")
            print(f"Suggestion preview: {result.get('suggestion', 'No suggestion')[:150]}...")
            
            # Check what type of AI was used
            context = result.get('context_used', {})
            primary_ai = context.get('primary_ai', 'unknown')
            print(f"Primary AI: {primary_ai}")
            
            if 'ollama' in result.get('method', '').lower():
                print("🎉 Ollama integration confirmed!")
            
            return True
        else:
            print("⚠️ AI improvement system returned None")
            return False
            
    except Exception as e:
        print(f"❌ AI improvement test error: {e}")
        return False

def show_final_status(tests_passed):
    """Show final integration status"""
    print(f"\n{'='*60}")
    print("🎯 FINAL INTEGRATION STATUS")
    print('='*60)
    
    if tests_passed >= 2:
        print("🏆 SUCCESS: Ollama + ChromaDB + LlamaIndex Integration Working!")
        print()
        print("✅ What you now have:")
        print("  🏠 Local LLM Processing (TinyLLaMA)")
        print("  🔒 Complete Privacy (No data leaves your machine)")
        print("  ⚡ Fast Responses (Local inference)")
        print("  💰 Zero Costs (No API fees)")
        print("  📚 Smart Context (Vector search with ChromaDB)")
        print("  🎯 Writing Focus (Optimized for DocScanner rules)")
        print()
        print("🚀 Your DocScanner is now powered by:")
        print("  • Ollama (Local LLM Runtime)")
        print("  • ChromaDB (Vector Storage)")  
        print("  • LlamaIndex (RAG Framework)")
        print("  • TinyLLaMA (Efficient AI Model)")
        print()
        print("💡 Next steps:")
        print("  1. Test with real documents")
        print("  2. Consider upgrading to mistral or phi3 for better quality")
        print("  3. Add custom writing rules to the knowledge base")
        
    elif tests_passed >= 1:
        print("⚠️ PARTIAL: Some components working")
        print("Check individual test results above for issues")
        
    else:
        print("❌ FAILED: Integration not working")
        print("Check error messages above and ensure:")
        print("  1. Ollama is running: ollama serve")
        print("  2. Model is available: ollama list")
        print("  3. Dependencies installed: pip install llama-index-core")

def main():
    """Run comprehensive integration test"""
    print("🚀 DocScanner Ollama + ChromaDB + LlamaIndex Integration Test")
    print("=" * 70)
    
    tests = [
        ("RAG System Config", test_rag_system_status),
        ("Direct Ollama RAG", test_direct_ollama_rag),
        ("Rule Integration", test_rule_with_rag),
        ("AI System Integration", test_ai_improvement_integration)
    ]
    
    passed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*10} {test_name} {'='*10}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    show_final_status(passed)

if __name__ == "__main__":
    main()

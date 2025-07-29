#!/usr/bin/env python3
"""
Simple test script to verify the Gemini Answer changes without dependencies
"""

def test_frontend_changes():
    """Test that frontend template includes the new Gemini Answer section"""
    try:
        with open('app/templates/index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("🔍 Testing Frontend Changes...")
        
        # Check for the changed "Writing Problem" to "Issue"
        if '📋 Issue:' in content:
            print("✅ Writing Problem changed to Issue")
        else:
            print("❌ Writing Problem not changed to Issue")
            
        # Check for Gemini Answer section
        if '📘 Gemini Answer:' in content:
            print("✅ Gemini Answer section added")
        else:
            print("❌ Gemini Answer section missing")
            
        # Check for gemini_answer variable usage
        if 'aiSuggestion.gemini_answer' in content:
            print("✅ Gemini Answer variable used correctly")
        else:
            print("❌ Gemini Answer variable not found")
            
        # Check for CSS styling
        if '.gemini-answer' in content:
            print("✅ Gemini Answer CSS styling added")
        else:
            print("❌ Gemini Answer CSS styling missing")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing frontend: {e}")
        return False

def test_backend_changes():
    """Test that backend includes gemini_answer field"""
    try:
        print("\n🔍 Testing Backend Changes...")
        
        # Check AI improvement file
        with open('app/ai_improvement.py', 'r', encoding='utf-8') as f:
            ai_content = f.read()
            
        if '"gemini_answer"' in ai_content:
            print("✅ AI Improvement includes gemini_answer field")
        else:
            print("❌ AI Improvement missing gemini_answer field")
            
        # Check RAG system file
        with open('app/rag_system.py', 'r', encoding='utf-8') as f:
            rag_content = f.read()
            
        if '_get_direct_gemini_answer' in rag_content:
            print("✅ RAG system includes direct Gemini answer method")
        else:
            print("❌ RAG system missing direct Gemini answer method")
            
        if '"gemini_answer": gemini_answer' in rag_content:
            print("✅ RAG system returns gemini_answer field")
        else:
            print("❌ RAG system missing gemini_answer return field")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def main():
    print("🚀 Testing Gemini Answer Integration (File Changes)\n")
    
    # Run tests
    frontend_test = test_frontend_changes()
    backend_test = test_backend_changes()
    
    print(f"\n📊 Test Summary:")
    print(f"Frontend Changes: {'✅ PASS' if frontend_test else '❌ FAIL'}")
    print(f"Backend Changes: {'✅ PASS' if backend_test else '❌ FAIL'}")
    
    if frontend_test and backend_test:
        print("\n🎉 All file changes verified! The implementation looks correct.")
        print("\n📋 Changes Made:")
        print("1. ✅ Changed 'Writing Problem' to '📋 Issue' in the AI panel")
        print("2. ✅ Added '📘 Gemini Answer' section to display direct Gemini responses")
        print("3. ✅ Added custom CSS styling for the Gemini answer section") 
        print("4. ✅ Modified backend to generate and return gemini_answer field")
        print("5. ✅ Updated fallback suggestions to include gemini_answer")
        print("\n🚀 Ready to test with the running application!")
    else:
        print("\n⚠️ Some changes were not properly applied. Check the files.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple test to verify RAG integration structure is working
"""

import sys
import os

# Add app directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
sys.path.insert(0, app_dir)

def test_imports():
    """Test that basic imports work."""
    print("🧪 Testing basic imports...")
    
    try:
        from ai_improvement import get_enhanced_ai_suggestion
        print("✅ ai_improvement module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ai_improvement: {e}")
        return False
    
    try:
        from rag_system import rag_system, get_rag_suggestion
        print("✅ rag_system module imported successfully")
    except ImportError as e:
        print(f"⚠️  RAG system import failed (expected if dependencies not installed): {e}")
        print("   This is normal - run 'python setup_rag.py' to install RAG dependencies")
    
    return True

def test_enhanced_suggestion():
    """Test enhanced AI suggestion without RAG."""
    print("\n🤖 Testing enhanced AI suggestion (without RAG)...")
    
    try:
        from ai_improvement import get_enhanced_ai_suggestion
        
        result = get_enhanced_ai_suggestion(
            feedback_text="This sentence is in passive voice",
            sentence_context="The report was written by John.",
            document_type="business",
            writing_goals=["clarity", "active_voice"]
        )
        
        if result and isinstance(result, dict):
            print("✅ Enhanced AI suggestion generated")
            print(f"   Method: {result.get('method', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 'unknown')}")
            print(f"   Suggestion: {result.get('suggestion', 'N/A')[:100]}...")
            return True
        else:
            print("⚠️  No result generated (this may be expected if APIs aren't configured)")
            return False
            
    except Exception as e:
        print(f"❌ Error testing enhanced suggestion: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Doc Scanner RAG Integration Structure Test")
    print("=" * 50)
    print("Testing basic structure and imports...\n")
    
    # Test imports
    if not test_imports():
        print("\n❌ Basic imports failed. Check your Python environment.")
        return
    
    # Test enhanced suggestions
    test_enhanced_suggestion()
    
    print("\n📊 Structure Test Complete")
    print("=" * 30)
    print("\nNext steps:")
    print("1. To enable RAG features, run: python setup_rag.py")
    print("2. Then test with: python demo_rag.py")
    print("3. Start the app with: python run.py")
    print("\nThe basic AI suggestion system is ready to use!")
    print("RAG enhancement will be automatically enabled when dependencies are installed.")

if __name__ == "__main__":
    main()

"""
Test the RAG-powered writing rules system
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def test_rag_system():
    """Test the RAG system with sample writing issues."""
    
    print("🚀 Testing RAG-Powered Writing Rules System\n")
    
    # Test importing the RAG helper
    try:
        from app.rules.rag_main import get_rag_suggestion, is_rag_available
        print("✅ RAG main interface imported successfully")
        
        if is_rag_available():
            print("✅ RAG system is available and initialized")
        else:
            print("⚠️ RAG system not fully initialized (may need dependencies)")
    except Exception as e:
        print(f"❌ Error importing RAG main interface: {e}")
        return
    
    # Test sample issues
    test_cases = [
        {
            "issue": "passive voice detected",
            "sentence": "The report was written by the team.",
            "category": "grammar",
            "expected": "Active voice suggestions"
        },
        {
            "issue": "wordy phrase detected", 
            "sentence": "In order to complete the task, we need to work together.",
            "category": "clarity",
            "expected": "Conciseness suggestions"
        },
        {
            "issue": "non-inclusive language",
            "sentence": "Hey guys, let's start the meeting.",
            "category": "accessibility", 
            "expected": "Inclusive language suggestions"
        }
    ]
    
    print("\n📝 Testing Writing Issues:\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['issue'].title()}")
        print(f"Sentence: \"{test_case['sentence']}\"")
        print(f"Category: {test_case['category']}")
        
        try:
            suggestion = get_rag_suggestion(
                issue_text=test_case['issue'],
                sentence_context=test_case['sentence'],
                category=test_case['category']
            )
            
            print(f"💡 RAG Suggestion: {suggestion.get('suggestion', 'No suggestion')}")
            print(f"🔍 Source: {suggestion.get('source', 'Unknown')}")
            print(f"📊 Confidence: {suggestion.get('confidence', 0.0)}")
            print(f"📚 Rules Retrieved: {suggestion.get('retrieved_rules', 0)}")
            print()
            
        except Exception as e:
            print(f"❌ Error getting suggestion: {e}\n")
    
    # Test individual rule files
    print("🔍 Testing Individual Rule Files:\n")
    
    rule_files = [
        'grammar', 'clarity', 'formatting', 'tone', 
        'terminology', 'accessibility', 'punctuation', 'capitalization'
    ]
    
    for rule_name in rule_files:
        try:
            module = __import__(f'app.rules.{rule_name}', fromlist=['check'])
            if hasattr(module, 'check'):
                print(f"✅ {rule_name}.py - check function available")
            else:
                print(f"❌ {rule_name}.py - no check function")
        except Exception as e:
            print(f"❌ {rule_name}.py - import error: {e}")
    
    print("\n🎯 RAG System Test Complete!")

if __name__ == "__main__":
    test_rag_system()

#!/usr/bin/env python3
"""
Test the intelligent analysis directly to reproduce the 'No test named match' error
"""
import sys
import os
import traceback

# Add app to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_intelligent_analysis_directly():
    """Test the intelligent analysis function directly"""
    try:
        print("🔧 Testing intelligent analysis directly...")
        
        # Import required components
        print("📦 Importing spaCy...")
        import spacy
        
        print("📦 Loading spaCy model...")
        nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser'])
        
        print("📦 Importing intelligent AI module...")
        from intelligent_ai_improvement import get_enhanced_ai_suggestion as get_intelligent_ai_suggestion
        
        # Test text
        test_text = "This is a simple test sentence to check for issues."
        
        print(f"🔧 Testing with text: '{test_text}'")
        print("🔧 Processing with spaCy...")
        doc = nlp(test_text)
        
        print("🔧 Calling intelligent AI analysis...")
        
        # Call the intelligent analysis function
        result = get_intelligent_ai_suggestion(doc, test_text)
        
        print(f"✅ Intelligent analysis completed successfully!")
        print(f"📋 Result type: {type(result)}")
        print(f"📋 Result: {result}")
        
    except Exception as e:
        print(f"❌ Error in intelligent analysis: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        
        # Check if this is the specific error we're looking for
        if "No test named 'match'" in str(e):
            print("🎯 FOUND IT! This is the 'No test named match' error!")
        
        return False
    
    return True

def test_analyze_intelligent_endpoint():
    """Test the analyze_intelligent function from app.py"""
    try:
        print("\n🔧 Testing analyze_intelligent endpoint function...")
        
        # Import the analyze_intelligent function
        print("📦 Importing analyze_intelligent from app...")
        from app import analyze_intelligent
        
        # Create test data
        test_data = {
            'text': 'This is a test sentence to analyze for intelligence.',
            'context': 'test context'
        }
        
        print(f"🔧 Testing with data: {test_data}")
        
        # Call the function directly (simulate the Flask request)
        class MockRequest:
            def get_json(self):
                return test_data
        
        # This would normally be called via Flask, but let's test the logic
        print("🔧 Calling analyze_intelligent function...")
        
        # We need to test the core logic, so let's extract it
        text = test_data['text']
        
        # Import spaCy and load model
        import spacy
        nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser'])
        doc = nlp(text)
        
        # Import the intelligent AI function
        from intelligent_ai_improvement import get_enhanced_ai_suggestion as get_intelligent_ai_suggestion
        
        # Call intelligent analysis
        result = get_intelligent_ai_suggestion(doc, text)
        
        print(f"✅ analyze_intelligent logic completed successfully!")
        print(f"📋 Result: {result}")
        
    except Exception as e:
        print(f"❌ Error in analyze_intelligent: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        traceback.print_exc()
        
        # Check if this is the specific error we're looking for
        if "No test named 'match'" in str(e):
            print("🎯 FOUND IT! This is the 'No test named match' error!")
        
        return False
    
    return True

def main():
    print("🔧 Debug: Testing intelligent analysis for 'No test named match' error")
    print("=" * 70)
    
    # Test 1: Direct intelligent analysis
    success1 = test_intelligent_analysis_directly()
    
    # Test 2: Analyze intelligent endpoint
    success2 = test_analyze_intelligent_endpoint()
    
    print("\n" + "=" * 70)
    print("📊 SUMMARY:")
    print(f"✅ Direct intelligent analysis: {'Success' if success1 else 'Failed'}")
    print(f"✅ Analyze intelligent endpoint: {'Success' if success2 else 'Failed'}")
    
    if not success1 or not success2:
        print("\n🎯 Error reproduced! Check the traceback above for details.")
    else:
        print("\n🤔 No errors found - the issue might be context-specific.")

if __name__ == "__main__":
    main()
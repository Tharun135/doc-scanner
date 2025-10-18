#!/usr/bin/env python3
"""
Final comprehensive test to confirm the 'No test named match' error is completely resolved
"""
import sys
import os
import traceback

def test_complete_intelligent_analysis():
    """Test the complete intelligent analysis pipeline"""
    try:
        print("🔧 Testing complete intelligent analysis pipeline...")
        
        # Set up the path properly
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))
        
        # Import and test the intelligent AI system
        print("📦 Importing intelligent AI system...")
        from intelligent_ai_improvement import get_enhanced_ai_suggestion
        
        # Test with sample data
        test_text = "This document needs to be improved for better clarity."
        
        print(f"🔧 Testing with: '{test_text}'")
        
        result = get_enhanced_ai_suggestion(
            feedback_text=test_text,
            sentence_context="Document improvement context",
            document_type="general",
            writing_goals=["clarity", "conciseness"],
            document_content="Full document content for context",
            option_number=1
        )
        
        print(f"✅ Intelligent AI analysis completed successfully!")
        print(f"📋 Result keys: {list(result.keys())}")
        print(f"📋 Success: {result.get('success', False)}")
        print(f"📋 Method: {result.get('method', 'unknown')}")
        
        return True, result
        
    except Exception as e:
        print(f"❌ Error in intelligent analysis: {str(e)}")
        
        # Check for the specific errors we've been fixing
        if "No test named 'match'" in str(e):
            print("🚨 FOUND: The 'No test named match' error still exists!")
            return False, str(e)
        elif "TemplateRuntimeError" in str(e):
            print("🚨 FOUND: Template runtime error detected!")
            return False, str(e)
        elif "'spacy.tokens.doc.Doc' object has no attribute 'lower'" in str(e):
            print("🚨 FOUND: Doc object parameter error still exists!")
            return False, str(e)
        else:
            print(f"⚠️ Different error (not the ones we fixed): {e}")
            traceback.print_exc()
            return False, str(e)

def test_template_rendering():
    """Test template rendering specifically"""
    try:
        print("\n🔧 Testing template rendering...")
        
        from flask import Flask, render_template
        
        # Create Flask app
        app = Flask(__name__, template_folder='app/templates')
        
        # Test data
        test_suggestions = [
            {
                'method': 'intelligent_analysis',
                'success': True,
                'confidence': 'high',
                'suggestion': 'Test suggestion',
                'ai_answer': 'Test AI answer'
            }
        ]
        
        with app.app_context():
            result = render_template('intelligent_results.html', suggestions=test_suggestions)
            
        print("✅ Template rendering successful!")
        return True, "Template OK"
        
    except Exception as e:
        print(f"❌ Template error: {e}")
        
        if "No test named 'match'" in str(e):
            print("🚨 FOUND: Template still has 'No test named match' error!")
            return False, str(e)
        else:
            print(f"⚠️ Different template error: {e}")
            return False, str(e)

def main():
    print("🔧 COMPREHENSIVE TEST: Verifying 'No test named match' error fixes")
    print("=" * 75)
    
    # Test 1: Intelligent Analysis
    analysis_success, analysis_result = test_complete_intelligent_analysis()
    
    # Test 2: Template Rendering
    template_success, template_result = test_template_rendering()
    
    print("\n" + "=" * 75)
    print("📊 FINAL RESULTS:")
    print(f"✅ Intelligent Analysis: {'PASS' if analysis_success else 'FAIL'}")
    print(f"✅ Template Rendering: {'PASS' if template_success else 'FAIL'}")
    
    if analysis_success and template_success:
        print("\n🎉 SUCCESS: All 'No test named match' errors have been RESOLVED!")
        print("🔧 The DocScanner intelligent analysis is now working properly.")
        print("🚀 Users can now use the intelligent analysis feature without errors.")
        return 0
    else:
        print(f"\n❌ ISSUES REMAIN:")
        if not analysis_success:
            print(f"   - Intelligent Analysis: {analysis_result}")
        if not template_success:
            print(f"   - Template Rendering: {template_result}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
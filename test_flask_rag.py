#!/usr/bin/env python3
"""
Test the Flask app RAG system integration
"""

import sys
import os

# Add the app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

print("🚀 Testing Flask App RAG Integration...")

try:
    # Test imports
    from app.enhanced_rag_complete import get_enhanced_suggestion, get_rag_status
    print("✅ Enhanced RAG system imported successfully")
    
    # Test RAG status
    status = get_rag_status()
    print(f"📊 RAG Status: {status}")
    
    # Test if dependencies are now working
    if status.get('dependencies', {}).get('llamaindex'):
        print("🎉 LlamaIndex dependencies are now working!")
        
        # Test a simple suggestion
        result = get_enhanced_suggestion(
            issue_text="This sentence is written in passive voice.",
            issue_type="passive_voice",
            context="Test document"
        )
        
        print("📝 Test suggestion result:")
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   Response: {result.get('enhanced_response', 'No response')[:100]}...")
        
    else:
        print("⚠️  RAG dependencies still need configuration")
        print("   Checking individual components...")
        deps = status.get('dependencies', {})
        for component, available in deps.items():
            icon = "✅" if available else "❌"
            print(f"   {icon} {component}: {available}")
            
except Exception as e:
    print(f"❌ Error testing RAG system: {e}")
    import traceback
    traceback.print_exc()

print("🏁 RAG integration test completed!")

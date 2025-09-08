#!/usr/bin/env python3
"""
Test the Smart Rewriter with the specific technical content that was failing
"""

from smart_rewriter import SmartDocumentRewriter

def test_smart_rewriter():
    print("🧪 Testing Smart Document Rewriter")
    print("=" * 60)
    
    # Your specific technical content that was not being rewritten
    technical_content = """Requesting for the complete process image of the configured tags

SLMP Connector supports the "Update Request" functionality. This enables you to receive the complete process image of the configured tags. In case the application fails to receive the initial publish of the complete process image by the SLMP Connector app, you can initiate request for the same.

You must add a topic in IE Databus in the following format to receive the configured data: ie/c/j/simatic/v1/updaterequest

where ie: industrial edge, c: control, j: jsonThe JSON payload structure for "Update Request" is as follows:

{"Path" : "<connector-id>/<connection-name>/<collection-name>"}

connector-id should be"slmp1" and collection-name should be "default" for SLMP Connector, since only the "default" collection is currently supported.

For receiving the last Tag data of all deployed tags under all connections
{"Path" : "slmp1/default"}

For receiving the last Tag data of the deployed tags under a specific connection
{"Path" : "slmp1/<connection-name>/default>"}"""

    print(f"📄 Original Technical Content ({len(technical_content)} chars):")
    print("-" * 40)
    print(technical_content[:200] + "..." if len(technical_content) > 200 else technical_content)
    
    # Create smart rewriter
    rewriter = SmartDocumentRewriter()
    
    print("\n🔍 Step 1: Analyzing document structure...")
    analysis = rewriter.analyze_document_structure(technical_content)
    
    print(f"📊 Analysis Results:")
    print(f"  • Sentences: {analysis['sentence_count']}")
    print(f"  • Avg sentence length: {analysis['avg_sentence_length']:.1f} words")
    print(f"  • Complex sentences: {len(analysis['complex_sentences'])}")
    print(f"  • Technical terms found: {len(set(analysis['technical_terms']))}")
    print(f"  • Improvement areas: {', '.join(analysis['improvement_areas'])}")
    
    print("\n🎯 Step 2: Creating targeted rewrite strategy...")
    
    # Test the smart rewriter
    result = rewriter.smart_rewrite_document(technical_content, mode='simplicity')
    
    print(f"\n✅ Result: Success = {result['success']}")
    
    if result['success']:
        rewritten = result['rewritten_text']
        print(f"\n📝 Rewritten Content ({len(rewritten)} chars):")
        print("-" * 40)
        print(rewritten)
        
        # Check if it actually changed
        if rewritten.strip() != technical_content.strip():
            print(f"\n🎉 SUCCESS: Content was actually rewritten!")
            print(f"📈 Length change: {len(technical_content)} → {len(rewritten)} chars")
        else:
            print(f"\n⚠️ WARNING: Content appears unchanged")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_smart_rewriter()

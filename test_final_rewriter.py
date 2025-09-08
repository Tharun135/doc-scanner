#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from rewriter.ollama_rewriter import OllamaRewriter

def test_user_content():
    """Test with the user's specific SLMP connector content"""
    
    # The exact content the user provided
    test_content = """<b>SLMP connector</b><br><br>This section describes the details required to create SLMP connection to the Mitsubishi PLC. The recommended structure is as follows. The structure is included to make it easy to understand the recommended approach to implementation.

<b>payloadType</b>: The encoding of the communication method for the SLMP PLC. This indicates if it is ASCII encoding or Binary encoding.

<b>msgStructureScheme</b>: This indicates the version of the message structure scheme for the required message format. In the SLMP implementation, this will be &quot;SLMP&quot;. Here's the usage example:

<b>msgStructureSchemeVersion</b>: This indicates the version of the message structure scheme required to work with the SLMP connector.

<b>provideAppInstanceId</b>: This indicates if the application instance id is provided as part of the payload or is going to be added automatically by the SDK.

<b>payloadMsgType</b>: This indicates the message type that is passed to the payload.

<b>Possible Values</b>: 1) <b>accessmode</b> bulk mode and 2) <b>connectionname</b> single element mode

<b>collectionname</b>: The above elements make it easy to understand the data. The data to be used to create the collection in the SLMP collection.

<b>Please provide more information to complete</b>"""
    
    print("Testing Enhanced Rewriter with User's SLMP Content")
    print("=" * 60)
    print(f"Original text ({len(test_content)} characters):")
    print(test_content[:200] + "..." if len(test_content) > 200 else test_content)
    print("\n" + "=" * 60)
    
    # Test the rewriter
    rewriter = OllamaRewriter()
    result = rewriter.rewrite_document(test_content, mode="simplicity")
    
    print("RESULTS:")
    print(f"Success: {result.get('success', False)}")
    print(f"Error: {result.get('error', 'None')}")
    
    original_text = result.get('original_text', '')
    rewritten_text = result.get('rewritten_text', '')
    
    print(f"\nOriginal length: {len(original_text)} characters")
    print(f"Rewritten length: {len(rewritten_text)} characters")
    
    # Check if text actually changed
    changed = original_text != rewritten_text
    print(f"Content changed: {changed}")
    
    if changed:
        print(f"\nLength change: {len(rewritten_text) - len(original_text):+d} characters")
        
        # Show first 300 characters of rewritten text
        print(f"\nRewritten text (first 300 chars):")
        print(rewritten_text[:300] + ("..." if len(rewritten_text) > 300 else ""))
        
        # Show improvement metrics
        if 'improvement_percentage' in result:
            print(f"\nImprovement: {result['improvement_percentage']:.1f}%")
    else:
        print("\nWARNING: Text was not changed!")
        
        # Check what method was used
        if result.get('method_used'):
            print(f"Method used: {result['method_used']}")
    
    print("\n" + "=" * 60)
    return result

if __name__ == "__main__":
    test_user_content()

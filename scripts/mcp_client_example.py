"""
MCP Client Example for Doc-Scanner

This demonstrates how to connect to the DocScanner MCP server
and use its tools for document analysis and AI suggestions.
"""

import asyncio
import json
import websockets


async def call_mcp_tool(websocket, tool_name, arguments):
    """Call an MCP tool and return the result."""
    request = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/call',
        'params': {
            'name': tool_name,
            'arguments': arguments
        }
    }
    
    # Send request
    await websocket.send(json.dumps(request))
    
    # Receive response
    response = await websocket.recv()
    result = json.loads(response)
    
    return result


async def list_tools(websocket):
    """List available MCP tools."""
    request = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'tools/list',
        'params': {}
    }
    
    await websocket.send(json.dumps(request))
    response = await websocket.recv()
    result = json.loads(response)
    
    return result


async def main():
    """Main client demonstration."""
    uri = "ws://localhost:8765"
    
    print(f"Connecting to DocScanner MCP server at {uri}...")
    
    async with websockets.connect(uri) as websocket:
        print("✅ Connected!")
        
        # 1. Initialize the connection
        print("\n1. Initializing connection...")
        init_request = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': 'initialize',
            'params': {
                'protocolVersion': '2024-11-05',
                'capabilities': {},
                'clientInfo': {
                    'name': 'DocScanner Test Client',
                    'version': '1.0.0'
                }
            }
        }
        await websocket.send(json.dumps(init_request))
        response = await websocket.recv()
        init_result = json.loads(response)
        print(f"   Server: {init_result['result']['serverInfo']['name']}")
        print(f"   Version: {init_result['result']['serverInfo']['version']}")
        
        # 2. List available tools
        print("\n2. Listing available tools...")
        tools_result = await list_tools(websocket)
        for tool in tools_result['result']['tools']:
            print(f"   - {tool['name']}: {tool['description']}")
        
        # 3. Analyze a document
        print("\n3. Analyzing sample text...")
        sample_text = "The system was configured by the administrator. You should click the button."
        
        analysis_result = await call_mcp_tool(
            websocket,
            'analyze_document',
            {
                'text': sample_text,
                'document_type': 'technical'
            }
        )
        
        if 'result' in analysis_result:
            content = analysis_result['result']['content'][0]['text']
            analysis = json.loads(content)
            print(f"   Total sentences: {analysis.get('total_sentences', 0)}")
            print(f"   Total issues: {analysis.get('total_issues', 0)}")
            if analysis.get('issues'):
                print(f"   First issue: {analysis['issues'][0].get('feedback_text', 'N/A')}")
        
        # 4. Generate AI suggestion
        print("\n4. Generating AI suggestion...")
        suggestion_result = await call_mcp_tool(
            websocket,
            'generate_suggestion',
            {
                'feedback_text': 'passive voice detected',
                'sentence_context': 'The system was configured by the administrator.',
                'document_type': 'technical'
            }
        )
        
        if 'result' in suggestion_result:
            content = suggestion_result['result']['content'][0]['text']
            suggestion = json.loads(content)
            print(f"   Suggestion: {suggestion.get('suggestion', 'N/A')}")
            print(f"   Confidence: {suggestion.get('confidence', 'N/A')}")
        
        print("\n✅ All tests completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ConnectionRefusedError:
        print("❌ Error: Could not connect to MCP server.")
        print("   Make sure the server is running: python start_mcp_server.py")
    except Exception as e:
        print(f"❌ Error: {e}")

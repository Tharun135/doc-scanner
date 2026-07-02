"""
Standalone MCP Server for Doc-Scanner
Quick start script without relative import issues
"""

import asyncio
import json
import logging
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.ai_improvement import get_enhanced_ai_suggestion
from app.app import analyze_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocScannerMCPServer:
    """Simple MCP server for doc-scanner."""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = {}
        
    async def start(self):
        """Start the MCP server."""
        import websockets
        
        logger.info(f"Starting DocScanner MCP server on ws://{self.host}:{self.port}")
        
        try:
            server = await websockets.serve(
                self.handle_client,
                self.host,
                self.port
            )
            logger.info(f"✅ MCP server running on ws://{self.host}:{self.port}")
            logger.info("Tools available: analyze_document, generate_suggestion")
            
            await asyncio.Future()  # Run forever
            
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise
    
    async def handle_client(self, websocket):
        """Handle WebSocket client connection."""
        client_id = id(websocket)
        logger.info(f"Client {client_id} connected")
        
        try:
            async for message in websocket:
                try:
                    request = json.loads(message)
                    response = await self.handle_request(request)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    error = {
                        'jsonrpc': '2.0',
                        'id': None,
                        'error': {'code': -32700, 'message': 'Parse error'}
                    }
                    await websocket.send(json.dumps(error))
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    error = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'error': {'code': -32603, 'message': str(e)}
                    }
                    await websocket.send(json.dumps(error))
        finally:
            logger.info(f"Client {client_id} disconnected")
    
    async def handle_request(self, request):
        """Handle MCP request."""
        method = request.get('method')
        params = request.get('params', {})
        req_id = request.get('id')
        
        logger.info(f"Received request: {method}")
        
        if method == 'initialize':
            result = {
                'protocolVersion': '2024-11-05',
                'capabilities': {
                    'tools': {},
                    'resources': {}
                },
                'serverInfo': {
                    'name': 'DocScanner MCP Server',
                    'version': '1.0.0'
                }
            }
        
        elif method == 'tools/list':
            result = {
                'tools': [
                    {
                        'name': 'analyze_document',
                        'description': 'Analyze text for writing quality issues',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'text': {'type': 'string', 'description': 'Text to analyze'},
                                'document_type': {'type': 'string', 'default': 'general'}
                            },
                            'required': ['text']
                        }
                    },
                    {
                        'name': 'generate_suggestion',
                        'description': 'Generate AI suggestion for improvement',
                        'inputSchema': {
                            'type': 'object',
                            'properties': {
                                'feedback_text': {'type': 'string'},
                                'sentence_context': {'type': 'string'},
                                'document_type': {'type': 'string', 'default': 'general'}
                            },
                            'required': ['feedback_text', 'sentence_context']
                        }
                    }
                ]
            }
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            arguments = params.get('arguments', {})
            
            if tool_name == 'analyze_document':
                # Analyze text
                text = arguments.get('text', '')
                doc_type = arguments.get('document_type', 'general')
                
                analysis_result = analyze_text(text, document_type=doc_type)
                
                result = {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps(analysis_result, indent=2)
                    }]
                }
            
            elif tool_name == 'generate_suggestion':
                # Generate AI suggestion
                feedback = arguments.get('feedback_text', '')
                sentence = arguments.get('sentence_context', '')
                doc_type = arguments.get('document_type', 'general')
                
                suggestion = get_enhanced_ai_suggestion(
                    feedback_text=feedback,
                    sentence_context=sentence,
                    document_type=doc_type
                )
                
                result = {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps(suggestion, indent=2)
                    }]
                }
            
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        
        else:
            raise ValueError(f"Unknown method: {method}")
        
        return {
            'jsonrpc': '2.0',
            'id': req_id,
            'result': result
        }


async def main():
    parser = argparse.ArgumentParser(description='DocScanner MCP Server')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8765, help='Server port')
    
    args = parser.parse_args()
    
    server = DocScannerMCPServer(args.host, args.port)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    asyncio.run(main())

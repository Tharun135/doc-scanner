"""
Model Context Protocol (MCP) Server for Document Review Agent
Provides standardized interface for the agent to work with VS Code and other clients.
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import uuid
from datetime import datetime

from .agent import DocumentReviewAgent
from .protocol import AgentMessage, AgentCommunicationProtocol

logger = logging.getLogger(__name__)


class MCPServer:
    """
    Model Context Protocol server for the Document Review Agent.
    Provides a standardized interface for VS Code extensions and other clients.
    """
    
    def __init__(self, agent: DocumentReviewAgent, host: str = "localhost", port: int = 8765):
        self.agent = agent
        self.host = host
        self.port = port
        self.clients = {}
        self.server = None
        self.communication = AgentCommunicationProtocol()
        
        # Register MCP method handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP method handlers."""
        handlers = {
            'initialize': self._handle_initialize,
            'tools/list': self._handle_tools_list,
            'tools/call': self._handle_tools_call,
            'resources/list': self._handle_resources_list,
            'resources/read': self._handle_resources_read,
            'prompts/list': self._handle_prompts_list,
            'prompts/get': self._handle_prompts_get,
            'agent/status': self._handle_agent_status,
            'agent/capabilities': self._handle_agent_capabilities,
            'document/analyze': self._handle_document_analyze,
            'document/batch': self._handle_document_batch,
            'ai/suggest': self._handle_ai_suggest,
            'quality/assess': self._handle_quality_assess
        }
        
        for method, handler in handlers.items():
            self.communication.register_handler(method, handler)
    
    async def start(self):
        """Start the MCP server."""
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        
        # Start the agent first
        await self.agent.start()
        
        # Start WebSocket server
        import websockets
        
        self.server = await websockets.serve(
            self._handle_client,
            self.host,
            self.port
        )
        
        logger.info(f"MCP server started on ws://{self.host}:{self.port}")
    
    async def stop(self):
        """Stop the MCP server."""
        logger.info("Stopping MCP server")
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        await self.agent.stop()
        
        logger.info("MCP server stopped")
    
    async def _handle_client(self, websocket, path):
        """Handle a new client connection."""
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket
        
        logger.info(f"Client {client_id} connected")
        
        try:
            async for message in websocket:
                try:
                    # Parse JSON message
                    data = json.loads(message)
                    
                    # Create agent message
                    agent_message = AgentMessage(
                        id=data.get('id', str(uuid.uuid4())),
                        type=data.get('type', 'request'),
                        method=data.get('method'),
                        params=data.get('params')
                    )
                    
                    # Handle the message
                    response = await self.communication.handle_message(agent_message)
                    
                    if response:
                        # Send response back to client
                        response_data = {
                            'id': response.id,
                            'type': response.type,
                            'result': response.result,
                            'error': response.error
                        }
                        
                        await websocket.send(json.dumps(response_data))
                
                except json.JSONDecodeError:
                    error_response = {
                        'id': None,
                        'type': 'error',
                        'error': {'code': -32700, 'message': 'Parse error'}
                    }
                    await websocket.send(json.dumps(error_response))
                
                except Exception as e:
                    logger.error(f"Error handling message: {str(e)}")
                    error_response = {
                        'id': None,
                        'type': 'error',
                        'error': {'code': -32603, 'message': f'Internal error: {str(e)}'}
                    }
                    await websocket.send(json.dumps(error_response))
        
        except Exception as e:
            logger.error(f"Client {client_id} error: {str(e)}")
        
        finally:
            del self.clients[client_id]
            logger.info(f"Client {client_id} disconnected")
    
    # MCP Method Handlers
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request."""
        return {
            'protocolVersion': '1.0.0',
            'capabilities': {
                'tools': {'listChanged': True},
                'resources': {'subscribe': True, 'listChanged': True},
                'prompts': {'listChanged': True},
                'agent': {
                    'document_analysis': True,
                    'ai_suggestions': True,
                    'batch_processing': True,
                    'quality_assessment': True
                }
            },
            'serverInfo': {
                'name': 'Document Review Agent',
                'version': '1.0.0',
                'description': 'AI-powered document review and analysis agent'
            }
        }
    
    async def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available tools."""
        tools = [
            {
                'name': 'analyze_document',
                'description': 'Analyze a document for writing quality and issues',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'document_path': {'type': 'string', 'description': 'Path to the document'},
                        'document_type': {'type': 'string', 'default': 'general'},
                        'writing_goals': {'type': 'array', 'items': {'type': 'string'}}
                    },
                    'required': ['document_path']
                }
            },
            {
                'name': 'generate_suggestion',
                'description': 'Generate AI suggestions for writing issues',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'feedback_text': {'type': 'string', 'description': 'The issue description'},
                        'sentence_context': {'type': 'string', 'description': 'The sentence context'},
                        'document_type': {'type': 'string', 'default': 'general'}
                    },
                    'required': ['feedback_text']
                }
            },
            {
                'name': 'batch_process',
                'description': 'Process multiple documents in batch',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'file_paths': {'type': 'array', 'items': {'type': 'string'}},
                        'parallel': {'type': 'boolean', 'default': True}
                    },
                    'required': ['file_paths']
                }
            },
            {
                'name': 'assess_quality',
                'description': 'Assess document quality',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'document_path': {'type': 'string', 'description': 'Path to the document'}
                    },
                    'required': ['document_path']
                }
            }
        ]
        
        return {'tools': tools}
    
    async def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if tool_name == 'analyze_document':
            result = await self.agent.execute_task('document_analysis', arguments)
        elif tool_name == 'generate_suggestion':
            result = await self.agent.execute_task('ai_suggestions', arguments)
        elif tool_name == 'batch_process':
            result = await self.agent.execute_task('batch_processing', arguments)
        elif tool_name == 'assess_quality':
            result = await self.agent.execute_task('quality_assessment', arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return {
            'content': [
                {
                    'type': 'text',
                    'text': json.dumps(asdict(result), indent=2, default=str)
                }
            ]
        }
    
    async def _handle_resources_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available resources."""
        resources = [
            {
                'uri': 'agent://status',
                'name': 'Agent Status',
                'description': 'Current status of the document review agent'
            },
            {
                'uri': 'agent://capabilities',
                'name': 'Agent Capabilities',
                'description': 'List of agent capabilities'
            },
            {
                'uri': 'agent://metrics',
                'name': 'Performance Metrics',
                'description': 'Agent performance metrics'
            }
        ]
        
        return {'resources': resources}
    
    async def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a specific resource."""
        uri = params.get('uri')
        
        if uri == 'agent://status':
            content = json.dumps(self.agent.get_status(), indent=2)
        elif uri == 'agent://capabilities':
            capabilities = [asdict(cap) for cap in self.agent.capabilities]
            content = json.dumps({'capabilities': capabilities}, indent=2)
        elif uri == 'agent://metrics':
            # Get basic metrics
            status = self.agent.get_status()
            metrics = {
                'queue_size': status.get('queue_size', 0),
                'cached_results': status.get('cached_results', 0),
                'uptime': 'N/A',  # Could track actual uptime
                'total_processed': 'N/A'  # Could track total processed documents
            }
            content = json.dumps(metrics, indent=2)
        else:
            raise ValueError(f"Unknown resource: {uri}")
        
        return {
            'contents': [
                {
                    'uri': uri,
                    'mimeType': 'application/json',
                    'text': content
                }
            ]
        }
    
    async def _handle_prompts_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available prompts."""
        prompts = [
            {
                'name': 'analyze_document',
                'description': 'Analyze a document for quality issues',
                'arguments': [
                    {
                        'name': 'document_path',
                        'description': 'Path to the document to analyze',
                        'required': True
                    },
                    {
                        'name': 'focus_areas',
                        'description': 'Specific areas to focus on (grammar, style, clarity)',
                        'required': False
                    }
                ]
            },
            {
                'name': 'improve_writing',
                'description': 'Get suggestions to improve writing quality',
                'arguments': [
                    {
                        'name': 'text',
                        'description': 'Text to improve',
                        'required': True
                    },
                    {
                        'name': 'style',
                        'description': 'Target writing style (formal, casual, technical)',
                        'required': False
                    }
                ]
            }
        ]
        
        return {'prompts': prompts}
    
    async def _handle_prompts_get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a specific prompt."""
        name = params.get('name')
        arguments = params.get('arguments', {})
        
        if name == 'analyze_document':
            document_path = arguments.get('document_path', '')
            focus_areas = arguments.get('focus_areas', 'general quality')
            
            prompt = f"""Analyze the document at '{document_path}' for writing quality.

Focus on: {focus_areas}

The analysis will include:
- Grammar and syntax issues
- Sentence structure and clarity
- Writing style and tone
- Readability and flow
- Specific suggestions for improvement

Please provide the document path to begin analysis."""
            
        elif name == 'improve_writing':
            text = arguments.get('text', '')
            style = arguments.get('style', 'professional')
            
            prompt = f"""Improve the following text for {style} writing:

"{text}"

I'll analyze this text and provide specific suggestions for:
- Clarity and conciseness
- Grammar and style
- Word choice and tone
- Structure and flow

Please provide the text you'd like me to review."""
        
        else:
            raise ValueError(f"Unknown prompt: {name}")
        
        return {
            'description': f"Prompt for {name}",
            'messages': [
                {
                    'role': 'user',
                    'content': {
                        'type': 'text',
                        'text': prompt
                    }
                }
            ]
        }
    
    # Agent-specific handlers
    
    async def _handle_agent_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent status."""
        return self.agent.get_status()
    
    async def _handle_agent_capabilities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get agent capabilities."""
        return {
            'capabilities': [asdict(cap) for cap in self.agent.capabilities]
        }
    
    async def _handle_document_analyze(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a document."""
        result = await self.agent.execute_task('document_analysis', params)
        return asdict(result)
    
    async def _handle_document_batch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process documents in batch."""
        result = await self.agent.execute_task('batch_processing', params)
        return asdict(result)
    
    async def _handle_ai_suggest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI suggestions."""
        result = await self.agent.execute_task('ai_suggestions', params)
        return asdict(result)
    
    async def _handle_quality_assess(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Assess document quality."""
        result = await self.agent.execute_task('quality_assessment', params)
        return asdict(result)


# Utility function to start the MCP server
async def start_mcp_server(agent: DocumentReviewAgent = None, 
                          host: str = "localhost", 
                          port: int = 8765):
    """Start the MCP server with optional agent."""
    if agent is None:
        agent = DocumentReviewAgent()
    
    server = MCPServer(agent, host, port)
    await server.start()
    
    return server


# Main function for standalone server
async def main():
    """Main function to run the MCP server standalone."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Document Review Agent MCP Server')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8765, help='Server port')
    parser.add_argument('--log-level', default='INFO', help='Log level')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start server
    agent = DocumentReviewAgent()
    server = await start_mcp_server(agent, args.host, args.port)
    
    try:
        logger.info("MCP Server running. Press Ctrl+C to stop.")
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())

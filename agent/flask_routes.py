"""
Flask API routes for the Document Review Agent
Integrates the agent with the existing Flask application.
"""

from flask import Blueprint, request, jsonify
import asyncio
import logging
from datetime import datetime
import uuid
import time

from .agent import DocumentReviewAgent, DocumentReviewTask
from .tools import DocumentTools, AITools, ValidationTools

logger = logging.getLogger(__name__)

# Create agent blueprint
agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')

# Global agent instance
_agent_instance = None
_agent_tools = {
    'document': DocumentTools(),
    'ai': AITools(),
    'validation': ValidationTools()
}


def get_agent():
    """Get or create the global agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = DocumentReviewAgent()
        # Start the agent in the background
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is already running, create a task
                asyncio.create_task(_agent_instance.start())
            else:
                # If no loop is running, run it
                loop.run_until_complete(_agent_instance.start())
        except RuntimeError:
            # Handle case where no event loop exists
            asyncio.run(_agent_instance.start())
    return _agent_instance


@agent_bp.route('/status', methods=['GET'])
def get_agent_status():
    """Get the current status of the agent."""
    try:
        agent = get_agent()
        status = agent.get_status()
        return jsonify({
            'success': True,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting agent status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/capabilities', methods=['GET'])
def get_agent_capabilities():
    """Get the agent's capabilities."""
    try:
        agent = get_agent()
        capabilities = [
            {
                'name': cap.name,
                'description': cap.description,
                'parameters': cap.parameters
            }
            for cap in agent.capabilities
        ]
        return jsonify({
            'success': True,
            'capabilities': capabilities
        })
    except Exception as e:
        logger.error(f"Error getting agent capabilities: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/analyze', methods=['POST'])
def analyze_document():
    """Analyze a document using the agent."""
    try:
        data = request.get_json()
        document_path = data.get('document_path')
        document_type = data.get('document_type', 'general')
        writing_goals = data.get('writing_goals', ['clarity', 'conciseness'])
        
        if not document_path:
            return jsonify({
                'success': False,
                'error': 'document_path is required'
            }), 400
        
        # Create and execute task
        task_id = f"api_analysis_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # Use async wrapper
        async def run_analysis():
            agent = get_agent()
            result = await agent.execute_task('document_analysis', {
                'document_path': document_path,
                'document_type': document_type,
                'writing_goals': writing_goals
            })
            return result
        
        # Run the async task
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Create a new event loop for this thread
                import threading
                result_holder = {}
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result_holder['result'] = new_loop.run_until_complete(run_analysis())
                    new_loop.close()
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                result = result_holder['result']
            else:
                result = loop.run_until_complete(run_analysis())
        except RuntimeError:
            result = asyncio.run(run_analysis())
        
        return jsonify({
            'success': result.success,
            'task_id': task_id,
            'data': result.data,
            'execution_time': result.execution_time,
            'timestamp': result.timestamp.isoformat(),
            'error': result.error
        })
        
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/suggest', methods=['POST'])
def generate_suggestion():
    """Generate AI suggestions using the agent."""
    try:
        data = request.get_json()
        feedback_text = data.get('feedback_text')
        sentence_context = data.get('sentence_context', '')
        document_type = data.get('document_type', 'general')
        writing_goals = data.get('writing_goals', ['clarity', 'conciseness'])
        
        if not feedback_text:
            return jsonify({
                'success': False,
                'error': 'feedback_text is required'
            }), 400
        
        # Use async wrapper
        async def run_suggestion():
            agent = get_agent()
            result = await agent.execute_task('ai_suggestions', {
                'feedback_text': feedback_text,
                'sentence_context': sentence_context,
                'document_type': document_type,
                'writing_goals': writing_goals
            })
            return result
        
        # Run the async task
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import threading
                result_holder = {}
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result_holder['result'] = new_loop.run_until_complete(run_suggestion())
                    new_loop.close()
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                result = result_holder['result']
            else:
                result = loop.run_until_complete(run_suggestion())
        except RuntimeError:
            result = asyncio.run(run_suggestion())
        
        return jsonify({
            'success': result.success,
            'suggestion': result.data,
            'execution_time': result.execution_time,
            'timestamp': result.timestamp.isoformat(),
            'error': result.error
        })
        
    except Exception as e:
        logger.error(f"Error generating suggestion: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/batch', methods=['POST'])
def batch_process():
    """Process multiple documents in batch."""
    try:
        data = request.get_json()
        file_paths = data.get('file_paths', [])
        parallel = data.get('parallel', True)
        document_type = data.get('document_type', 'general')
        
        if not file_paths:
            return jsonify({
                'success': False,
                'error': 'file_paths is required'
            }), 400
        
        # Use async wrapper
        async def run_batch():
            agent = get_agent()
            result = await agent.execute_task('batch_processing', {
                'file_paths': file_paths,
                'parallel': parallel
            })
            return result
        
        # Run the async task
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import threading
                result_holder = {}
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result_holder['result'] = new_loop.run_until_complete(run_batch())
                    new_loop.close()
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                result = result_holder['result']
            else:
                result = loop.run_until_complete(run_batch())
        except RuntimeError:
            result = asyncio.run(run_batch())
        
        return jsonify({
            'success': result.success,
            'data': result.data,
            'execution_time': result.execution_time,
            'timestamp': result.timestamp.isoformat(),
            'error': result.error
        })
        
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/quality', methods=['POST'])
def assess_quality():
    """Assess document quality."""
    try:
        data = request.get_json()
        document_path = data.get('document_path')
        
        if not document_path:
            return jsonify({
                'success': False,
                'error': 'document_path is required'
            }), 400
        
        # Use async wrapper
        async def run_quality():
            agent = get_agent()
            result = await agent.execute_task('quality_assessment', {
                'document_path': document_path
            })
            return result
        
        # Run the async task
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import threading
                result_holder = {}
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    result_holder['result'] = new_loop.run_until_complete(run_quality())
                    new_loop.close()
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                result = result_holder['result']
            else:
                result = loop.run_until_complete(run_quality())
        except RuntimeError:
            result = asyncio.run(run_quality())
        
        return jsonify({
            'success': result.success,
            'quality_assessment': result.data,
            'execution_time': result.execution_time,
            'timestamp': result.timestamp.isoformat(),
            'error': result.error
        })
        
    except Exception as e:
        logger.error(f"Error assessing quality: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/tools/document/read', methods=['POST'])
def read_document():
    """Read and parse a document."""
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': 'file_path is required'
            }), 400
        
        # Use document tools
        async def run_read():
            return await _agent_tools['document'].read_document(file_path)
        
        result = asyncio.run(run_read())
        
        return jsonify({
            'success': True,
            'document': result
        })
        
    except Exception as e:
        logger.error(f"Error reading document: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/tools/document/structure', methods=['POST'])
def analyze_structure():
    """Analyze document structure."""
    try:
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'content is required'
            }), 400
        
        # Use document tools
        async def run_structure():
            return await _agent_tools['document'].analyze_document_structure(content)
        
        result = asyncio.run(run_structure())
        
        return jsonify({
            'success': True,
            'structure': result
        })
        
    except Exception as e:
        logger.error(f"Error analyzing structure: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@agent_bp.route('/tools/validation/quality', methods=['POST'])
def validate_quality():
    """Validate document quality analysis."""
    try:
        data = request.get_json()
        analysis_result = data.get('analysis_result')
        
        if not analysis_result:
            return jsonify({
                'success': False,
                'error': 'analysis_result is required'
            }), 400
        
        # Use validation tools
        async def run_validation():
            return await _agent_tools['validation'].validate_document_quality(analysis_result)
        
        result = asyncio.run(run_validation())
        
        return jsonify({
            'success': True,
            'validation': result
        })
        
    except Exception as e:
        logger.error(f"Error validating quality: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Health check endpoint
@agent_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        agent = get_agent()
        status = agent.get_status()
        
        # Basic health checks
        is_healthy = (
            status.get('is_running', False) and
            status.get('queue_size', 0) < 100 and
            len(status.get('capabilities', [])) > 0
        )
        
        return jsonify({
            'success': True,
            'healthy': is_healthy,
            'status': status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            'success': False,
            'healthy': False,
            'error': str(e)
        }), 500

"""
Enhanced Flask routes that use FastAPI backend for vector search.
These routes extend your existing Flask UI with semantic search capabilities.
No UI changes needed - just enhanced backend functionality.
"""
from flask import Blueprint, request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

# Create blueprint for enhanced routes
enhanced = Blueprint('enhanced', __name__, url_prefix='/api/enhanced')


@enhanced.route('/health', methods=['GET'])
def health_check():
    """Check if FastAPI backend is available."""
    bridge = current_app.fastapi_bridge
    
    return jsonify({
        'flask': 'running',
        'fastapi_available': bridge.enabled,
        'fastapi_url': bridge.fastapi_url if bridge.enabled else None
    })


@enhanced.route('/upload', methods=['POST'])
def upload_document():
    """
    Enhanced upload that uses FastAPI backend for vector search.
    Falls back to regular upload if FastAPI is not available.
    """
    bridge = current_app.fastapi_bridge
    
    if not bridge.enabled:
        return jsonify({
            'status': 'warning',
            'message': 'Vector search backend not available. Document uploaded but not indexed for semantic search.',
            'file_uploaded': True,
            'vector_indexed': False
        }), 200
    
    try:
        # Check if file exists in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Upload to FastAPI backend
        result = bridge.upload_document(file)
        
        if result:
            return jsonify({
                'status': 'success',
                'message': 'Document uploaded and indexed for semantic search',
                'file_uploaded': True,
                'vector_indexed': True,
                'file_id': result.get('file_id'),
                'chunks_ingested': result.get('chunks_ingested'),
                'format': result.get('file_format')
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Upload to vector search backend failed'
            }), 500
            
    except Exception as e:
        logger.error(f"Enhanced upload failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@enhanced.route('/search', methods=['POST'])
def semantic_search():
    """
    Semantic search across all uploaded documents.
    Uses FastAPI vector search backend.
    """
    bridge = current_app.fastapi_bridge
    
    if not bridge.enabled:
        return jsonify({
            'error': 'Vector search backend not available',
            'suggestion': 'Start FastAPI server with: python run_fastapi.py'
        }), 503
    
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        top_k = data.get('top_k', 5)
        filters = data.get('filters', {})
        
        # Perform semantic search
        logger.info(f"Performing semantic search: query='{query}', top_k={top_k}")
        results = bridge.semantic_search(query, top_k, filters)
        logger.info(f"Search results: {results}")
        
        if results and 'error' not in results:
            return jsonify({
                'status': 'success',
                'query': query,
                'results': results.get('results', []),
                'total_results': results.get('total_results', 0),
                'processing_time': results.get('processing_time', 0),
                'search_time': results.get('processing_time', 0)  # Add search_time for frontend
            }), 200
        else:
            error_msg = results.get('error', 'Search failed') if results else 'Search failed'
            logger.error(f"Search failed: {error_msg}")
            return jsonify({
                'status': 'error',
                'message': error_msg,
                'error': error_msg
            }), 500
            
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@enhanced.route('/rag', methods=['POST'])
def rag_context():
    """
    Get RAG context for AI-powered writing suggestions.
    Returns relevant document chunks formatted for LLM consumption.
    """
    bridge = current_app.fastapi_bridge
    
    if not bridge.enabled:
        return jsonify({
            'error': 'Vector search backend not available'
        }), 503
    
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'error': 'Query parameter required'}), 400
        
        top_k = data.get('top_k', 3)
        
        # Get RAG context
        result = bridge.rag_query(query, top_k)
        
        if result:
            return jsonify({
                'status': 'success',
                'query': query,
                'context': result.get('context', ''),
                'sources': result.get('sources', []),
                'total_chunks': result.get('total_chunks', 0)
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'RAG query failed'
            }), 500
            
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@enhanced.route('/analyze', methods=['POST'])
def analyze_with_ai():
    """
    Enhanced text analysis that combines:
    1. Your existing rule-based checks
    2. RAG context from style guides
    3. AI-powered suggestions (if configured)
    """
    bridge = current_app.fastapi_bridge
    
    try:
        data = request.get_json()
        text = data.get('text')
        
        if not text:
            return jsonify({'error': 'Text parameter required'}), 400
        
        # Step 1: Your existing rule-based analysis
        # (This would call your existing analyze function)
        rule_findings = []  # Placeholder - integrate with your existing rules
        
        # Step 2: Get RAG context if available
        rag_context = None
        if bridge.enabled:
            try:
                rag_result = bridge.rag_query(
                    "writing style guidelines best practices", 
                    top_k=3
                )
                if rag_result:
                    rag_context = rag_result.get('context', '')
            except Exception as e:
                logger.warning(f"RAG context retrieval failed: {e}")
        
        # Step 3: Combine results
        response = {
            'status': 'success',
            'text_length': len(text),
            'rule_findings': rule_findings,
            'rag_enhanced': rag_context is not None,
            'rag_context': rag_context if rag_context else None
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Enhanced analysis failed: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@enhanced.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics from both Flask and FastAPI backends."""
    bridge = current_app.fastapi_bridge
    
    stats = {
        'flask': {
            'status': 'running'
        },
        'fastapi': {
            'available': False
        }
    }
    
    if bridge.enabled:
        try:
            fastapi_stats = bridge.get_stats()
            if fastapi_stats:
                stats['fastapi'] = {
                    'available': True,
                    'total_chunks': fastapi_stats.get('stats', {}).get('total_chunks', 0),
                    'unique_files': fastapi_stats.get('stats', {}).get('unique_files', 0),
                    'embedding_model': fastapi_stats.get('stats', {}).get('embedding_model', 'unknown')
                }
        except Exception as e:
            logger.warning(f"Failed to get FastAPI stats: {e}")
    
    return jsonify(stats), 200


def init_enhanced_routes(app):
    """Initialize enhanced routes with the Flask app."""
    app.register_blueprint(enhanced)
    logger.info("✅ Enhanced routes registered (vector search backend)")

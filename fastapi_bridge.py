# fastapi_bridge.py
"""
Bridge module to integrate FastAPI endpoints into Flask app.
Use this during the transition period to gradually migrate from Flask to FastAPI.

Add this to your Flask app to proxy requests to FastAPI without changing the UI.
"""
import requests
import os
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

# FastAPI server URL (default localhost)
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")


class FastAPIBridge:
    """
    Bridge class to proxy requests from Flask to FastAPI.
    Provides transparent integration during migration.
    """
    
    def __init__(self, fastapi_url: str = FASTAPI_URL):
        self.fastapi_url = fastapi_url
        self.enabled = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if FastAPI server is running."""
        try:
            response = requests.get(f"{self.fastapi_url}/health", timeout=2)
            if response.status_code == 200:
                logger.info(f"✅ FastAPI bridge connected: {self.fastapi_url}")
                return True
        except Exception as e:
            logger.warning(f"⚠️  FastAPI not available at {self.fastapi_url}: {e}")
        return False
    
    def semantic_search(self, query: str, top_k: int = 5, filters: dict = None):
        """
        Perform semantic search via FastAPI.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            dict with results or error
        """
        if not self.enabled:
            return {"error": "FastAPI not available", "results": []}
        
        try:
            response = requests.post(
                f"{self.fastapi_url}/query",
                json={
                    "query": query,
                    "top_k": top_k,
                    "filters": filters
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return {"error": str(e), "results": []}
    
    def upload_document(self, file_path: str):
        """
        Upload document to FastAPI for ingestion.
        
        Args:
            file_path: Path to file to upload
            
        Returns:
            dict with upload result
        """
        if not self.enabled:
            return {"error": "FastAPI not available"}
        
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{self.fastapi_url}/upload",
                    files={"file": f},
                    timeout=300
                )
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error(f"Document upload failed: {e}")
            return {"error": str(e)}
    
    def rag_query(self, query: str, top_k: int = 3):
        """
        Get RAG context for LLM prompting.
        
        Args:
            query: Query text
            top_k: Number of context chunks
            
        Returns:
            dict with context and sources
        """
        if not self.enabled:
            return {"error": "FastAPI not available", "context": ""}
        
        try:
            response = requests.post(
                f"{self.fastapi_url}/query/rag",
                json={"query": query, "top_k": top_k},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {"error": str(e), "context": ""}
    
    def get_stats(self):
        """Get FastAPI system statistics."""
        if not self.enabled:
            return {"error": "FastAPI not available"}
        
        try:
            response = requests.get(f"{self.fastapi_url}/health/stats", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}


# Global bridge instance
_bridge = None


def get_bridge() -> FastAPIBridge:
    """Get or create global bridge instance."""
    global _bridge
    if _bridge is None:
        _bridge = FastAPIBridge()
    return _bridge


def requires_fastapi(f):
    """
    Decorator to mark Flask routes that require FastAPI.
    Automatically returns error if FastAPI is not available.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        bridge = get_bridge()
        if not bridge.enabled:
            return jsonify({
                "error": "FastAPI service not available",
                "message": "Please start FastAPI server: python run_fastapi.py"
            }), 503
        return f(*args, **kwargs)
    return decorated_function


# ============= Flask Route Examples =============
# Add these to your Flask app.py to enable FastAPI features

def register_fastapi_routes(app):
    """
    Register FastAPI proxy routes in Flask app.
    Call this function in your Flask app initialization.
    
    Example:
        from fastapi_bridge import register_fastapi_routes
        app = Flask(__name__)
        register_fastapi_routes(app)
    """
    from flask import Blueprint
    
    fastapi_bp = Blueprint('fastapi', __name__, url_prefix='/api/v2')
    bridge = get_bridge()
    
    @fastapi_bp.route('/search', methods=['POST'])
    @requires_fastapi
    def semantic_search_route():
        """Semantic search endpoint."""
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 5)
        filters = data.get('filters')
        
        result = bridge.semantic_search(query, top_k, filters)
        return jsonify(result)
    
    @fastapi_bp.route('/upload', methods=['POST'])
    @requires_fastapi
    def upload_route():
        """Document upload endpoint."""
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Save temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            result = bridge.upload_document(tmp.name)
            os.unlink(tmp.name)
        
        return jsonify(result)
    
    @fastapi_bp.route('/rag', methods=['POST'])
    @requires_fastapi
    def rag_route():
        """RAG context retrieval endpoint."""
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 3)
        
        result = bridge.rag_query(query, top_k)
        return jsonify(result)
    
    @fastapi_bp.route('/stats', methods=['GET'])
    @requires_fastapi
    def stats_route():
        """FastAPI statistics endpoint."""
        stats = bridge.get_stats()
        return jsonify(stats)
    
    @fastapi_bp.route('/status', methods=['GET'])
    def status_route():
        """Check FastAPI availability."""
        return jsonify({
            "fastapi_enabled": bridge.enabled,
            "fastapi_url": bridge.fastapi_url
        })
    
    app.register_blueprint(fastapi_bp)
    logger.info("✅ FastAPI bridge routes registered at /api/v2")


# ============= Usage Examples =============

if __name__ == "__main__":
    # Test the bridge
    bridge = FastAPIBridge()
    
    if bridge.enabled:
        print("✅ FastAPI bridge is operational")
        
        # Test semantic search
        result = bridge.semantic_search("How to write clear documentation?", top_k=3)
        print(f"\nSearch returned {result.get('total_results', 0)} results")
        
        # Get stats
        stats = bridge.get_stats()
        print(f"\nVector store has {stats.get('stats', {}).get('total_chunks', 0)} chunks")
    else:
        print("❌ FastAPI not available. Start with: python run_fastapi.py")

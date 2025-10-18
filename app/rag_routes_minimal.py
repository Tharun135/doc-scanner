"""
Minimal RAG Routes for DocScanner - fallback when full RAG dependencies are not available
"""

import os
import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash

logger = logging.getLogger(__name__)

# Create Blueprint
rag = Blueprint('rag', __name__, url_prefix='/rag')

def init_rag_system():
    """Minimal RAG system initialization - returns False to indicate limited functionality"""
    return False

@rag.route('/dashboard')
def rag_dashboard():
    """RAG Dashboard - shows dependency warning when full RAG system is not available"""
    return render_template('rag_dashboard.html', 
                         rag_available=False,
                         dependencies_missing=True,
                         error_message="RAG system dependencies are not properly configured. Please install: pip install chromadb sentence-transformers scikit-learn")

@rag.route('/api/status')
def rag_status():
    """RAG system status endpoint"""
    return jsonify({
        "status": "dependencies_missing",
        "message": "RAG system dependencies are not available",
        "required_packages": ["chromadb", "sentence-transformers", "scikit-learn"],
        "features_available": {
            "document_upload": False,
            "semantic_search": False,
            "vector_database": False,
            "knowledge_base": False
        }
    })

@rag.route('/api/health')
def rag_health():
    """RAG system health check"""
    return jsonify({
        "vector_db": {"status": "down", "message": "ChromaDB not available"},
        "embedding_service": {"status": "down", "message": "Sentence Transformers not available"},
        "search_performance": {"status": "unknown", "avg_time": None}
    })

@rag.route('/api/upload', methods=['POST'])
def upload_document():
    """Document upload endpoint - returns error when RAG system is not available"""
    return jsonify({
        "success": False,
        "error": "Document upload is not available. RAG system dependencies are missing.",
        "required_packages": ["chromadb", "sentence-transformers", "scikit-learn"]
    }), 503

@rag.route('/api/search', methods=['POST'])
def search_knowledge_base():
    """Knowledge base search endpoint - returns error when RAG system is not available"""
    return jsonify({
        "success": False,
        "error": "Knowledge base search is not available. RAG system dependencies are missing.",
        "results": [],
        "required_packages": ["chromadb", "sentence-transformers", "scikit-learn"]
    }), 503

@rag.route('/api/chunks')
def get_chunks():
    """Get knowledge base chunks - returns empty when RAG system is not available"""
    return jsonify({
        "chunks": [],
        "total_chunks": 0,
        "message": "No chunks available - RAG system dependencies missing"
    })

@rag.route('/api/analytics')
def get_analytics():
    """Get RAG analytics - returns empty analytics when system is not available"""
    return jsonify({
        "total_queries": 0,
        "avg_relevance_score": 0.0,
        "success_rate": 0.0,
        "total_chunks": 0,
        "performance_metrics": {
            "avg_response_time": 0,
            "queries_today": 0
        },
        "message": "Analytics not available - RAG system dependencies missing"
    })
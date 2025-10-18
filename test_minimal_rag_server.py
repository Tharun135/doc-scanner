#!/usr/bin/env python3
"""
Minimal Flask app to test RAG upload functionality without model downloads
"""

import os
import sys
from flask import Flask, render_template, request, jsonify

# Set offline mode to prevent model downloads
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'

app = Flask(__name__)

# Mock RAG availability
RAG_AVAILABLE = True
supported_formats = ['pdf', 'docx', 'doc', 'md', 'html', 'txt']

@app.route('/')
def index():
    return '<h1>DocScanner RAG Test</h1><a href="/rag/dashboard">RAG Dashboard</a>'

@app.route('/rag/dashboard')
def rag_dashboard():
    """Mock RAG dashboard"""
    stats = {
        'total_chunks': 0,
        'total_queries': 0,
        'avg_relevance': 0.0,
        'success_rate': 0.0
    }
    
    return render_template('rag/dashboard.html', 
                         stats=stats, 
                         supported_formats=supported_formats,
                         rag_available=RAG_AVAILABLE)

@app.route('/rag/upload_knowledge', methods=['GET', 'POST'])
def upload_knowledge():
    """Mock upload knowledge page"""
    if request.method == 'GET':
        return render_template('rag/upload_knowledge.html', 
                             supported_formats=supported_formats,
                             rag_available=RAG_AVAILABLE)
    
    # Handle POST (file upload)
    if 'files[]' not in request.files:
        return jsonify({"error": "No files provided"}), 400
    
    files = request.files.getlist('files[]')
    processed_files = []
    
    for file in files:
        if file.filename:
            processed_files.append({
                'filename': file.filename,
                'size': len(file.read()),
                'status': 'processed'
            })
    
    return jsonify({
        "message": f"Successfully uploaded {len(processed_files)} files",
        "files": processed_files
    })

@app.route('/rag/stats')
def rag_stats():
    """Mock RAG stats endpoint"""
    return jsonify({
        'total_chunks': 0,
        'total_queries': 0,
        'avg_relevance': 0.0,
        'success_rate': 0.0
    })

if __name__ == '__main__':
    # Set template folder to the actual location
    app.template_folder = 'app/templates'
    app.static_folder = 'app/static'
    
    print("🚀 Starting minimal RAG test server...")
    print("✅ RAG_AVAILABLE = True")
    print("📁 Using templates from:", app.template_folder)
    print("🌐 Open: http://127.0.0.1:5001/rag/upload_knowledge")
    
    app.run(host='127.0.0.1', port=5001, debug=True)
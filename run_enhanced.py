#!/usr/bin/env python3
"""
Enhanced Doc-Scanner with AI Rewriter Integration
Starts the doc-scanner application with integrated AI rewriting capabilities
"""

import os
import sys
import logging
from app import create_app

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the enhanced doc-scanner application."""
    
    logger.info("🚀 Starting Doc-Scanner with AI Rewriter Integration...")
    
    # Create the Flask app with rewriter integration
    try:
        app, socketio = create_app()
        logger.info("✅ Application created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create application: {e}")
        sys.exit(1)
    
    # Check if Ollama is available (optional)
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [model.get("name", "unknown") for model in models]
            logger.info(f"🤖 Ollama available with models: {', '.join(model_names)}")
        else:
            logger.warning("⚠️ Ollama service not responding (rewriter features may be limited)")
    except (requests.RequestException, ImportError):
        logger.warning("⚠️ Ollama not available (rewriter features will be disabled)")
    
    # Print available endpoints
    logger.info("\n📝 Available Endpoints:")
    logger.info("   Main Application: http://localhost:5000")
    logger.info("   AI Rewriter: http://localhost:5000/api/rewriter/status")
    logger.info("   Rewrite Text: POST http://localhost:5000/rewrite-suggestion")
    logger.info("   Readability: POST http://localhost:5000/readability-analysis")
    logger.info("   Full Rewrite: POST http://localhost:5000/document-rewrite")
    
    logger.info("\n📖 Documentation:")
    logger.info("   Integration Guide: REWRITER_INTEGRATION_GUIDE.md")
    logger.info("   Quick Summary: INTEGRATION_SUMMARY.md")
    
    logger.info("\n🧪 Test Integration:")
    logger.info("   Run: python test_rewriter_integration.py")
    
    # Start the application
    try:
        logger.info("\n🌟 Starting enhanced doc-scanner on http://localhost:5000")
        logger.info("   Press Ctrl+C to stop")
        
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=False,  # Set to True for development
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down doc-scanner...")
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

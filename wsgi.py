"""
WSGI Entry Point for DocScanner Application
Production-ready with Gunicorn support
"""
import os
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app

# Create Flask application instance
application = create_app()

# For development/testing only
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    
    application.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )

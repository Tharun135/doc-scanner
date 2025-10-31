#!/usr/bin/env python3
"""
Ultra simple stable server for DocScanner AI
"""

import os
import sys

def run_ultra_simple_server():
    print("Starting DocScanner AI...")
    
    # Set environment
    os.environ['FLASK_ENV'] = 'production' 
    os.environ['FLASK_DEBUG'] = '0'
    os.environ['STABLE_MODE'] = '1'
    
    try:
        from app import create_app
        app = create_app()
        socketio = app.socketio
        
        print("Application initialized successfully")
        print("Server starting on http://localhost:5000")
        print("AI suggestions are now available!")
        
        # Simple Flask server
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_ultra_simple_server()
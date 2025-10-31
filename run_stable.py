#!/usr/bin/env python3
"""
Stable server runner for DocScanner AI with proper production configuration
Eliminates file watching issues and restart loops that cause AI suggestion failures
"""

import os
import sys
from werkzeug.serving import WSGIRequestHandler

def run_stable_server():
    """Run the server with stable configuration"""
    print("🚀 Starting DocScanner AI with stable configuration...")
    
    # Set production-like environment variables to prevent restart loops
    os.environ['FLASK_ENV'] = 'production'
    os.environ['FLASK_DEBUG'] = '0'
    os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    
    # Disable file watching that causes crashes
    os.environ['WERKZEUG_USE_RELOADER'] = '0'
    
    # Import after setting environment variables
    from app import create_app
    
    try:
        print("📋 Initializing application...")
        app = create_app()
        socketio = app.socketio
        
        # Configure for stability
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        
        print("✅ Application initialized successfully")
        print("🌐 Starting server on http://localhost:5000")
        print("🧠 AI suggestions will be available once server is ready")
        print("⚠️  Use Ctrl+C to stop the server")
        print("-" * 50)
        
        # Custom request handler to reduce verbosity
        class QuietWSGIRequestHandler(WSGIRequestHandler):
            def log_request(self, code='-', size='-'):
                # Only log non-200 responses and AI suggestion requests
                if code != 200 or '/ai_suggestion' in self.path:
                    super().log_request(code, size)
        
        # Run with stable configuration - use app.run for more stability
        if socketio:
            print("🌐 Using SocketIO server...")
            socketio.run(
                app,
                host='0.0.0.0',
                port=5000,
                debug=False,
                use_reloader=False,  # Prevent file watching issues
                log_output=False  # Reduce noise
            )
        else:
            print("🌐 Using Flask server...")
            app.run(
                host='0.0.0.0',
                port=5000,
                debug=False,
                use_reloader=False,
                threaded=True
            )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    run_stable_server()
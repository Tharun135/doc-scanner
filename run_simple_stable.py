#!/usr/bin/env python3
"""
Simple stable server for DocScanner AI - bypasses SocketIO issues
"""

import os
import sys

def run_simple_stable_server():
    """Run the server with simple Flask configuration"""
    print("🚀 Starting DocScanner AI (Simple Stable Mode)...")
    
    # Set environment to prevent file watching
    os.environ['FLASK_ENV'] = 'production' 
    os.environ['FLASK_DEBUG'] = '0'
    os.environ['STABLE_MODE'] = '1'
    
    try:
        print("📋 Initializing application...")
        from app import create_app
        
        app, socketio = create_app()
        
        print("✅ Application initialized successfully")
        print("🌐 Starting server on http://localhost:5000")
        print("🧠 AI suggestions ready!")
        print("⚠️  Use Ctrl+C to stop the server")
        print("-" * 50)
        
        # Use simple Flask server without SocketIO to avoid issues
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
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_simple_stable_server()
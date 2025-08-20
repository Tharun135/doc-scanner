#!/usr/bin/env python3
"""
Simple test to verify WebSocket implementation is working.
"""

try:
    from app import create_app
    print("✅ App import successful")
    
    app, socketio = create_app()
    print("✅ App creation successful")
    print("✅ SocketIO instance created")
    
    print("\n🚀 Starting server...")
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

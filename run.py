import os
from app import create_app

app = create_app()
socketio = app.socketio

if __name__ == '__main__':
    # Check for stable mode environment variable
    stable_mode = os.environ.get('STABLE_MODE', '0') == '1'
    debug_mode = not stable_mode and os.environ.get('FLASK_DEBUG', '1') == '1'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🚀 Starting DocScanner AI (Debug: {debug_mode}, Stable: {stable_mode}, Port: {port})")
    
    # Use socketio.run if available, otherwise use app.run
    if socketio:
        socketio.run(
            app, 
            debug=debug_mode, 
            host='0.0.0.0', 
            port=port,
            use_reloader=not stable_mode  # Disable reloader in stable mode
        )
    else:
        print("⚠️ Running without SocketIO support")
        app.run(debug=debug_mode, host='0.0.0.0', port=port, use_reloader=not stable_mode)

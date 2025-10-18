import os
from app import create_app

app, socketio = create_app()

if __name__ == '__main__':
    # Force disable debug mode to prevent file watching and constant restarts
    debug_mode = False
    
    # Use socketio.run if available, otherwise use app.run
    if socketio:
        socketio.run(app, debug=debug_mode, host='0.0.0.0', port=5000)
    else:
        print("⚠️ Running without SocketIO support")
        app.run(debug=debug_mode, host='0.0.0.0', port=5000)

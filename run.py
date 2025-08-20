from app import create_app

app, socketio = create_app()

if __name__ == '__main__':
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

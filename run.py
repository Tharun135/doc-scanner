from app import create_app

app, socketio = create_app()

if __name__ == '__main__':
    # Use socketio.run if available, otherwise use app.run
    if socketio:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    else:
        print("⚠️ Running without SocketIO support")
        app.run(debug=True, host='0.0.0.0', port=5000)

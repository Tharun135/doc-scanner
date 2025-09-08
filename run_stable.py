from app import create_app

app, socketio = create_app()

if __name__ == '__main__':
    # Run without debug mode for stability
    socketio.run(app, debug=False, host='0.0.0.0', port=5000)

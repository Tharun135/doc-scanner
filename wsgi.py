import os
from app import create_app

# Create the Flask application instance
app, socketio = create_app()

if __name__ == "__main__":
    # For local development
    if socketio:
        socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
    else:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
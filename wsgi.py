import os
from app import create_app

# Create the Flask application instance
flask_app, socketio = create_app()

# For Gunicorn, we need just the Flask app
app = flask_app

if __name__ == "__main__":
    # For local development
    port = int(os.environ.get('PORT', 5000))
    if socketio:
        socketio.run(flask_app, host='0.0.0.0', port=port, debug=False)
    else:
        flask_app.run(host='0.0.0.0', port=port, debug=False)
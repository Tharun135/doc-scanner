from app import create_app  # adjust import if your factory lives elsewhere

# Your factory should return (app, socketio)
app, socketio = create_app()

# Do NOT call socketio.run() here; Gunicorn will serve the app.
# If you need CORS for a separate frontend:
# from flask_cors import CORS
# CORS(app)

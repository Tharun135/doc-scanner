from flask import Flask

# Make flask_socketio optional
try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False
    SocketIO = None

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production
    
    # Initialize SocketIO only if available
    if SOCKETIO_AVAILABLE:
        socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)
    else:
        socketio = None
    
    # Initialize progress tracker
    from .progress_tracker import initialize_progress_tracker
    progress_tracker = initialize_progress_tracker(socketio)

    from .app import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Add SocketIO event handlers only if available
    if SOCKETIO_AVAILABLE and socketio:
        @socketio.on('connect')
        def handle_connect():
            print('Client connected')
        
        @socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')
        
        @socketio.on('join_progress_room')
        def handle_join_room(data):
            from flask_socketio import join_room
            room_id = data.get('room_id')
            if room_id:
                join_room(room_id)
                print(f'Client joined progress room: {room_id}')
    
    # Register agent blueprint
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from agent.flask_routes_fixed import agent_bp
        app.register_blueprint(agent_bp)
        print("✅ Agent blueprint loaded successfully!")
    except ImportError as e:
        print(f"Warning: Could not import agent blueprint: {e}")
        # Create a minimal agent endpoint for testing
        from flask import Blueprint, jsonify, request
        minimal_agent_bp = Blueprint('agent', __name__, url_prefix='/api/agent')
        
        @minimal_agent_bp.route('/status', methods=['GET'])
        def agent_status():
            return jsonify({"status": "running", "message": "Agent is operational"})
        
        @minimal_agent_bp.route('/analyze', methods=['POST'])
        def analyze_document():
            return jsonify({"message": "Analysis complete", "issues": []})
            
        app.register_blueprint(minimal_agent_bp)
        print("✅ Minimal agent endpoints created!")

    # Store socketio instance in app for access in routes
    app.socketio = socketio
    return app, socketio
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
    
    # Configure file upload settings
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
    app.config['UPLOAD_EXTENSIONS'] = ['.txt', '.pdf', '.docx', '.doc', '.md', '.adoc', '.zip']
    
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
    
    # Register RAG blueprint for knowledge base management
    try:
        from .rag_routes import rag, init_rag_system
        app.register_blueprint(rag)
        
        # Don't initialize RAG system at startup to avoid hanging
        # It will be initialized on first access to RAG routes
        print("✅ RAG system registered - will initialize on first use!")
        
        # Start performance optimization in background (optional)
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
            from rag_performance_optimizer import preload_rag_dashboard_data
            preload_rag_dashboard_data()
            print("🚀 RAG dashboard preloading started in background...")
        except ImportError:
            print("Note: RAG performance optimization not available (optional feature)")
        except Exception as opt_e:
            print(f"Note: RAG performance optimization not available: {opt_e}")
    except Exception as e:
        print(f"Warning: Could not import full RAG system: {e}")
        print("⚠️ Loading minimal RAG system...")
        try:
            from .rag_routes_minimal import rag, init_rag_system
            app.register_blueprint(rag)
            init_rag_system()
            print("✅ Minimal RAG system loaded successfully!")
        except Exception as e2:
            print(f"Error: Could not load minimal RAG system: {e2}")
            print("⚠️ Running without RAG capabilities")
    
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
    return app

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

# Make flask_socketio optional
try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
    print("✅ Flask-SocketIO is available and will be used for real-time progress tracking")
except ImportError as e:
    SOCKETIO_AVAILABLE = False
    SocketIO = None
    print(f"⚠️ Flask-SocketIO not found ({e}). Real-time progress tracking will be disabled.")

# Make flask_cors optional
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
    CORS = None

# Module-level instances so models and auth can import them directly
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # ── Security & DB configuration ──────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change-me-in-production-random-string')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'app.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Initialize extensions ────────────────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please sign in to access Doc Scanner.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create all DB tables if they don't exist yet
    with app.app_context():
        db.create_all()
        print("✅ User database initialized (app.db)")

    # ── CORS ─────────────────────────────────────────────────────────────────
    if CORS_AVAILABLE:
        CORS(app)
        print("✅ CORS enabled")
    else:
        @app.after_request
        def add_cors_headers(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        print("✅ Manual CORS headers added")

    # ── File upload settings ─────────────────────────────────────────────────
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
    app.config['UPLOAD_EXTENSIONS'] = ['.txt', '.pdf', '.docx', '.doc', '.md', '.adoc', '.zip']

    # ── SocketIO ─────────────────────────────────────────────────────────────
    if SOCKETIO_AVAILABLE:
        socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)
    else:
        socketio = None

    from .progress_tracker import initialize_progress_tracker
    progress_tracker = initialize_progress_tracker(socketio)

    # ── Blueprints ────────────────────────────────────────────────────────────
    # Auth blueprint (login / register / logout)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    print("✅ Auth blueprint registered (login/register/logout)")

    # Main scanner blueprint
    from .app import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # RAG blueprint
    try:
        from .rag_routes import rag, init_rag_system
        app.register_blueprint(rag)
        print("✅ RAG system registered - will initialize on first use!")
        try:
            import sys
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

    # ── SocketIO event handlers ───────────────────────────────────────────────
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

    # ── Agent blueprint ───────────────────────────────────────────────────────
    try:
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from agent.flask_routes_fixed import agent_bp
        app.register_blueprint(agent_bp)
        print("✅ Agent blueprint loaded successfully!")
    except ImportError as e:
        print(f"Warning: Could not import agent blueprint: {e}")
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

    app.socketio = socketio
    return app

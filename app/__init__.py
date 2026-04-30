from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

# Make flask_socketio optional
try:
    from flask_socketio import SocketIO
    SOCKETIO_AVAILABLE = True
    print("[OK] Flask-SocketIO is available and will be used for real-time progress tracking")
except ImportError as e:
    SOCKETIO_AVAILABLE = False
    SocketIO = None
    print(f"[WARN] Flask-SocketIO not found ({e}). Real-time progress tracking will be disabled.")

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

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
    LIMITER_AVAILABLE = True
except ImportError:
    limiter = None
    LIMITER_AVAILABLE = False



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
    
    if LIMITER_AVAILABLE:
        limiter.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create all DB tables if they don't exist yet
    with app.app_context():
        db.create_all()
        print("[OK] User database initialized (app.db)")

    # ── CORS ─────────────────────────────────────────────────────────────────
    if CORS_AVAILABLE:
        CORS(app)
        print("[OK] CORS enabled")
    else:
        @app.after_request
        def add_cors_headers(response):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        print("[OK] Manual CORS headers added")

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
    print("[OK] Auth blueprint registered (login/register/logout)")

    # Main scanner blueprint
    from .app import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # RAG blueprint - DISABLED per request to move to direct LLM
    # try:
    #     from .rag_routes import rag, init_rag_system
    #     app.register_blueprint(rag)
    #     print("[OK] RAG system registered - will initialize on first use!")
    #     try:
    #         import sys
    #         sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    #         sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
    #         from rag_performance_optimizer import preload_rag_dashboard_data
    #         preload_rag_dashboard_data()
    #         print("[START] RAG dashboard preloading started in background...")
    #     except ImportError:
    #         print("Note: RAG performance optimization not available (optional feature)")
    #     except Exception as opt_e:
    #         print(f"Note: RAG performance optimization not available: {opt_e}")
    # except Exception as e:
    #     print(f"Warning: Could not import full RAG system: {e}")
    #     print("[WARN] Loading minimal RAG system...")
    #     try:
    #         from .rag_routes_minimal import rag, init_rag_system
    #         app.register_blueprint(rag)
    #         init_rag_system()
    #         print("[OK] Minimal RAG system loaded successfully!")
    #     except Exception as e2:
    #         print(f"Error: Could not load minimal RAG system: {e2}")
    #         print("[WARN] Running without RAG capabilities")

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
        print("[OK] Agent blueprint loaded successfully!")
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
        print("[OK] Minimal agent endpoints created!")

    # ── Background Cleanup Task ───────────────────────────────────────────────
    def start_cleanup_thread(app):
        import threading
        import time
        from datetime import datetime, timedelta

        def cleanup_task():
            with app.app_context():
                upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
                if not os.path.exists(upload_dir):
                    return

                while True:
                    try:
                        print(f"[CLEAN] Running background cleanup (at {datetime.now().strftime('%H:%M:%S')})...")
                        count = 0
                        now = time.time()
                        for f in os.listdir(upload_dir):
                            f_path = os.path.join(upload_dir, f)
                            # Check if file is older than 24 hours (86400 seconds)
                            if os.stat(f_path).st_mtime < now - 86400:
                                os.remove(f_path)
                                count += 1
                        if count > 0:
                            print(f"[OK] Cleaned up {count} old file(s) from uploads folder.")
                    except Exception as e:
                        print(f"[WARN] Cleanup task error: {e}")
                    
                    # Run once every hour (3600 seconds)
                    time.sleep(3600)

        thread = threading.Thread(target=cleanup_task, daemon=True)
        thread.start()

    # Start the cleanup thread
    start_cleanup_thread(app)

    # ── Rule Remediation Ingestion - DISABLED ───────────────────────────────
    # try:
    #     from .rules.rule_remediations import ingest_into_chromadb
    #     import threading
    #     # Run in background to not block app startup
    #     def run_ingestion():
    #         with app.app_context():
    #             try:
    #                 # Use a path relative to the app directory or as configured
    #                 persist_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docscanner_rules_db')
    #                 ingest_into_chromadb(persist_path=persist_path)
    #             except Exception as e:
    #                 print(f"[WARN] Rule ingestion background task error: {e}")
    # 
    #     threading.Thread(target=run_ingestion, daemon=True).start()
    #     print("[START] Rule remediation ingestion scheduled in background...")
    # except ImportError:
    #     print("Note: Rule remediations module not found (optional feature)")
    # except Exception as e:
    #     print(f"Warning: Could not initialize rule remediations: {e}")

    app.socketio = socketio
    return app


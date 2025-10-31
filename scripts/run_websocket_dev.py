#!/usr/bin/env python3
"""
Simplified run script for WebSocket development that bypasses heavy dependencies.
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import uuid
import time
import threading
import os

def create_simple_app():
    """Create a simplified app for WebSocket testing."""
    app = Flask(__name__, template_folder='app/templates')
    app.config['SECRET_KEY'] = 'websocket-dev-key'
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)
    
    # Simple progress tracker (same as the progress_tracker.py concept)
    class SimpleProgressTracker:
        def __init__(self, socketio):
            self.socketio = socketio
            self.active_sessions = {}
            
        def start_session(self, room_id):
            self.active_sessions[room_id] = {'start_time': time.time()}
            
        def update_stage(self, room_id, stage_index, message):
            if room_id in self.active_sessions:
                stages = [
                    {'percentage': 10, 'name': 'Upload', 'icon': 'fas fa-upload'},
                    {'percentage': 30, 'name': 'Parse', 'icon': 'fas fa-file-alt'},
                    {'percentage': 50, 'name': 'Extract', 'icon': 'fas fa-cut'},
                    {'percentage': 80, 'name': 'Analyze', 'icon': 'fas fa-search'},
                    {'percentage': 100, 'name': 'Report', 'icon': 'fas fa-chart-line'}
                ]
                
                if stage_index < len(stages):
                    stage = stages[stage_index]
                    percentage = stage['percentage']
                    stage_name = stage['name']
                else:
                    percentage = 100
                    stage_name = 'Complete'
                
                elapsed = time.time() - self.active_sessions[room_id]['start_time']
                
                # Calculate ETA
                eta_seconds = 0
                if percentage > 0 and percentage < 100:
                    estimated_total = (elapsed / percentage) * 100
                    eta_seconds = max(0, estimated_total - elapsed)
                
                self.socketio.emit('progress_update', {
                    'percentage': percentage,
                    'message': message,
                    'stage_name': stage_name,
                    'stage_index': stage_index,
                    'elapsed_time': round(elapsed, 2),
                    'eta_seconds': round(eta_seconds, 1) if eta_seconds > 0 else 0,
                    'completed': percentage >= 100
                }, room=room_id)
                
                print(f"📊 Stage {stage_index}: {stage_name} ({percentage}%) - {message}")
                
        def complete_session(self, room_id, success=True, final_message="Processing complete!"):
            if room_id in self.active_sessions:
                elapsed = time.time() - self.active_sessions[room_id]['start_time']
                self.socketio.emit('progress_update', {
                    'percentage': 100,
                    'message': final_message,
                    'stage_name': 'Complete',
                    'elapsed_time': round(elapsed, 2),
                    'completed': True,
                    'success': success
                }, room=room_id)
                del self.active_sessions[room_id]
    
    progress_tracker = SimpleProgressTracker(socketio)
    
    # WebSocket event handlers
    @socketio.on('connect')
    def handle_connect():
        print('✅ Client connected')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('❌ Client disconnected')
    
    @socketio.on('join_progress_room')
    def handle_join_room(data):
        from flask_socketio import join_room
        room_id = data.get('room_id')
        if room_id:
            join_room(room_id)
            print(f'📱 Client joined progress room: {room_id}')
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/start_upload', methods=['POST'])
    def start_upload():
        room_id = str(uuid.uuid4())
        progress_tracker.start_session(room_id)
        print(f'🚀 Started upload session: {room_id}')
        return jsonify({"room_id": room_id})
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        room_id = request.form.get('room_id')
        
        if not file.filename:
            return jsonify({"error": "No selected file"}), 400

        print(f"📄 Processing file: {file.filename} (Room: {room_id})")

        def simulate_real_processing():
            try:
                # Stage 1: Upload (10%)
                progress_tracker.update_stage(room_id, 0, f"Uploading {file.filename}...")
                time.sleep(0.5)
                
                # Stage 2: Parse (30%)
                progress_tracker.update_stage(room_id, 1, f"Parsing {file.filename.split('.')[-1].upper()} content...")
                time.sleep(1.0)
                
                # Stage 3: Extract (50%)
                progress_tracker.update_stage(room_id, 2, "Identifying sentence boundaries...")
                time.sleep(0.8)
                
                # Stage 4: Analyze (80%) - This would be the longest in real app
                progress_tracker.update_stage(room_id, 3, "Applying grammar and style rules...")
                time.sleep(2.0)  # Simulate heavy processing
                
                # Stage 5: Report (100%)
                progress_tracker.update_stage(room_id, 4, "Compiling insights and metrics...")
                time.sleep(0.3)
                
                # Complete
                progress_tracker.complete_session(room_id, success=True, 
                    final_message="Analysis complete! Document processed successfully.")
                
            except Exception as e:
                progress_tracker.complete_session(room_id, success=False, 
                    final_message=f"Error: {str(e)}")

        # Run processing in background thread to not block the response
        thread = threading.Thread(target=simulate_real_processing)
        thread.start()
        
        # Return immediately while processing continues in background
        return jsonify({
            "status": "processing",
            "room_id": room_id,
            "message": "Document processing started"
        })
    
    return app, socketio

if __name__ == '__main__':
    print("🔧 Starting Development WebSocket Server...")
    print("📋 Features: Real-time progress tracking with WebSocket")
    print("🌐 URL: http://127.0.0.1:5000")
    print("⚠️  Note: This is a simplified version for WebSocket testing")
    
    app, socketio = create_simple_app()
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)

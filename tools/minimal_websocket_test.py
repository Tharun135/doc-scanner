#!/usr/bin/env python3
"""
Minimal WebSocket test without heavy dependencies.
"""

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import uuid
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-websocket-key'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

# Simple progress tracker
class SimpleProgressTracker:
    def __init__(self, socketio):
        self.socketio = socketio
        self.active_sessions = {}
        
    def start_session(self, room_id):
        self.active_sessions[room_id] = {'start_time': time.time()}
        self.socketio.emit('progress_update', {
            'percentage': 0,
            'message': 'Starting document processing...',
            'stage_name': 'Initializing'
        }, room=room_id)
        
    def update_progress(self, room_id, percentage, message, stage_name):
        if room_id in self.active_sessions:
            elapsed = time.time() - self.active_sessions[room_id]['start_time']
            self.socketio.emit('progress_update', {
                'percentage': percentage,
                'message': message,
                'stage_name': stage_name,
                'elapsed_time': round(elapsed, 2),
                'completed': percentage >= 100
            }, room=room_id)
            
    def complete_session(self, room_id):
        if room_id in self.active_sessions:
            elapsed = time.time() - self.active_sessions[room_id]['start_time']
            self.socketio.emit('progress_update', {
                'percentage': 100,
                'message': 'Processing completed!',
                'stage_name': 'Complete',
                'elapsed_time': round(elapsed, 2),
                'completed': True
            }, room=room_id)
            del self.active_sessions[room_id]

progress_tracker = SimpleProgressTracker(socketio)

# WebSocket event handlers
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

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Progress Test</title>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
</head>
<body>
    <h1>WebSocket Progress Test</h1>
    <div id="progress">
        <div>Progress: <span id="percentage">0%</span></div>
        <div>Stage: <span id="stage">Waiting</span></div>
        <div>Message: <span id="message">Ready to test</span></div>
    </div>
    <button onclick="startTest()">Start Test Upload</button>
    
    <script>
        const socket = io();
        let currentRoomId = null;

        socket.on('connect', () => {
            console.log('Connected to WebSocket server');
        });

        socket.on('progress_update', (data) => {
            document.getElementById('percentage').textContent = data.percentage + '%';
            document.getElementById('stage').textContent = data.stage_name || 'Processing';
            document.getElementById('message').textContent = data.message || '';
            
            if (data.completed) {
                setTimeout(() => alert('Test completed successfully!'), 500);
            }
        });

        async function startTest() {
            // Get room ID
            const roomResponse = await fetch('/start_upload', { method: 'POST' });
            const roomData = await roomResponse.json();
            currentRoomId = roomData.room_id;
            
            // Join room
            socket.emit('join_progress_room', { room_id: currentRoomId });
            
            // Start test upload
            const testResponse = await fetch('/test_upload', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ room_id: currentRoomId })
            });
        }
    </script>
</body>
</html>
    '''

@app.route('/start_upload', methods=['POST'])
def start_upload():
    room_id = str(uuid.uuid4())
    return jsonify({"room_id": room_id})

@app.route('/test_upload', methods=['POST'])
def test_upload():
    data = request.get_json()
    room_id = data.get('room_id')
    
    def simulate_processing():
        stages = [
            (10, "Uploading Document", "Receiving and validating document..."),
            (30, "Parsing Content", "Extracting text content..."),
            (50, "Breaking into Sentences", "Identifying sentence boundaries..."),
            (80, "Analyzing with Rules", "Applying grammar and style rules..."),
            (100, "Generating Report", "Compiling insights and metrics...")
        ]
        
        progress_tracker.start_session(room_id)
        
        for percentage, stage_name, message in stages:
            time.sleep(0.5)  # Simulate processing time
            progress_tracker.update_progress(room_id, percentage, message, stage_name)
        
        progress_tracker.complete_session(room_id)
    
    # Run processing in background thread
    thread = threading.Thread(target=simulate_processing)
    thread.start()
    
    return jsonify({"status": "processing started"})

if __name__ == '__main__':
    print("🚀 Starting WebSocket test server...")
    print("📱 Open http://127.0.0.1:5000 to test")
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)

"""
Real-time progress tracking for document processing using WebSocket connections.
"""

import time
import uuid
from typing import Dict, Any, Optional
from flask_socketio import emit
import logging

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Manages progress tracking for document processing tasks."""
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.active_sessions = {}  # session_id -> progress_info
        
    def start_session(self, room_id: str, total_stages: int = 5) -> str:
        """Start a new progress tracking session."""
        session_info = {
            'room_id': room_id,
            'total_stages': total_stages,
            'current_stage': 0,
            'start_time': time.time(),
            'stages': [
                {'name': 'Uploading Document', 'description': 'Receiving and validating your document...', 'percentage': 10},
                {'name': 'Parsing Content', 'description': 'Extracting text from PDF, DOCX, or Markdown...', 'percentage': 30},
                {'name': 'Breaking into Sentences', 'description': 'Identifying sentence boundaries and structure...', 'percentage': 50},
                {'name': 'Analyzing with Rules', 'description': 'Applying grammar, style, and readability rules...', 'percentage': 80},
                {'name': 'Generating Report', 'description': 'Compiling insights and quality metrics...', 'percentage': 100}
            ]
        }
        
        self.active_sessions[room_id] = session_info
        logger.info(f"Started progress session: {room_id}")
        
        # Send initial progress update
        self._emit_progress(room_id, 0, "Starting document processing...")
        return room_id
    
    def update_stage(self, room_id: str, stage_index: int, message: Optional[str] = None):
        """Update the current processing stage."""
        if room_id not in self.active_sessions:
            logger.warning(f"Progress session not found: {room_id}")
            return
            
        session = self.active_sessions[room_id]
        
        if stage_index >= len(session['stages']):
            logger.warning(f"Invalid stage index {stage_index} for session {room_id}")
            return
            
        session['current_stage'] = stage_index
        stage = session['stages'][stage_index]
        
        # Use stage description if no custom message provided
        if message is None:
            message = stage['description']
            
        self._emit_progress(room_id, stage['percentage'], message, stage['name'])
        logger.info(f"Session {room_id}: Stage {stage_index} - {stage['name']}")
    
    def update_progress(self, room_id: str, percentage: int, message: str, stage_name: Optional[str] = None):
        """Update progress with custom percentage and message."""
        if room_id not in self.active_sessions:
            logger.warning(f"Progress session not found: {room_id}")
            return
            
        self._emit_progress(room_id, percentage, message, stage_name)
    
    def add_substep(self, room_id: str, substep_message: str):
        """Add a substep message within the current stage."""
        if room_id not in self.active_sessions:
            return
            
        session = self.active_sessions[room_id]
        current_stage_idx = session['current_stage']
        
        if current_stage_idx < len(session['stages']):
            stage = session['stages'][current_stage_idx]
            self._emit_progress(room_id, stage['percentage'], substep_message, stage['name'], is_substep=True)
    
    def complete_session(self, room_id: str, success: bool = True, final_message: str = "Processing completed!"):
        """Complete the progress tracking session."""
        if room_id not in self.active_sessions:
            return
            
        session = self.active_sessions[room_id]
        elapsed_time = time.time() - session['start_time']
        
        # Send completion event
        completion_data = {
            'percentage': 100,
            'message': final_message,
            'stage_name': 'Complete',
            'success': success,
            'elapsed_time': round(elapsed_time, 2),
            'completed': True
        }
        
        if self.socketio:
            self.socketio.emit('progress_update', completion_data, room=room_id)
            logger.info(f"Completed session {room_id} in {elapsed_time:.2f}s")
        
        # Clean up session
        del self.active_sessions[room_id]
    
    def fail_session(self, room_id: str, error_message: str):
        """Mark session as failed with error message."""
        self.complete_session(room_id, success=False, final_message=f"Error: {error_message}")
    
    def _emit_progress(self, room_id: str, percentage: int, message: str, stage_name: Optional[str] = None, is_substep: bool = False):
        """Emit progress update to WebSocket clients."""
        if not self.socketio:
            return
            
        session = self.active_sessions.get(room_id)
        if not session:
            return
            
        elapsed_time = time.time() - session['start_time']
        
        # Calculate ETA based on current progress
        eta_seconds = 0
        if percentage > 0:
            estimated_total = (elapsed_time / percentage) * 100
            eta_seconds = max(0, estimated_total - elapsed_time)
        
        progress_data = {
            'percentage': percentage,
            'message': message,
            'stage_name': stage_name or 'Processing',
            'elapsed_time': round(elapsed_time, 2),
            'eta_seconds': round(eta_seconds, 1) if eta_seconds > 0 else 0,
            'is_substep': is_substep,
            'completed': False
        }
        
        self.socketio.emit('progress_update', progress_data, room=room_id)

# Global progress tracker instance
progress_tracker = None

def initialize_progress_tracker(socketio):
    """Initialize the global progress tracker with SocketIO instance."""
    global progress_tracker
    progress_tracker = ProgressTracker(socketio)
    return progress_tracker

def get_progress_tracker() -> Optional[ProgressTracker]:
    """Get the global progress tracker instance."""
    return progress_tracker

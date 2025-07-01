"""
Performance monitoring and feedback learning system for AI suggestions.
Tracks effectiveness and continuously improves suggestion quality.
"""

import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import sqlite3
import os

logger = logging.getLogger(__name__)

@dataclass
class SuggestionMetrics:
    """Metrics for tracking suggestion performance."""
    suggestion_id: str
    feedback_text: str
    sentence_context: str
    document_type: str
    suggestion_method: str
    response_time: float
    timestamp: datetime
    user_rating: Optional[int] = None  # 1-5 scale
    user_feedback: Optional[str] = None
    was_helpful: Optional[bool] = None
    was_implemented: Optional[bool] = None

class PerformanceMonitor:
    """Monitors and tracks AI suggestion performance."""
    
    def __init__(self, db_path: str = "suggestion_metrics.db"):
        self.db_path = db_path
        self.init_database()
        self.recent_metrics = deque(maxlen=1000)  # Keep last 1000 in memory
        
    def init_database(self):
        """Initialize SQLite database for persistence."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suggestion_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suggestion_id TEXT UNIQUE,
                    feedback_text TEXT,
                    sentence_context TEXT,
                    document_type TEXT,
                    suggestion_method TEXT,
                    response_time REAL,
                    timestamp TEXT,
                    user_rating INTEGER,
                    user_feedback TEXT,
                    was_helpful INTEGER,
                    was_implemented INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON suggestion_metrics(timestamp)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_method ON suggestion_metrics(suggestion_method)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_document_type ON suggestion_metrics(document_type)
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def record_suggestion(self, metrics: SuggestionMetrics):
        """Record a new suggestion and its metrics."""
        try:
            # Add to memory cache
            self.recent_metrics.append(metrics)
            
            # Persist to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO suggestion_metrics 
                (suggestion_id, feedback_text, sentence_context, document_type, 
                 suggestion_method, response_time, timestamp, user_rating, 
                 user_feedback, was_helpful, was_implemented)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.suggestion_id,
                metrics.feedback_text,
                metrics.sentence_context,
                metrics.document_type,
                metrics.suggestion_method,
                metrics.response_time,
                metrics.timestamp.isoformat(),
                metrics.user_rating,
                metrics.user_feedback,
                metrics.was_helpful,
                metrics.was_implemented
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error recording suggestion metrics: {e}")
    
    def update_user_feedback(self, suggestion_id: str, rating: int = None, 
                           feedback: str = None, was_helpful: bool = None,
                           was_implemented: bool = None):
        """Update user feedback for a suggestion."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            updates = []
            values = []
            
            if rating is not None:
                updates.append("user_rating = ?")
                values.append(rating)
            
            if feedback is not None:
                updates.append("user_feedback = ?")
                values.append(feedback)
            
            if was_helpful is not None:
                updates.append("was_helpful = ?")
                values.append(1 if was_helpful else 0)
            
            if was_implemented is not None:
                updates.append("was_implemented = ?")
                values.append(1 if was_implemented else 0)
            
            if updates:
                values.append(suggestion_id)
                query = f"UPDATE suggestion_metrics SET {', '.join(updates)} WHERE suggestion_id = ?"
                cursor.execute(query, values)
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating user feedback: {e}")
    
    def get_performance_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get performance statistics for the last N days."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Overall stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_suggestions,
                    AVG(response_time) as avg_response_time,
                    AVG(user_rating) as avg_rating,
                    SUM(CASE WHEN was_helpful = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as helpful_percentage,
                    SUM(CASE WHEN was_implemented = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as implementation_percentage
                FROM suggestion_metrics 
                WHERE timestamp > ?
            ''', (since_date,))
            
            overall_stats = cursor.fetchone()
            
            # Performance by method
            cursor.execute('''
                SELECT 
                    suggestion_method,
                    COUNT(*) as count,
                    AVG(response_time) as avg_response_time,
                    AVG(user_rating) as avg_rating,
                    SUM(CASE WHEN was_helpful = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as helpful_percentage
                FROM suggestion_metrics 
                WHERE timestamp > ?
                GROUP BY suggestion_method
            ''', (since_date,))
            
            method_stats = cursor.fetchall()
            
            # Performance by document type
            cursor.execute('''
                SELECT 
                    document_type,
                    COUNT(*) as count,
                    AVG(user_rating) as avg_rating,
                    SUM(CASE WHEN was_helpful = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as helpful_percentage
                FROM suggestion_metrics 
                WHERE timestamp > ?
                GROUP BY document_type
            ''', (since_date,))
            
            document_stats = cursor.fetchall()
            
            conn.close()
            
            return {
                "overall": {
                    "total_suggestions": overall_stats[0] or 0,
                    "avg_response_time": round(overall_stats[1] or 0, 3),
                    "avg_rating": round(overall_stats[2] or 0, 2),
                    "helpful_percentage": round(overall_stats[3] or 0, 1),
                    "implementation_percentage": round(overall_stats[4] or 0, 1)
                },
                "by_method": [
                    {
                        "method": row[0],
                        "count": row[1],
                        "avg_response_time": round(row[2], 3),
                        "avg_rating": round(row[3] or 0, 2),
                        "helpful_percentage": round(row[4] or 0, 1)
                    } for row in method_stats
                ],
                "by_document_type": [
                    {
                        "document_type": row[0],
                        "count": row[1],
                        "avg_rating": round(row[2] or 0, 2),
                        "helpful_percentage": round(row[3] or 0, 1)
                    } for row in document_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {}
    
    def get_improvement_recommendations(self) -> List[Dict[str, str]]:
        """Analyze metrics to suggest improvements."""
        recommendations = []
        
        try:
            stats = self.get_performance_stats(days=30)
            
            if not stats:
                return recommendations
            
            overall = stats.get("overall", {})
            by_method = stats.get("by_method", [])
            
            # Check overall performance
            if overall.get("avg_rating", 0) < 3.5:
                recommendations.append({
                    "type": "overall_quality",
                    "issue": "Low average user rating",
                    "suggestion": "Review and improve prompt templates and fallback suggestions",
                    "priority": "high"
                })
            
            if overall.get("helpful_percentage", 0) < 60:
                recommendations.append({
                    "type": "relevance",
                    "issue": "Low helpfulness percentage",
                    "suggestion": "Improve context awareness and feedback classification",
                    "priority": "high"
                })
            
            if overall.get("avg_response_time", 0) > 5.0:
                recommendations.append({
                    "type": "performance",
                    "issue": "Slow response times",
                    "suggestion": "Optimize model parameters or consider model caching",
                    "priority": "medium"
                })
            
            # Check method-specific performance
            for method_data in by_method:
                method = method_data.get("method", "")
                rating = method_data.get("avg_rating", 0)
                helpful = method_data.get("helpful_percentage", 0)
                
                if rating < 3.0 and method_data.get("count", 0) > 10:
                    recommendations.append({
                        "type": "method_specific",
                        "issue": f"Poor performance for {method} method",
                        "suggestion": f"Review and improve {method} implementation",
                        "priority": "medium"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating improvement recommendations: {e}")
            return []

    def get_recent_suggestions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent suggestions for history display."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    suggestion_id,
                    feedback_text,
                    sentence_context,
                    document_type,
                    suggestion_method,
                    response_time,
                    timestamp,
                    user_rating,
                    user_feedback,
                    was_helpful,
                    was_implemented
                FROM suggestion_metrics 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            suggestions = []
            for row in rows:
                suggestions.append({
                    "suggestion_id": row[0],
                    "feedback_text": row[1],
                    "sentence_context": row[2],
                    "document_type": row[3],
                    "suggestion_method": row[4],
                    "response_time": row[5],
                    "timestamp": row[6],
                    "user_rating": row[7],
                    "user_feedback": row[8],
                    "was_helpful": bool(row[9]) if row[9] is not None else None,
                    "was_implemented": bool(row[10]) if row[10] is not None else None
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting recent suggestions: {e}")
            return []
    
class FeedbackLearningSystem:
    """System for learning from user feedback to improve suggestions."""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.learned_patterns = defaultdict(list)
        self.load_learned_patterns()
    
    def load_learned_patterns(self):
        """Load previously learned patterns from successful suggestions."""
        try:
            conn = sqlite3.connect(self.monitor.db_path)
            cursor = conn.cursor()
            
            # Get highly-rated suggestions for pattern learning
            cursor.execute('''
                SELECT feedback_text, sentence_context, user_feedback
                FROM suggestion_metrics 
                WHERE user_rating >= 4 AND user_feedback IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 500
            ''')
            
            successful_suggestions = cursor.fetchall()
            
            for feedback_text, sentence_context, user_feedback in successful_suggestions:
                # Extract patterns from successful suggestions
                pattern = self.extract_pattern(feedback_text, sentence_context, user_feedback)
                if pattern:
                    self.learned_patterns[pattern["type"]].append(pattern)
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error loading learned patterns: {e}")
    
    def extract_pattern(self, feedback_text: str, sentence_context: str, 
                       user_feedback: str) -> Optional[Dict[str, Any]]:
        """Extract learnable patterns from successful suggestions."""
        try:
            # Simple pattern extraction - could be made more sophisticated
            feedback_lower = feedback_text.lower()
            
            if "passive voice" in feedback_lower:
                return {
                    "type": "passive_voice",
                    "context_keywords": self.extract_keywords(sentence_context),
                    "successful_approach": user_feedback[:200],  # Truncate for storage
                    "confidence": 0.8
                }
            elif "long sentence" in feedback_lower:
                return {
                    "type": "sentence_length",
                    "context_length": len(sentence_context.split()),
                    "successful_approach": user_feedback[:200],
                    "confidence": 0.7
                }
            elif "unclear" in feedback_lower or "confusing" in feedback_lower:
                return {
                    "type": "clarity",
                    "context_keywords": self.extract_keywords(sentence_context),
                    "successful_approach": user_feedback[:200],
                    "confidence": 0.6
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting pattern: {e}")
            return None
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract key terms from text for pattern matching."""
        # Simple keyword extraction - could use NLP libraries for better results
        words = text.lower().split()
        # Filter out common words and keep significant terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return keywords[:10]  # Keep top 10 keywords
    
    def get_learned_suggestion(self, feedback_text: str, sentence_context: str) -> Optional[str]:
        """Get suggestion based on learned patterns."""
        try:
            feedback_lower = feedback_text.lower()
            context_keywords = self.extract_keywords(sentence_context)
            
            # Look for matching patterns
            for pattern_type, patterns in self.learned_patterns.items():
                if self.matches_pattern_type(feedback_lower, pattern_type):
                    # Find best matching pattern
                    best_pattern = self.find_best_pattern_match(patterns, context_keywords)
                    if best_pattern:
                        return f"Based on successful similar cases: {best_pattern['successful_approach']}"
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting learned suggestion: {e}")
            return None
    
    def matches_pattern_type(self, feedback_text: str, pattern_type: str) -> bool:
        """Check if feedback matches a learned pattern type."""
        pattern_keywords = {
            "passive_voice": ["passive", "voice"],
            "sentence_length": ["long", "sentence", "complex"],
            "clarity": ["unclear", "confusing", "ambiguous", "vague"]
        }
        
        keywords = pattern_keywords.get(pattern_type, [])
        return any(keyword in feedback_text for keyword in keywords)
    
    def find_best_pattern_match(self, patterns: List[Dict], context_keywords: List[str]) -> Optional[Dict]:
        """Find the best matching pattern based on context similarity."""
        best_match = None
        best_score = 0
        
        for pattern in patterns:
            if "context_keywords" in pattern:
                # Calculate keyword overlap
                pattern_keywords = pattern["context_keywords"]
                overlap = len(set(context_keywords) & set(pattern_keywords))
                score = overlap / max(len(context_keywords), 1) * pattern.get("confidence", 0.5)
                
                if score > best_score:
                    best_score = score
                    best_match = pattern
        
        return best_match if best_score > 0.3 else None

# Global instances
monitor = PerformanceMonitor()
learning_system = FeedbackLearningSystem(monitor)

def track_suggestion(suggestion_id: str, feedback_text: str, sentence_context: str,
                    document_type: str, suggestion_method: str, response_time: float):
    """Convenience function to track a suggestion."""
    metrics = SuggestionMetrics(
        suggestion_id=suggestion_id,
        feedback_text=feedback_text,
        sentence_context=sentence_context,
        document_type=document_type,
        suggestion_method=suggestion_method,
        response_time=response_time,
        timestamp=datetime.now()
    )
    monitor.record_suggestion(metrics)

def record_user_feedback(suggestion_id: str, **feedback_data):
    """Convenience function to record user feedback."""
    monitor.update_user_feedback(suggestion_id, **feedback_data)

def get_performance_dashboard() -> Dict[str, Any]:
    """Get comprehensive performance dashboard data."""
    stats = monitor.get_performance_stats()
    recommendations = monitor.get_improvement_recommendations()
    recent_suggestions = monitor.get_recent_suggestions()
    
    return {
        "overall_stats": stats.get("overall", {}),
        "performance_stats": stats,
        "improvement_recommendations": recommendations,
        "recent_suggestions": recent_suggestions,
        "learned_patterns_count": sum(len(patterns) for patterns in learning_system.learned_patterns.values()),
        "total_feedback_entries": len(monitor.recent_metrics)
    }

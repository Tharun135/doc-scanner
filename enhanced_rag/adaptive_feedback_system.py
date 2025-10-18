"""
Adaptive feedback system that learns from user interactions to improve suggestions.
This addresses the need for continuous improvement based on user acceptance patterns.
"""
import json
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class FeedbackRecord:
    """Record of user feedback on AI suggestions"""
    suggestion_id: str
    rule_id: str
    original_text: str
    suggested_text: str
    user_action: str  # "accepted", "rejected", "modified"
    user_modification: Optional[str] = None
    document_type: str = "general"
    confidence_score: float = 0.0
    method_used: str = "unknown"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class AdaptiveFeedbackSystem:
    """
    System that learns from user feedback to improve AI suggestions.
    Tracks acceptance rates, common modifications, and rule effectiveness.
    """
    
    def __init__(self, db_path: str = "adaptive_feedback.db"):
        self.db_path = db_path
        self._init_database()
        self.rule_effectiveness = {}
        self.method_performance = {}
        self._load_cached_metrics()
    
    def _init_database(self):
        """Initialize SQLite database for feedback storage"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedback_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suggestion_id TEXT,
                    rule_id TEXT,
                    original_text TEXT,
                    suggested_text TEXT,
                    user_action TEXT,
                    user_modification TEXT,
                    document_type TEXT,
                    confidence_score REAL,
                    method_used TEXT,
                    timestamp TEXT
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rule_id ON feedback_records(rule_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON feedback_records(timestamp)
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize feedback database: {e}")
    
    def record_feedback(self, feedback: FeedbackRecord):
        """Record user feedback for a suggestion"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO feedback_records 
                (suggestion_id, rule_id, original_text, suggested_text, 
                 user_action, user_modification, document_type, 
                 confidence_score, method_used, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.suggestion_id,
                feedback.rule_id,
                feedback.original_text,
                feedback.suggested_text,
                feedback.user_action,
                feedback.user_modification,
                feedback.document_type,
                feedback.confidence_score,
                feedback.method_used,
                feedback.timestamp.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            # Update cached metrics
            self._update_rule_effectiveness(feedback)
            
        except Exception as e:
            logger.error(f"Failed to record feedback: {e}")
    
    def get_rule_effectiveness(self, rule_id: str, days: int = 30) -> Dict[str, Any]:
        """Get effectiveness metrics for a specific rule"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT user_action, COUNT(*) as count
                FROM feedback_records 
                WHERE rule_id = ? AND timestamp > ?
                GROUP BY user_action
            """, (rule_id, since_date))
            
            results = cursor.fetchall()
            conn.close()
            
            total = sum(count for _, count in results)
            if total == 0:
                return {"acceptance_rate": 0.0, "total_suggestions": 0}
            
            accepted = sum(count for action, count in results if action == "accepted")
            rejected = sum(count for action, count in results if action == "rejected")
            modified = sum(count for action, count in results if action == "modified")
            
            return {
                "acceptance_rate": accepted / total,
                "rejection_rate": rejected / total,
                "modification_rate": modified / total,
                "total_suggestions": total,
                "effectiveness_score": (accepted + 0.5 * modified) / total
            }
            
        except Exception as e:
            logger.error(f"Failed to get rule effectiveness: {e}")
            return {"acceptance_rate": 0.0, "total_suggestions": 0}
    
    def get_method_performance(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Get performance metrics for different correction methods"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT method_used, user_action, COUNT(*) as count,
                       AVG(confidence_score) as avg_confidence
                FROM feedback_records 
                WHERE timestamp > ?
                GROUP BY method_used, user_action
            """, (since_date,))
            
            results = cursor.fetchall()
            conn.close()
            
            # Process results
            method_stats = {}
            for method, action, count, avg_confidence in results:
                if method not in method_stats:
                    method_stats[method] = {
                        "accepted": 0, "rejected": 0, "modified": 0,
                        "total": 0, "avg_confidence": 0.0
                    }
                
                method_stats[method][action] = count
                method_stats[method]["total"] += count
                method_stats[method]["avg_confidence"] = avg_confidence or 0.0
            
            # Calculate effectiveness scores
            for method in method_stats:
                stats = method_stats[method]
                if stats["total"] > 0:
                    stats["effectiveness_score"] = (
                        stats["accepted"] + 0.5 * stats["modified"]
                    ) / stats["total"]
                else:
                    stats["effectiveness_score"] = 0.0
            
            return method_stats
            
        except Exception as e:
            logger.error(f"Failed to get method performance: {e}")
            return {}
    
    def get_adaptive_confidence_adjustment(self, 
                                         rule_id: str, 
                                         method: str,
                                         base_confidence: float) -> float:
        """
        Adjust confidence score based on historical performance.
        
        Args:
            rule_id: The writing rule being applied
            method: The correction method being used
            base_confidence: Original confidence score
            
        Returns:
            Adjusted confidence score
        """
        # Get rule effectiveness
        rule_effectiveness = self.get_rule_effectiveness(rule_id)
        rule_score = rule_effectiveness.get("effectiveness_score", 0.5)
        
        # Get method performance
        method_performance = self.get_method_performance()
        method_score = method_performance.get(method, {}).get("effectiveness_score", 0.5)
        
        # Weighted adjustment
        rule_weight = 0.6
        method_weight = 0.4
        
        adjustment_factor = (rule_weight * rule_score + method_weight * method_score)
        
        # Apply conservative adjustment
        adjusted_confidence = base_confidence * (0.5 + 0.5 * adjustment_factor)
        
        return min(max(adjusted_confidence, 0.1), 1.0)  # Keep within bounds
    
    def get_suggestions_to_improve(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get suggestions that need improvement based on user feedback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find rules with high rejection rates
            cursor.execute("""
                SELECT rule_id, 
                       COUNT(*) as total,
                       SUM(CASE WHEN user_action = 'rejected' THEN 1 ELSE 0 END) as rejected,
                       SUM(CASE WHEN user_action = 'accepted' THEN 1 ELSE 0 END) as accepted
                FROM feedback_records 
                WHERE timestamp > date('now', '-30 days')
                GROUP BY rule_id
                HAVING total >= 5
                ORDER BY (rejected * 1.0 / total) DESC
                LIMIT ?
            """, (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            improvement_suggestions = []
            for rule_id, total, rejected, accepted in results:
                rejection_rate = rejected / total
                if rejection_rate > 0.3:  # More than 30% rejection rate
                    improvement_suggestions.append({
                        "rule_id": rule_id,
                        "total_suggestions": total,
                        "rejection_rate": rejection_rate,
                        "acceptance_rate": accepted / total,
                        "priority": "high" if rejection_rate > 0.5 else "medium"
                    })
            
            return improvement_suggestions
            
        except Exception as e:
            logger.error(f"Failed to get improvement suggestions: {e}")
            return []
    
    def _update_rule_effectiveness(self, feedback: FeedbackRecord):
        """Update cached rule effectiveness metrics"""
        rule_id = feedback.rule_id
        if rule_id not in self.rule_effectiveness:
            self.rule_effectiveness[rule_id] = {
                "total": 0, "accepted": 0, "rejected": 0, "modified": 0
            }
        
        self.rule_effectiveness[rule_id]["total"] += 1
        self.rule_effectiveness[rule_id][feedback.user_action] += 1
    
    def _load_cached_metrics(self):
        """Load recent metrics into cache for fast access"""
        try:
            # Load rule effectiveness for last 30 days
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=30)).isoformat()
            
            cursor.execute("""
                SELECT rule_id, user_action, COUNT(*) as count
                FROM feedback_records 
                WHERE timestamp > ?
                GROUP BY rule_id, user_action
            """, (since_date,))
            
            results = cursor.fetchall()
            conn.close()
            
            self.rule_effectiveness = {}
            for rule_id, action, count in results:
                if rule_id not in self.rule_effectiveness:
                    self.rule_effectiveness[rule_id] = {
                        "total": 0, "accepted": 0, "rejected": 0, "modified": 0
                    }
                self.rule_effectiveness[rule_id][action] = count
                self.rule_effectiveness[rule_id]["total"] += count
                
        except Exception as e:
            logger.error(f"Failed to load cached metrics: {e}")
    
    def export_analytics_report(self, days: int = 30) -> Dict[str, Any]:
        """Export comprehensive analytics report"""
        
        method_performance = self.get_method_performance(days)
        improvement_suggestions = self.get_suggestions_to_improve()
        
        # Get overall statistics
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute("""
                SELECT COUNT(*) as total_suggestions,
                       SUM(CASE WHEN user_action = 'accepted' THEN 1 ELSE 0 END) as total_accepted,
                       AVG(confidence_score) as avg_confidence
                FROM feedback_records 
                WHERE timestamp > ?
            """, (since_date,))
            
            overall_stats = cursor.fetchone()
            conn.close()
            
            total_suggestions, total_accepted, avg_confidence = overall_stats
            overall_acceptance_rate = total_accepted / total_suggestions if total_suggestions > 0 else 0
            
        except Exception as e:
            logger.error(f"Failed to get overall statistics: {e}")
            total_suggestions = 0
            overall_acceptance_rate = 0
            avg_confidence = 0
        
        return {
            "period_days": days,
            "overall_statistics": {
                "total_suggestions": total_suggestions,
                "overall_acceptance_rate": overall_acceptance_rate,
                "average_confidence": avg_confidence
            },
            "method_performance": method_performance,
            "improvement_suggestions": improvement_suggestions,
            "generated_at": datetime.now().isoformat()
        }


# Global instance for easy access
_adaptive_feedback_system = None

def get_adaptive_feedback_system() -> AdaptiveFeedbackSystem:
    """Get the global adaptive feedback system instance"""
    global _adaptive_feedback_system
    if _adaptive_feedback_system is None:
        _adaptive_feedback_system = AdaptiveFeedbackSystem()
    return _adaptive_feedback_system


if __name__ == "__main__":
    # Test the adaptive feedback system
    system = AdaptiveFeedbackSystem()
    
    # Simulate some feedback records
    test_feedbacks = [
        FeedbackRecord(
            suggestion_id="test_1",
            rule_id="capitalization_sentence_start",
            original_text="it is working.",
            suggested_text="It is working.",
            user_action="accepted",
            method_used="comprehensive_rule_engine",
            confidence_score=0.9
        ),
        FeedbackRecord(
            suggestion_id="test_2",
            rule_id="passive_voice",
            original_text="The data is processed by the system.",
            suggested_text="The system processes the data.",
            user_action="accepted",
            method_used="rule_specific_correction",
            confidence_score=0.8
        ),
        FeedbackRecord(
            suggestion_id="test_3",
            rule_id="long_sentences",
            original_text="This is a very long sentence that should be broken up.",
            suggested_text="This is a very long sentence. It should be broken up.",
            user_action="modified",
            user_modification="This is a long sentence. Break it up for clarity.",
            method_used="enhanced_fallback",
            confidence_score=0.6
        )
    ]
    
    # Record feedback
    for feedback in test_feedbacks:
        system.record_feedback(feedback)
    
    # Get analytics
    report = system.export_analytics_report(days=1)
    print("Analytics Report:")
    print(json.dumps(report, indent=2, default=str))

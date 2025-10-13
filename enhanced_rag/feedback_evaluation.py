# enhanced_rag/feedback_evaluation.py
"""
Feedback loop and evaluation system for continuous RAG improvement.
Implements user feedback collection, performance metrics, and adaptation.
"""

import logging
import time
import json
import sqlite3
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)


@dataclass
class UserFeedback:
    """User feedback on RAG suggestions."""
    feedback_id: str
    query: str
    retrieved_chunks: List[str]
    generated_response: str
    user_rating: int  # 1-5 scale
    user_comment: Optional[str]
    was_helpful: bool
    was_implemented: bool
    timestamp: str
    response_time: float
    method_used: str  # 'semantic', 'hybrid', 'reranked'


@dataclass
class RetrievalMetrics:
    """Metrics for retrieval quality evaluation."""
    query: str
    retrieved_chunk_ids: List[str]
    relevance_scores: List[float]
    precision_at_k: Dict[int, float]  # P@1, P@3, P@5
    recall_at_k: Dict[int, float]
    mrr: float  # Mean Reciprocal Rank
    ndcg: float  # Normalized Discounted Cumulative Gain
    timestamp: str


@dataclass
class GenerationMetrics:
    """Metrics for generation quality evaluation."""
    query: str
    context_chunks: List[str]
    generated_text: str
    bleu_score: Optional[float]
    rouge_scores: Optional[Dict[str, float]]
    semantic_similarity: Optional[float]
    factual_accuracy: Optional[float]
    style_adherence: Optional[float]
    timestamp: str


class FeedbackEvaluationSystem:
    """
    Comprehensive feedback and evaluation system for RAG improvement.
    Handles user feedback collection, performance tracking, and adaptation.
    """
    
    def __init__(self, 
                 db_path: str = "rag_feedback.db",
                 enable_auto_adaptation: bool = True,
                 adaptation_threshold: int = 10):
        """
        Initialize feedback evaluation system.
        
        Args:
            db_path: Path to SQLite database for storing feedback
            enable_auto_adaptation: Whether to auto-adapt based on feedback
            adaptation_threshold: Minimum feedback items before adaptation
        """
        self.db_path = db_path
        self.enable_auto_adaptation = enable_auto_adaptation
        self.adaptation_threshold = adaptation_threshold
        
        # Initialize database
        self._init_database()
        
        # Performance tracking
        self.metrics_cache = {}
        self.adaptation_history = []
        
        logger.info(f"✅ Feedback evaluation system initialized")
    
    def _init_database(self):
        """Initialize SQLite database for feedback storage."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # User feedback table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_feedback (
                    feedback_id TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    retrieved_chunks TEXT NOT NULL,
                    generated_response TEXT NOT NULL,
                    user_rating INTEGER NOT NULL,
                    user_comment TEXT,
                    was_helpful BOOLEAN NOT NULL,
                    was_implemented BOOLEAN NOT NULL,
                    timestamp TEXT NOT NULL,
                    response_time REAL NOT NULL,
                    method_used TEXT NOT NULL
                )
            ''')
            
            # Retrieval metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS retrieval_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    retrieved_chunk_ids TEXT NOT NULL,
                    relevance_scores TEXT NOT NULL,
                    precision_at_k TEXT NOT NULL,
                    recall_at_k TEXT NOT NULL,
                    mrr REAL NOT NULL,
                    ndcg REAL NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            # Generation metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generation_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    context_chunks TEXT NOT NULL,
                    generated_text TEXT NOT NULL,
                    bleu_score REAL,
                    rouge_scores TEXT,
                    semantic_similarity REAL,
                    factual_accuracy REAL,
                    style_adherence REAL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            # Adaptation history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS adaptation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adaptation_type TEXT NOT NULL,
                    parameters_changed TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    feedback_count INTEGER NOT NULL,
                    performance_before TEXT NOT NULL,
                    performance_after TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Database initialized: {self.db_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            raise
    
    def record_user_feedback(self, feedback: UserFeedback) -> bool:
        """
        Record user feedback in the database.
        
        Args:
            feedback: UserFeedback object
            
        Returns:
            True if successfully recorded
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_feedback (
                    feedback_id, query, retrieved_chunks, generated_response,
                    user_rating, user_comment, was_helpful, was_implemented,
                    timestamp, response_time, method_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                feedback.feedback_id,
                feedback.query,
                json.dumps(feedback.retrieved_chunks),
                feedback.generated_response,
                feedback.user_rating,
                feedback.user_comment,
                feedback.was_helpful,
                feedback.was_implemented,
                feedback.timestamp,
                feedback.response_time,
                feedback.method_used
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ User feedback recorded: {feedback.feedback_id}")
            
            # Check if adaptation is needed
            if self.enable_auto_adaptation:
                self._check_adaptation_trigger()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record user feedback: {e}")
            return False
    
    def record_retrieval_metrics(self, metrics: RetrievalMetrics) -> bool:
        """
        Record retrieval performance metrics.
        
        Args:
            metrics: RetrievalMetrics object
            
        Returns:
            True if successfully recorded
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO retrieval_metrics (
                    query, retrieved_chunk_ids, relevance_scores,
                    precision_at_k, recall_at_k, mrr, ndcg, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.query,
                json.dumps(metrics.retrieved_chunk_ids),
                json.dumps(metrics.relevance_scores),
                json.dumps(metrics.precision_at_k),
                json.dumps(metrics.recall_at_k),
                metrics.mrr,
                metrics.ndcg,
                metrics.timestamp
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record retrieval metrics: {e}")
            return False
    
    def record_generation_metrics(self, metrics: GenerationMetrics) -> bool:
        """
        Record generation performance metrics.
        
        Args:
            metrics: GenerationMetrics object
            
        Returns:
            True if successfully recorded
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO generation_metrics (
                    query, context_chunks, generated_text,
                    bleu_score, rouge_scores, semantic_similarity,
                    factual_accuracy, style_adherence, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.query,
                json.dumps(metrics.context_chunks),
                metrics.generated_text,
                metrics.bleu_score,
                json.dumps(metrics.rouge_scores) if metrics.rouge_scores else None,
                metrics.semantic_similarity,
                metrics.factual_accuracy,
                metrics.style_adherence,
                metrics.timestamp
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to record generation metrics: {e}")
            return False
    
    def get_feedback_analytics(self, 
                              days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive feedback analytics for the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Analytics dictionary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Date filter
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get feedback stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_feedback,
                    AVG(user_rating) as avg_rating,
                    SUM(CASE WHEN was_helpful = 1 THEN 1 ELSE 0 END) as helpful_count,
                    SUM(CASE WHEN was_implemented = 1 THEN 1 ELSE 0 END) as implemented_count,
                    AVG(response_time) as avg_response_time
                FROM user_feedback 
                WHERE timestamp >= ?
            ''', (cutoff_date,))
            
            stats = cursor.fetchone()
            
            # Get feedback by method
            cursor.execute('''
                SELECT method_used, COUNT(*), AVG(user_rating)
                FROM user_feedback 
                WHERE timestamp >= ?
                GROUP BY method_used
            ''', (cutoff_date,))
            
            method_stats = cursor.fetchall()
            
            # Get rating distribution
            cursor.execute('''
                SELECT user_rating, COUNT(*)
                FROM user_feedback 
                WHERE timestamp >= ?
                GROUP BY user_rating
                ORDER BY user_rating
            ''', (cutoff_date,))
            
            rating_distribution = cursor.fetchall()
            
            conn.close()
            
            analytics = {
                'period_days': days,
                'total_feedback': stats[0] or 0,
                'average_rating': stats[1] or 0.0,
                'helpful_percentage': (stats[2] / max(1, stats[0])) * 100 if stats[0] else 0,
                'implementation_percentage': (stats[3] / max(1, stats[0])) * 100 if stats[0] else 0,
                'average_response_time': stats[4] or 0.0,
                'method_performance': {
                    method: {'count': count, 'avg_rating': rating}
                    for method, count, rating in method_stats
                },
                'rating_distribution': {
                    rating: count for rating, count in rating_distribution
                }
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Failed to get feedback analytics: {e}")
            return {}
    
    def get_performance_trends(self, 
                              metric: str = "user_rating",
                              days: int = 30,
                              granularity: str = "daily") -> List[Tuple[str, float]]:
        """
        Get performance trends over time.
        
        Args:
            metric: Metric to track ('user_rating', 'response_time', 'helpful_rate')
            days: Number of days to analyze
            granularity: Time granularity ('daily', 'weekly')
            
        Returns:
            List of (date, value) tuples
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            if granularity == "daily":
                date_format = "DATE(timestamp)"
            else:
                date_format = "DATE(timestamp, 'weekday 0', '-7 days')"
            
            if metric == "user_rating":
                query = f'''
                    SELECT {date_format} as period, AVG(user_rating)
                    FROM user_feedback 
                    WHERE timestamp >= ?
                    GROUP BY period
                    ORDER BY period
                '''
            elif metric == "response_time":
                query = f'''
                    SELECT {date_format} as period, AVG(response_time)
                    FROM user_feedback 
                    WHERE timestamp >= ?
                    GROUP BY period
                    ORDER BY period
                '''
            elif metric == "helpful_rate":
                query = f'''
                    SELECT {date_format} as period, 
                           AVG(CASE WHEN was_helpful = 1 THEN 1.0 ELSE 0.0 END) * 100
                    FROM user_feedback 
                    WHERE timestamp >= ?
                    GROUP BY period
                    ORDER BY period
                '''
            else:
                return []
            
            cursor.execute(query, (cutoff_date,))
            results = cursor.fetchall()
            
            conn.close()
            
            return [(date, value) for date, value in results]
            
        except Exception as e:
            logger.error(f"❌ Failed to get performance trends: {e}")
            return []
    
    def identify_improvement_opportunities(self) -> List[Dict[str, Any]]:
        """
        Identify specific areas for improvement based on feedback patterns.
        
        Returns:
            List of improvement opportunities with priorities
        """
        opportunities = []
        
        try:
            analytics = self.get_feedback_analytics(days=30)
            
            # Low average rating
            if analytics.get('average_rating', 0) < 3.5:
                opportunities.append({
                    'type': 'Low Overall Rating',
                    'priority': 'High',
                    'description': f"Average rating is {analytics['average_rating']:.2f}",
                    'suggested_actions': [
                        'Review prompt templates',
                        'Improve retrieval quality',
                        'Add more training examples'
                    ]
                })
            
            # Low helpful percentage
            if analytics.get('helpful_percentage', 0) < 60:
                opportunities.append({
                    'type': 'Low Helpfulness',
                    'priority': 'High',
                    'description': f"Only {analytics['helpful_percentage']:.1f}% found suggestions helpful",
                    'suggested_actions': [
                        'Improve context relevance',
                        'Enhance suggestion specificity',
                        'Better style guide integration'
                    ]
                })
            
            # Slow response times
            if analytics.get('average_response_time', 0) > 5.0:
                opportunities.append({
                    'type': 'Slow Response Time',
                    'priority': 'Medium',
                    'description': f"Average response time is {analytics['average_response_time']:.2f}s",
                    'suggested_actions': [
                        'Optimize retrieval queries',
                        'Implement better caching',
                        'Use faster embedding models'
                    ]
                })
            
            # Method-specific issues
            method_performance = analytics.get('method_performance', {})
            for method, stats in method_performance.items():
                if stats['avg_rating'] < 3.0:
                    opportunities.append({
                        'type': f'Poor {method} Performance',
                        'priority': 'Medium',
                        'description': f"{method} method has {stats['avg_rating']:.2f} average rating",
                        'suggested_actions': [
                            f'Improve {method} algorithm',
                            'Review training data',
                            'Adjust scoring weights'
                        ]
                    })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"❌ Failed to identify improvement opportunities: {e}")
            return []
    
    def _check_adaptation_trigger(self):
        """Check if enough feedback has been collected to trigger adaptation."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count recent feedback
            recent_date = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute('''
                SELECT COUNT(*) FROM user_feedback 
                WHERE timestamp >= ?
            ''', (recent_date,))
            
            recent_feedback_count = cursor.fetchone()[0]
            conn.close()
            
            if recent_feedback_count >= self.adaptation_threshold:
                self._perform_adaptation()
                
        except Exception as e:
            logger.error(f"❌ Failed to check adaptation trigger: {e}")
    
    def _perform_adaptation(self):
        """Perform automatic adaptation based on feedback patterns."""
        try:
            opportunities = self.identify_improvement_opportunities()
            high_priority = [opp for opp in opportunities if opp['priority'] == 'High']
            
            if not high_priority:
                return
            
            # Record adaptation attempt
            adaptation_record = {
                'adaptation_type': 'auto_feedback_based',
                'parameters_changed': json.dumps([opp['type'] for opp in high_priority]),
                'reason': f"Found {len(high_priority)} high-priority improvement opportunities",
                'feedback_count': self.adaptation_threshold,
                'performance_before': json.dumps(self.get_feedback_analytics(days=7)),
                'timestamp': datetime.now().isoformat()
            }
            
            # Store adaptation record
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO adaptation_history (
                    adaptation_type, parameters_changed, reason,
                    feedback_count, performance_before, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                adaptation_record['adaptation_type'],
                adaptation_record['parameters_changed'],
                adaptation_record['reason'],
                adaptation_record['feedback_count'],
                adaptation_record['performance_before'],
                adaptation_record['timestamp']
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Adaptation triggered: {adaptation_record['reason']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to perform adaptation: {e}")
    
    def export_feedback_data(self, 
                            output_path: str,
                            format: str = "json",
                            days: int = 30) -> bool:
        """
        Export feedback data for external analysis.
        
        Args:
            output_path: Path to save exported data
            format: Export format ('json', 'csv')
            days: Number of days of data to export
            
        Returns:
            True if export successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT * FROM user_feedback 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (cutoff_date,))
            
            feedback_data = cursor.fetchall()
            
            # Get column names
            cursor.execute("PRAGMA table_info(user_feedback)")
            columns = [col[1] for col in cursor.fetchall()]
            
            conn.close()
            
            if format == "json":
                data = [dict(zip(columns, row)) for row in feedback_data]
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == "csv":
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    writer.writerows(feedback_data)
            
            logger.info(f"✅ Feedback data exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to export feedback data: {e}")
            return False
    
    def generate_improvement_report(self) -> str:
        """
        Generate a comprehensive improvement report.
        
        Returns:
            Formatted report string
        """
        try:
            analytics = self.get_feedback_analytics(days=30)
            opportunities = self.identify_improvement_opportunities()
            trends = self.get_performance_trends(days=30)
            
            report = f"""
RAG SYSTEM IMPROVEMENT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

PERFORMANCE SUMMARY (Last 30 Days):
- Total Feedback: {analytics.get('total_feedback', 0)}
- Average Rating: {analytics.get('average_rating', 0):.2f}/5.0
- Helpful Rate: {analytics.get('helpful_percentage', 0):.1f}%
- Implementation Rate: {analytics.get('implementation_percentage', 0):.1f}%
- Avg Response Time: {analytics.get('average_response_time', 0):.2f}s

METHOD PERFORMANCE:
"""
            
            for method, stats in analytics.get('method_performance', {}).items():
                report += f"- {method}: {stats['avg_rating']:.2f}/5.0 ({stats['count']} samples)\n"
            
            report += f"\nIMPROVEMENT OPPORTUNITIES ({len(opportunities)} identified):\n"
            
            for i, opp in enumerate(opportunities, 1):
                report += f"{i}. {opp['type']} ({opp['priority']} Priority)\n"
                report += f"   {opp['description']}\n"
                report += f"   Suggested Actions: {', '.join(opp['suggested_actions'])}\n\n"
            
            if trends:
                recent_trend = trends[-5:]  # Last 5 data points
                if len(recent_trend) > 1:
                    trend_direction = "improving" if recent_trend[-1][1] > recent_trend[0][1] else "declining"
                    report += f"RECENT TREND: {trend_direction}\n"
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate improvement report: {e}")
            return "Error generating report"


# Global instance for easy access
_global_feedback_system = None

def get_feedback_system(db_path: str = "rag_feedback.db") -> FeedbackEvaluationSystem:
    """
    Get global feedback evaluation system instance.
    
    Args:
        db_path: Database path
        
    Returns:
        Global feedback system instance
    """
    global _global_feedback_system
    
    if _global_feedback_system is None:
        _global_feedback_system = FeedbackEvaluationSystem(db_path)
    
    return _global_feedback_system
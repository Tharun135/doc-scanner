"""
RAG Evaluation and Metrics System for DocScanner
Tracks retrieval quality, user feedback, and system performance.
"""

import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class EvaluationMetric:
    """Represents a single evaluation metric."""
    metric_id: str
    timestamp: datetime
    query: str
    retrieval_method: str
    relevance_score: float
    user_rating: Optional[float] = None  # 1-5 rating from user
    latency_ms: float = 0
    num_results: int = 0
    success: bool = True
    metadata: Dict[str, Any] = None

@dataclass
class RAGPerformanceStats:
    """Performance statistics for RAG system."""
    total_queries: int
    avg_relevance_score: float
    avg_user_rating: Optional[float]
    avg_latency_ms: float
    success_rate: float
    most_common_queries: List[str]
    retrieval_method_performance: Dict[str, Dict[str, float]]
    time_period: str

class RAGEvaluator:
    """Handles RAG system evaluation and metrics collection."""
    
    def __init__(self, db_path: str = "rag_evaluation.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for storing evaluation metrics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS rag_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_id TEXT UNIQUE,
                        timestamp TEXT NOT NULL,
                        query TEXT NOT NULL,
                        retrieval_method TEXT NOT NULL,
                        relevance_score REAL NOT NULL,
                        user_rating REAL,
                        latency_ms REAL DEFAULT 0,
                        num_results INTEGER DEFAULT 0,
                        success INTEGER DEFAULT 1,
                        metadata TEXT
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        metric_id TEXT,
                        feedback_type TEXT,  -- 'accept', 'reject', 'edit'
                        feedback_text TEXT,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (metric_id) REFERENCES rag_metrics (metric_id)
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON rag_metrics(timestamp)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_method ON rag_metrics(retrieval_method)
                ''')
                
            logger.info("✅ RAG evaluation database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG evaluation database: {e}")
    
    def log_retrieval(self, query: str, retrieval_method: str, results: List[Any],
                     latency_ms: float = 0, metadata: Dict[str, Any] = None) -> str:
        """
        Log a retrieval operation for evaluation.
        
        Returns:
            metric_id for tracking this retrieval
        """
        import uuid
        
        metric_id = str(uuid.uuid4())
        
        # Calculate relevance metrics
        relevance_score = 0
        if results:
            relevance_score = statistics.mean([
                getattr(result, 'relevance_score', 0) for result in results
            ])
        
        metric = EvaluationMetric(
            metric_id=metric_id,
            timestamp=datetime.now(),
            query=query,
            retrieval_method=retrieval_method,
            relevance_score=relevance_score,
            latency_ms=latency_ms,
            num_results=len(results),
            success=len(results) > 0,
            metadata=metadata or {}
        )
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO rag_metrics 
                    (metric_id, timestamp, query, retrieval_method, relevance_score, 
                     latency_ms, num_results, success, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metric.metric_id,
                    metric.timestamp.isoformat(),
                    metric.query,
                    metric.retrieval_method,
                    metric.relevance_score,
                    metric.latency_ms,
                    metric.num_results,
                    1 if metric.success else 0,
                    json.dumps(metric.metadata)
                ))
            
            logger.debug(f"📊 Logged retrieval metric: {metric_id}")
            return metric_id
            
        except Exception as e:
            logger.error(f"Failed to log retrieval metric: {e}")
            return ""
    
    def log_user_feedback(self, metric_id: str, feedback_type: str, 
                         feedback_text: str = "", user_rating: float = None):
        """Log user feedback for a specific retrieval."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Log user feedback
                conn.execute('''
                    INSERT INTO user_feedback (metric_id, feedback_type, feedback_text, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (metric_id, feedback_type, feedback_text, datetime.now().isoformat()))
                
                # Update user rating if provided
                if user_rating is not None:
                    conn.execute('''
                        UPDATE rag_metrics SET user_rating = ? WHERE metric_id = ?
                    ''', (user_rating, metric_id))
            
            logger.debug(f"📝 Logged user feedback: {feedback_type} for {metric_id}")
            
        except Exception as e:
            logger.error(f"Failed to log user feedback: {e}")
    
    def get_performance_stats(self, days: int = 30) -> RAGPerformanceStats:
        """Get performance statistics for the specified time period."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Basic metrics
                cursor = conn.execute('''
                    SELECT 
                        COUNT(*) as total_queries,
                        AVG(relevance_score) as avg_relevance,
                        AVG(user_rating) as avg_user_rating,
                        AVG(latency_ms) as avg_latency,
                        SUM(success) * 1.0 / COUNT(*) as success_rate
                    FROM rag_metrics 
                    WHERE timestamp > ?
                ''', (cutoff_date.isoformat(),))
                
                basic_stats = cursor.fetchone()
                
                # Most common queries
                cursor = conn.execute('''
                    SELECT query, COUNT(*) as count
                    FROM rag_metrics 
                    WHERE timestamp > ?
                    GROUP BY query
                    ORDER BY count DESC
                    LIMIT 10
                ''', (cutoff_date.isoformat(),))
                
                common_queries = [row[0] for row in cursor.fetchall()]
                
                # Method performance
                cursor = conn.execute('''
                    SELECT 
                        retrieval_method,
                        AVG(relevance_score) as avg_relevance,
                        AVG(latency_ms) as avg_latency,
                        SUM(success) * 1.0 / COUNT(*) as success_rate,
                        COUNT(*) as query_count
                    FROM rag_metrics 
                    WHERE timestamp > ?
                    GROUP BY retrieval_method
                ''', (cutoff_date.isoformat(),))
                
                method_performance = {}
                for row in cursor.fetchall():
                    method, avg_rel, avg_lat, succ_rate, count = row
                    method_performance[method] = {
                        'avg_relevance': avg_rel,
                        'avg_latency': avg_lat,
                        'success_rate': succ_rate,
                        'query_count': count
                    }
            
            stats = RAGPerformanceStats(
                total_queries=basic_stats[0] or 0,
                avg_relevance_score=basic_stats[1] or 0,
                avg_user_rating=basic_stats[2],
                avg_latency_ms=basic_stats[3] or 0,
                success_rate=basic_stats[4] or 0,
                most_common_queries=common_queries,
                retrieval_method_performance=method_performance,
                time_period=f"Last {days} days"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return RAGPerformanceStats(
                total_queries=0, avg_relevance_score=0, avg_user_rating=None,
                avg_latency_ms=0, success_rate=0, most_common_queries=[],
                retrieval_method_performance={}, time_period=f"Last {days} days"
            )
    
    def get_evaluation_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for the evaluation dashboard."""
        stats_7d = self.get_performance_stats(7)
        stats_30d = self.get_performance_stats(30)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Daily query counts for the last 30 days
                cursor = conn.execute('''
                    SELECT DATE(timestamp) as date, COUNT(*) as count
                    FROM rag_metrics 
                    WHERE timestamp > ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date
                ''', ((datetime.now() - timedelta(days=30)).isoformat(),))
                
                daily_counts = {row[0]: row[1] for row in cursor.fetchall()}
                
                # User feedback distribution
                cursor = conn.execute('''
                    SELECT feedback_type, COUNT(*) as count
                    FROM user_feedback
                    WHERE timestamp > ?
                    GROUP BY feedback_type
                ''', ((datetime.now() - timedelta(days=30)).isoformat(),))
                
                feedback_distribution = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Recent queries and ratings
                cursor = conn.execute('''
                    SELECT query, relevance_score, user_rating, retrieval_method, timestamp
                    FROM rag_metrics 
                    WHERE timestamp > ?
                    ORDER BY timestamp DESC
                    LIMIT 50
                ''', ((datetime.now() - timedelta(days=7)).isoformat(),))
                
                recent_queries = []
                for row in cursor.fetchall():
                    recent_queries.append({
                        'query': row[0],
                        'relevance_score': row[1],
                        'user_rating': row[2],
                        'method': row[3],
                        'timestamp': row[4]
                    })
        
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            daily_counts = {}
            feedback_distribution = {}
            recent_queries = []
        
        return {
            'stats_7d': asdict(stats_7d),
            'stats_30d': asdict(stats_30d),
            'daily_query_counts': daily_counts,
            'feedback_distribution': feedback_distribution,
            'recent_queries': recent_queries,
            'generated_at': datetime.now().isoformat()
        }
    
    def export_metrics(self, output_path: str, days: int = 30) -> bool:
        """Export metrics to JSON file for external analysis."""
        try:
            dashboard_data = self.get_evaluation_dashboard_data()
            
            with open(output_path, 'w') as f:
                json.dump(dashboard_data, f, indent=2, default=str)
            
            logger.info(f"✅ Exported RAG metrics to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return False
    
    def cleanup_old_metrics(self, days_to_keep: int = 90):
        """Clean up old metrics to keep database size manageable."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Delete old user feedback
                conn.execute('''
                    DELETE FROM user_feedback 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),))
                
                # Delete old metrics
                deleted_count = conn.execute('''
                    DELETE FROM rag_metrics 
                    WHERE timestamp < ?
                ''', (cutoff_date.isoformat(),)).rowcount
                
                conn.execute('VACUUM')
            
            logger.info(f"🧹 Cleaned up {deleted_count} old metrics (older than {days_to_keep} days)")
            
        except Exception as e:
            logger.error(f"Failed to clean up old metrics: {e}")

class RealtimeEvaluator:
    """Real-time evaluation of retrieval quality during operation."""
    
    def __init__(self):
        self.query_cache = {}  # Cache recent queries for performance
    
    def evaluate_retrieval_quality(self, query: str, results: List[Any]) -> Dict[str, float]:
        """
        Evaluate the quality of retrieval results in real-time.
        
        Returns:
            Dictionary with quality metrics
        """
        if not results:
            return {
                'relevance_score': 0.0,
                'diversity_score': 0.0,
                'coverage_score': 0.0,
                'quality_score': 0.0
            }
        
        # Calculate relevance (average of individual relevance scores)
        relevance_scores = [getattr(result, 'relevance_score', 0) for result in results]
        avg_relevance = statistics.mean(relevance_scores)
        
        # Calculate diversity (how different the results are from each other)
        diversity_score = self._calculate_diversity(results)
        
        # Calculate coverage (how well the results cover different aspects of the query)
        coverage_score = self._calculate_coverage(query, results)
        
        # Overall quality score (weighted combination)
        quality_score = (
            0.5 * avg_relevance +
            0.3 * diversity_score +
            0.2 * coverage_score
        )
        
        return {
            'relevance_score': avg_relevance,
            'diversity_score': diversity_score,
            'coverage_score': coverage_score,
            'quality_score': quality_score
        }
    
    def _calculate_diversity(self, results: List[Any]) -> float:
        """Calculate how diverse the results are."""
        if len(results) <= 1:
            return 1.0
        
        # Simple diversity based on content length and source variety
        contents = [getattr(result, 'content', '') for result in results]
        sources = [getattr(result, 'source_doc_id', 'unknown') for result in results]
        
        # Length diversity
        lengths = [len(content) for content in contents]
        length_diversity = statistics.stdev(lengths) / max(lengths) if max(lengths) > 0 else 0
        
        # Source diversity
        unique_sources = len(set(sources))
        source_diversity = unique_sources / len(sources)
        
        return (length_diversity + source_diversity) / 2
    
    def _calculate_coverage(self, query: str, results: List[Any]) -> float:
        """Calculate how well results cover the query."""
        query_words = set(query.lower().split())
        
        if not query_words:
            return 1.0
        
        # Count how many query words appear in results
        covered_words = set()
        
        for result in results:
            content = getattr(result, 'content', '').lower()
            for word in query_words:
                if word in content:
                    covered_words.add(word)
        
        return len(covered_words) / len(query_words)

# Global evaluator instance
_global_evaluator = None

def get_rag_evaluator() -> RAGEvaluator:
    """Get or create the global RAG evaluator instance."""
    global _global_evaluator
    if _global_evaluator is None:
        _global_evaluator = RAGEvaluator()
    return _global_evaluator

def log_retrieval_for_evaluation(query: str, method: str, results: List[Any], 
                                latency_ms: float = 0) -> str:
    """Convenience function to log retrieval for evaluation."""
    evaluator = get_rag_evaluator()
    return evaluator.log_retrieval(query, method, results, latency_ms)

def log_user_feedback_for_evaluation(metric_id: str, feedback_type: str, 
                                   feedback_text: str = "", rating: float = None):
    """Convenience function to log user feedback."""
    evaluator = get_rag_evaluator()
    evaluator.log_user_feedback(metric_id, feedback_type, feedback_text, rating)

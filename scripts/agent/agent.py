"""
Document Review Agent - Main Agent Class
This module contains the core agent that orchestrates document review tasks.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import time
from datetime import datetime

from ..app.ai_improvement import get_enhanced_ai_suggestion
from ..app.app import analyze_text, parse_file
from .tools import DocumentTools, AITools, ValidationTools
from .protocol import AgentProtocol, TaskResult, AgentCapability

logger = logging.getLogger(__name__)


@dataclass
class DocumentReviewTask:
    """Represents a document review task."""
    task_id: str
    document_path: str
    document_type: str = "general"
    writing_goals: List[str] = None
    priority: str = "normal"  # low, normal, high, urgent
    created_at: datetime = None
    status: str = "pending"  # pending, in_progress, completed, failed
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.writing_goals is None:
            self.writing_goals = ["clarity", "conciseness", "professionalism"]


@dataclass
class ReviewResult:
    """Represents the result of a document review."""
    task_id: str
    document_path: str
    total_sentences: int
    total_issues: int
    quality_score: float
    suggestions: List[Dict[str, Any]]
    processing_time: float
    timestamp: datetime
    agent_version: str = "1.0.0"


class DocumentReviewAgent(AgentProtocol):
    """
    Main Document Review Agent class.
    
    This agent can:
    - Analyze documents for writing quality
    - Provide AI-powered suggestions
    - Handle batch processing
    - Integrate with VS Code extension
    - Support Model Context Protocol (MCP)
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.tools = {
            'document': DocumentTools(),
            'ai': AITools(),
            'validation': ValidationTools()
        }
        self.task_queue = asyncio.Queue()
        self.results_cache = {}
        self.is_running = False
        
        # Initialize logging
        log_level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        logger.info(f"DocumentReviewAgent initialized with config: {self.config}")
    
    @property
    def capabilities(self) -> List[AgentCapability]:
        """Return the agent's capabilities."""
        return [
            AgentCapability(
                name="document_analysis",
                description="Analyze documents for writing quality and issues",
                parameters={
                    "document_path": {"type": "string", "required": True},
                    "document_type": {"type": "string", "default": "general"},
                    "writing_goals": {"type": "array", "default": ["clarity", "conciseness"]}
                }
            ),
            AgentCapability(
                name="ai_suggestions",
                description="Generate AI-powered writing suggestions",
                parameters={
                    "feedback_text": {"type": "string", "required": True},
                    "sentence_context": {"type": "string", "required": False},
                    "document_type": {"type": "string", "default": "general"}
                }
            ),
            AgentCapability(
                name="batch_processing",
                description="Process multiple documents in batch",
                parameters={
                    "file_paths": {"type": "array", "required": True},
                    "parallel": {"type": "boolean", "default": True}
                }
            ),
            AgentCapability(
                name="quality_assessment",
                description="Assess overall document quality",
                parameters={
                    "document_path": {"type": "string", "required": True}
                }
            )
        ]
    
    async def start(self):
        """Start the agent."""
        if self.is_running:
            logger.warning("Agent is already running")
            return
        
        self.is_running = True
        logger.info("DocumentReviewAgent started")
        
        # Start task processor
        asyncio.create_task(self._process_tasks())
    
    async def stop(self):
        """Stop the agent."""
        self.is_running = False
        logger.info("DocumentReviewAgent stopped")
    
    async def execute_task(self, task_type: str, parameters: Dict[str, Any]) -> TaskResult:
        """Execute a specific task."""
        start_time = time.time()
        
        try:
            if task_type == "document_analysis":
                result = await self._analyze_document(parameters)
            elif task_type == "ai_suggestions":
                result = await self._generate_ai_suggestion(parameters)
            elif task_type == "batch_processing":
                result = await self._process_batch(parameters)
            elif task_type == "quality_assessment":
                result = await self._assess_quality(parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            execution_time = time.time() - start_time
            
            return TaskResult(
                success=True,
                data=result,
                execution_time=execution_time,
                agent_id="document_review_agent",
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            execution_time = time.time() - start_time
            
            return TaskResult(
                success=False,
                error=str(e),
                execution_time=execution_time,
                agent_id="document_review_agent",
                timestamp=datetime.now()
            )
    
    async def add_task(self, task: DocumentReviewTask):
        """Add a task to the queue."""
        await self.task_queue.put(task)
        logger.info(f"Task {task.task_id} added to queue")
    
    async def get_result(self, task_id: str) -> Optional[ReviewResult]:
        """Get the result of a completed task."""
        return self.results_cache.get(task_id)
    
    async def _process_tasks(self):
        """Process tasks from the queue."""
        while self.is_running:
            try:
                # Wait for a task with timeout
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                logger.info(f"Processing task {task.task_id}")
                task.status = "in_progress"
                
                # Execute the task
                result = await self._review_document(task)
                
                # Store result
                self.results_cache[task.task_id] = result
                task.status = "completed"
                
                logger.info(f"Task {task.task_id} completed successfully")
                
            except asyncio.TimeoutError:
                # No tasks in queue, continue
                continue
            except Exception as e:
                logger.error(f"Error processing task: {str(e)}")
                if 'task' in locals():
                    task.status = "failed"
    
    async def _review_document(self, task: DocumentReviewTask) -> ReviewResult:
        """Review a single document."""
        start_time = time.time()
        
        # Read and parse the document
        document_path = Path(task.document_path)
        if not document_path.exists():
            raise FileNotFoundError(f"Document not found: {task.document_path}")
        
        # Use existing parsing logic
        with open(document_path, 'rb') as file:
            html_content = parse_file(file)
        
        # Analyze the content
        sentences = analyze_text(html_content)
        
        # Generate AI suggestions for each issue
        suggestions = []
        for sentence in sentences:
            for feedback_item in sentence.get('feedback', []):
                ai_suggestion = get_enhanced_ai_suggestion(
                    feedback_text=feedback_item.get('message', ''),
                    sentence_context=sentence.get('sentence', ''),
                    document_type=task.document_type,
                    writing_goals=task.writing_goals
                )
                
                suggestions.append({
                    'sentence_index': sentence.get('sentence_index', 0),
                    'sentence': sentence.get('sentence', ''),
                    'issue': feedback_item.get('message', ''),
                    'suggestion': ai_suggestion.get('suggestion', ''),
                    'confidence': ai_suggestion.get('confidence', 'low'),
                    'method': ai_suggestion.get('method', 'unknown')
                })
        
        # Calculate metrics
        total_sentences = len(sentences)
        total_issues = sum(len(s.get('feedback', [])) for s in sentences)
        quality_score = self._calculate_quality_score(total_sentences, total_issues)
        
        processing_time = time.time() - start_time
        
        return ReviewResult(
            task_id=task.task_id,
            document_path=task.document_path,
            total_sentences=total_sentences,
            total_issues=total_issues,
            quality_score=quality_score,
            suggestions=suggestions,
            processing_time=processing_time,
            timestamp=datetime.now()
        )
    
    async def _analyze_document(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a document for writing quality."""
        document_path = parameters.get('document_path')
        document_type = parameters.get('document_type', 'general')
        writing_goals = parameters.get('writing_goals', ['clarity', 'conciseness'])
        
        task = DocumentReviewTask(
            task_id=f"analysis_{int(time.time())}",
            document_path=document_path,
            document_type=document_type,
            writing_goals=writing_goals
        )
        
        result = await self._review_document(task)
        return asdict(result)
    
    async def _generate_ai_suggestion(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI suggestions for specific feedback."""
        feedback_text = parameters.get('feedback_text')
        sentence_context = parameters.get('sentence_context', '')
        document_type = parameters.get('document_type', 'general')
        
        suggestion = get_enhanced_ai_suggestion(
            feedback_text=feedback_text,
            sentence_context=sentence_context,
            document_type=document_type
        )
        
        return suggestion
    
    async def _process_batch(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process multiple documents in batch."""
        file_paths = parameters.get('file_paths', [])
        parallel = parameters.get('parallel', True)
        
        if parallel:
            tasks = []
            for i, file_path in enumerate(file_paths):
                task = DocumentReviewTask(
                    task_id=f"batch_{int(time.time())}_{i}",
                    document_path=file_path
                )
                tasks.append(self._review_document(task))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for i, file_path in enumerate(file_paths):
                task = DocumentReviewTask(
                    task_id=f"batch_{int(time.time())}_{i}",
                    document_path=file_path
                )
                result = await self._review_document(task)
                results.append(result)
        
        # Convert results to dict format
        return {
            'total_files': len(file_paths),
            'successful_files': len([r for r in results if not isinstance(r, Exception)]),
            'results': [asdict(r) if not isinstance(r, Exception) else {'error': str(r)} for r in results]
        }
    
    async def _assess_quality(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall document quality."""
        document_path = parameters.get('document_path')
        
        # Use document analysis
        analysis_result = await self._analyze_document({'document_path': document_path})
        
        # Additional quality metrics
        quality_metrics = {
            'overall_score': analysis_result['quality_score'],
            'readability': 'good' if analysis_result['quality_score'] > 0.7 else 'poor',
            'issue_density': analysis_result['total_issues'] / max(analysis_result['total_sentences'], 1),
            'recommendations': self._generate_quality_recommendations(analysis_result)
        }
        
        return quality_metrics
    
    def _calculate_quality_score(self, total_sentences: int, total_issues: int) -> float:
        """Calculate a quality score based on issues found."""
        if total_sentences == 0:
            return 0.0
        
        issue_ratio = total_issues / total_sentences
        # Score decreases as issue ratio increases
        score = max(0.0, 1.0 - (issue_ratio * 0.5))
        return round(score, 2)
    
    def _generate_quality_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        if analysis_result['quality_score'] < 0.5:
            recommendations.append("Document has significant quality issues. Consider major revision.")
        elif analysis_result['quality_score'] < 0.7:
            recommendations.append("Document has moderate quality issues. Focus on clarity and conciseness.")
        else:
            recommendations.append("Document quality is good. Minor improvements may enhance readability.")
        
        # Add specific recommendations based on common issues
        issue_types = set()
        for suggestion in analysis_result.get('suggestions', []):
            issue = suggestion.get('issue', '').lower()
            if 'passive voice' in issue:
                issue_types.add('passive_voice')
            elif 'long sentence' in issue:
                issue_types.add('long_sentences')
            elif 'may' in issue:
                issue_types.add('modal_verbs')
        
        if 'passive_voice' in issue_types:
            recommendations.append("Consider converting passive voice to active voice for more engaging writing.")
        if 'long_sentences' in issue_types:
            recommendations.append("Break down long sentences into shorter, more digestible parts.")
        if 'modal_verbs' in issue_types:
            recommendations.append("Review modal verb usage for clarity and directness.")
        
        return recommendations

    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            'is_running': self.is_running,
            'queue_size': self.task_queue.qsize(),
            'cached_results': len(self.results_cache),
            'capabilities': [cap.name for cap in self.capabilities],
            'version': '1.0.0'
        }

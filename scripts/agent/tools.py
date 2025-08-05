"""
Agent Tools - Specialized tools for document processing and AI interactions.
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
import re
from datetime import datetime

from ..app.ai_improvement import get_enhanced_ai_suggestion
from ..app.app import parse_file, analyze_text, analyze_sentence

logger = logging.getLogger(__name__)


class DocumentTools:
    """Tools for document processing and analysis."""
    
    def __init__(self):
        self.supported_formats = ['.txt', '.md', '.docx', '.pdf', '.html', '.adoc']
    
    async def read_document(self, file_path: str) -> Dict[str, Any]:
        """Read and parse a document."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        if path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        try:
            with open(path, 'rb') as file:
                html_content = parse_file(file)
            
            return {
                'file_path': file_path,
                'file_name': path.name,
                'file_size': path.stat().st_size,
                'format': path.suffix,
                'content': html_content,
                'parsed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error reading document {file_path}: {str(e)}")
            raise
    
    async def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure of a document."""
        sentences = analyze_text(content)
        
        # Count different elements
        word_count = len(content.split())
        paragraph_count = content.count('\n\n') + 1
        sentence_count = len(sentences)
        
        # Analyze sentence lengths
        sentence_lengths = [len(s.get('sentence', '').split()) for s in sentences]
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        
        # Count issues by type
        issue_types = {}
        for sentence in sentences:
            for feedback in sentence.get('feedback', []):
                issue_type = self._categorize_issue(feedback.get('message', ''))
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        return {
            'word_count': word_count,
            'paragraph_count': paragraph_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'sentence_lengths': sentence_lengths,
            'issue_types': issue_types,
            'readability_estimate': self._estimate_readability(avg_sentence_length, word_count)
        }
    
    async def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract metadata from a document."""
        path = Path(file_path)
        stat = path.stat()
        
        return {
            'file_name': path.name,
            'file_path': str(path.absolute()),
            'file_size': stat.st_size,
            'file_extension': path.suffix,
            'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'is_readable': os.access(path, os.R_OK),
            'is_writable': os.access(path, os.W_OK)
        }
    
    async def batch_process_directory(self, directory_path: str, 
                                    pattern: str = "*.*") -> List[Dict[str, Any]]:
        """Process all documents in a directory."""
        path = Path(directory_path)
        
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Invalid directory: {directory_path}")
        
        results = []
        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                try:
                    doc_data = await self.read_document(str(file_path))
                    structure = await self.analyze_document_structure(doc_data['content'])
                    metadata = await self.extract_metadata(str(file_path))
                    
                    results.append({
                        'document': doc_data,
                        'structure': structure,
                        'metadata': metadata
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {str(e)}")
                    results.append({
                        'file_path': str(file_path),
                        'error': str(e)
                    })
        
        return results
    
    def _categorize_issue(self, message: str) -> str:
        """Categorize an issue based on its message."""
        message_lower = message.lower()
        
        if 'passive voice' in message_lower:
            return 'passive_voice'
        elif 'long sentence' in message_lower or 'sentence length' in message_lower:
            return 'sentence_length'
        elif 'may' in message_lower and ('possibility' in message_lower or 'permission' in message_lower):
            return 'modal_verbs'
        elif 'backup' in message_lower or 'back up' in message_lower:
            return 'word_usage'
        elif 'repeated' in message_lower:
            return 'repetition'
        elif 'capitalize' in message_lower:
            return 'capitalization'
        else:
            return 'other'
    
    def _estimate_readability(self, avg_sentence_length: float, word_count: int) -> str:
        """Estimate readability based on sentence length."""
        if avg_sentence_length < 15:
            return 'easy'
        elif avg_sentence_length < 20:
            return 'moderate'
        elif avg_sentence_length < 25:
            return 'difficult'
        else:
            return 'very_difficult'


class AITools:
    """Tools for AI-powered analysis and suggestions."""
    
    def __init__(self):
        self.suggestion_cache = {}
        self.model_config = {
            'temperature': 0.01,
            'max_tokens': 150,
            'top_p': 0.3
        }
    
    async def generate_suggestion(self, feedback_text: str, 
                                sentence_context: str = "",
                                document_type: str = "general",
                                writing_goals: List[str] = None) -> Dict[str, Any]:
        """Generate an AI suggestion for a specific issue."""
        cache_key = f"{feedback_text}:{sentence_context}:{document_type}"
        
        if cache_key in self.suggestion_cache:
            logger.info("Using cached suggestion")
            return self.suggestion_cache[cache_key]
        
        try:
            suggestion = get_enhanced_ai_suggestion(
                feedback_text=feedback_text,
                sentence_context=sentence_context,
                document_type=document_type,
                writing_goals=writing_goals or ['clarity', 'conciseness']
            )
            
            # Cache the result
            self.suggestion_cache[cache_key] = suggestion
            
            return suggestion
            
        except Exception as e:
            logger.error(f"Error generating AI suggestion: {str(e)}")
            return {
                'suggestion': 'Unable to generate AI suggestion at this time.',
                'confidence': 'low',
                'method': 'fallback',
                'error': str(e)
            }
    
    async def batch_suggestions(self, issues: List[Dict[str, Any]], 
                              document_type: str = "general") -> List[Dict[str, Any]]:
        """Generate suggestions for multiple issues."""
        suggestions = []
        
        for issue in issues:
            suggestion = await self.generate_suggestion(
                feedback_text=issue.get('message', ''),
                sentence_context=issue.get('sentence', ''),
                document_type=document_type
            )
            
            suggestions.append({
                'issue': issue,
                'suggestion': suggestion
            })
        
        return suggestions
    
    async def summarize_document_issues(self, sentences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize all issues found in a document."""
        all_issues = []
        issue_counts = {}
        
        for sentence in sentences:
            for feedback in sentence.get('feedback', []):
                issue_type = self._categorize_issue_type(feedback.get('message', ''))
                all_issues.append({
                    'sentence_index': sentence.get('sentence_index', 0),
                    'sentence': sentence.get('sentence', ''),
                    'message': feedback.get('message', ''),
                    'type': issue_type
                })
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        # Generate high-level recommendations
        recommendations = self._generate_document_recommendations(issue_counts)
        
        return {
            'total_issues': len(all_issues),
            'issue_breakdown': issue_counts,
            'most_common_issue': max(issue_counts.items(), key=lambda x: x[1])[0] if issue_counts else None,
            'recommendations': recommendations,
            'issues': all_issues
        }
    
    async def analyze_writing_style(self, content: str) -> Dict[str, Any]:
        """Analyze the writing style of a document."""
        sentences = content.split('.')
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        # Calculate style metrics
        avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
        sentence_variety = len(set(sentence_lengths)) / len(sentence_lengths) if sentence_lengths else 0
        
        # Analyze word complexity
        words = content.split()
        complex_words = [w for w in words if len(w) > 6]
        complexity_ratio = len(complex_words) / len(words) if words else 0
        
        # Detect voice patterns
        passive_indicators = ['was', 'were', 'been', 'being', 'is', 'are']
        passive_count = sum(1 for word in words if word.lower() in passive_indicators)
        passive_ratio = passive_count / len(words) if words else 0
        
        return {
            'avg_sentence_length': round(avg_sentence_length, 1),
            'sentence_variety_score': round(sentence_variety, 2),
            'complexity_ratio': round(complexity_ratio, 2),
            'passive_voice_ratio': round(passive_ratio, 2),
            'readability_level': self._assess_readability_level(avg_sentence_length, complexity_ratio),
            'style_recommendations': self._get_style_recommendations(avg_sentence_length, complexity_ratio, passive_ratio)
        }
    
    def _categorize_issue_type(self, message: str) -> str:
        """Categorize an issue type."""
        message_lower = message.lower()
        
        categories = {
            'grammar': ['verb', 'tense', 'subject', 'agreement'],
            'clarity': ['unclear', 'confusing', 'ambiguous', 'vague'],
            'style': ['passive voice', 'tone', 'formality'],
            'structure': ['long sentence', 'run-on', 'fragment'],
            'word_choice': ['may', 'can', 'should', 'backup', 'back up'],
            'formatting': ['capitalize', 'punctuation', 'spacing']
        }
        
        for category, keywords in categories.items():
            if any(keyword in message_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _generate_document_recommendations(self, issue_counts: Dict[str, int]) -> List[str]:
        """Generate high-level recommendations based on issue patterns."""
        recommendations = []
        
        if issue_counts.get('structure', 0) > 5:
            recommendations.append("Focus on breaking down long sentences for better readability.")
        
        if issue_counts.get('style', 0) > 3:
            recommendations.append("Consider revising passive voice constructions for more engaging writing.")
        
        if issue_counts.get('word_choice', 0) > 2:
            recommendations.append("Review word choices for precision and clarity.")
        
        if issue_counts.get('grammar', 0) > 1:
            recommendations.append("Pay attention to grammar and verb usage.")
        
        if not recommendations:
            recommendations.append("Overall document quality is good. Minor improvements may enhance readability.")
        
        return recommendations
    
    def _assess_readability_level(self, avg_sentence_length: float, complexity_ratio: float) -> str:
        """Assess readability level based on metrics."""
        if avg_sentence_length < 15 and complexity_ratio < 0.3:
            return 'easy'
        elif avg_sentence_length < 20 and complexity_ratio < 0.4:
            return 'moderate'
        elif avg_sentence_length < 25 and complexity_ratio < 0.5:
            return 'difficult'
        else:
            return 'very_difficult'
    
    def _get_style_recommendations(self, avg_length: float, complexity: float, passive: float) -> List[str]:
        """Get style-specific recommendations."""
        recommendations = []
        
        if avg_length > 20:
            recommendations.append("Consider shorter sentences for better readability.")
        
        if complexity > 0.4:
            recommendations.append("Simplify complex words where possible.")
        
        if passive > 0.1:
            recommendations.append("Reduce passive voice usage for more direct writing.")
        
        return recommendations


class ValidationTools:
    """Tools for validating document quality and agent results."""
    
    def __init__(self):
        self.quality_thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'fair': 0.5,
            'poor': 0.3
        }
    
    async def validate_document_quality(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of a document analysis."""
        total_sentences = analysis_result.get('total_sentences', 0)
        total_issues = analysis_result.get('total_issues', 0)
        quality_score = analysis_result.get('quality_score', 0)
        
        # Calculate issue density
        issue_density = total_issues / max(total_sentences, 1)
        
        # Determine quality level
        quality_level = 'poor'
        for level, threshold in sorted(self.quality_thresholds.items(), key=lambda x: x[1], reverse=True):
            if quality_score >= threshold:
                quality_level = level
                break
        
        # Validate suggestions
        suggestions = analysis_result.get('suggestions', [])
        suggestion_quality = self._assess_suggestion_quality(suggestions)
        
        return {
            'is_valid': quality_score >= 0.0,
            'quality_level': quality_level,
            'issue_density': round(issue_density, 2),
            'suggestion_coverage': suggestion_quality['coverage'],
            'suggestion_confidence': suggestion_quality['avg_confidence'],
            'validation_notes': self._generate_validation_notes(quality_score, issue_density, suggestion_quality)
        }
    
    async def check_agent_health(self, agent_status: Dict[str, Any]) -> Dict[str, Any]:
        """Check the health of the agent system."""
        checks = {
            'agent_running': agent_status.get('is_running', False),
            'queue_manageable': agent_status.get('queue_size', 0) < 100,
            'cache_reasonable': agent_status.get('cached_results', 0) < 1000,
            'capabilities_available': len(agent_status.get('capabilities', [])) > 0
        }
        
        overall_health = all(checks.values())
        
        return {
            'overall_health': 'healthy' if overall_health else 'unhealthy',
            'checks': checks,
            'recommendations': self._get_health_recommendations(checks)
        }
    
    def _assess_suggestion_quality(self, suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess the quality of AI suggestions."""
        if not suggestions:
            return {'coverage': 0, 'avg_confidence': 0}
        
        # Count suggestions with high confidence
        high_confidence = sum(1 for s in suggestions if s.get('confidence') == 'high')
        coverage = high_confidence / len(suggestions)
        
        # Calculate average confidence (convert to numeric)
        confidence_values = []
        for s in suggestions:
            conf = s.get('confidence', 'low')
            if conf == 'high':
                confidence_values.append(0.8)
            elif conf == 'medium':
                confidence_values.append(0.6)
            else:
                confidence_values.append(0.3)
        
        avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
        
        return {
            'coverage': round(coverage, 2),
            'avg_confidence': round(avg_confidence, 2)
        }
    
    def _generate_validation_notes(self, quality_score: float, issue_density: float, 
                                 suggestion_quality: Dict[str, Any]) -> List[str]:
        """Generate validation notes."""
        notes = []
        
        if quality_score < 0.5:
            notes.append("Document requires significant improvement.")
        
        if issue_density > 0.5:
            notes.append("High issue density detected - consider major revision.")
        
        if suggestion_quality['coverage'] < 0.5:
            notes.append("Low suggestion coverage - manual review recommended.")
        
        if suggestion_quality['avg_confidence'] < 0.5:
            notes.append("Low suggestion confidence - results may need verification.")
        
        if not notes:
            notes.append("Validation passed - results appear reliable.")
        
        return notes
    
    def _get_health_recommendations(self, checks: Dict[str, bool]) -> List[str]:
        """Get health recommendations based on checks."""
        recommendations = []
        
        if not checks['agent_running']:
            recommendations.append("Agent is not running - restart required.")
        
        if not checks['queue_manageable']:
            recommendations.append("Task queue is too large - consider processing or clearing.")
        
        if not checks['cache_reasonable']:
            recommendations.append("Result cache is too large - consider clearing old results.")
        
        if not checks['capabilities_available']:
            recommendations.append("No capabilities available - check agent configuration.")
        
        return recommendations

"""
Chunk Factory - Generate knowledge base chunks programmatically.

This package converts your rules, examples, and patterns into 
properly structured DecisionChunks for the RAG system.
"""

from .rule_chunks import generate_rule_chunks
from .example_chunks import generate_example_chunks  
from .exception_chunks import generate_exception_chunks
from .pattern_chunks import generate_pattern_chunks

__all__ = [
    'generate_rule_chunks',
    'generate_example_chunks',
    'exception_chunks',
    'generate_pattern_chunks',
]

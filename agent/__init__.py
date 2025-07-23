"""
Document Review Agent Framework
A powerful agent system for automated document analysis and review.
"""

from .agent import DocumentReviewAgent
from .mcp_server import MCPServer
from .tools import DocumentTools, AITools, ValidationTools

__version__ = "1.0.0"
__all__ = ["DocumentReviewAgent", "MCPServer", "DocumentTools", "AITools", "ValidationTools"]

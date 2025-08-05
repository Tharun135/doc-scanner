"""
Agent Protocol Definitions
Defines the interface and data structures for the document review agent.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentCapability:
    """Represents a capability of the agent."""
    name: str
    description: str
    parameters: Dict[str, Any]


@dataclass
class TaskResult:
    """Represents the result of a task execution."""
    success: bool
    execution_time: float
    agent_id: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentProtocol(ABC):
    """
    Abstract base class for document review agents.
    Defines the interface that all agents must implement.
    """
    
    @property
    @abstractmethod
    def capabilities(self) -> List[AgentCapability]:
        """Return the agent's capabilities."""
        pass
    
    @abstractmethod
    async def start(self):
        """Start the agent."""
        pass
    
    @abstractmethod
    async def stop(self):
        """Stop the agent."""
        pass
    
    @abstractmethod
    async def execute_task(self, task_type: str, parameters: Dict[str, Any]) -> TaskResult:
        """Execute a specific task."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        pass


@dataclass
class AgentMessage:
    """Represents a message in the agent communication protocol."""
    id: str
    type: str  # request, response, notification, error
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AgentCommunicationProtocol:
    """
    Handles communication between the agent and external systems.
    Supports JSON-RPC style messaging.
    """
    
    def __init__(self):
        self.message_handlers = {}
    
    def register_handler(self, method: str, handler):
        """Register a message handler for a specific method."""
        self.message_handlers[method] = handler
    
    async def handle_message(self, message: AgentMessage) -> AgentMessage:
        """Handle an incoming message."""
        if message.type == "request":
            return await self._handle_request(message)
        elif message.type == "notification":
            await self._handle_notification(message)
            return None
        else:
            return self._create_error_response(
                message.id, 
                -32600, 
                "Invalid Request"
            )
    
    async def _handle_request(self, message: AgentMessage) -> AgentMessage:
        """Handle a request message."""
        method = message.method
        params = message.params or {}
        
        if method not in self.message_handlers:
            return self._create_error_response(
                message.id,
                -32601,
                f"Method not found: {method}"
            )
        
        try:
            handler = self.message_handlers[method]
            result = await handler(params)
            
            return AgentMessage(
                id=message.id,
                type="response",
                result=result
            )
            
        except Exception as e:
            return self._create_error_response(
                message.id,
                -32603,
                f"Internal error: {str(e)}"
            )
    
    async def _handle_notification(self, message: AgentMessage):
        """Handle a notification message."""
        method = message.method
        params = message.params or {}
        
        if method in self.message_handlers:
            try:
                handler = self.message_handlers[method]
                await handler(params)
            except Exception as e:
                # Notifications don't return errors, just log them
                print(f"Error handling notification {method}: {str(e)}")
    
    def _create_error_response(self, message_id: str, code: int, message: str) -> AgentMessage:
        """Create an error response message."""
        return AgentMessage(
            id=message_id,
            type="error",
            error={
                "code": code,
                "message": message
            }
        )

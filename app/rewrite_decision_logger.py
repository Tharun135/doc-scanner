"""
Rewrite Decision Capture System

Logs every rewrite decision with full context for later mining.
This is the PRIMARY data source for chunk generation.

Every time DocScanner analyzes a sentence, log:
- The sentence (with surrounding context)
- What rule triggered
- Whether rewrite was suggested
- User acceptance/rejection
- The actual rewrite (if any)
- Confidence score
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Type of decision made."""
    REWRITE_SUGGESTED = "rewrite_suggested"
    REWRITE_ACCEPTED = "rewrite_accepted"
    REWRITE_REJECTED = "rewrite_rejected"
    NO_REWRITE = "no_rewrite"
    REWRITE_SKIPPED = "rewrite_skipped"  # User ignored suggestion


class ConfidenceLevel(Enum):
    """Confidence in the rewrite decision."""
    HIGH = "high"        # Clear rule violation, obvious fix
    MEDIUM = "medium"    # Rule applies but context matters
    LOW = "low"          # Borderline case
    UNCERTAIN = "uncertain"  # Rule triggered but shouldn't have


@dataclass
class RewriteDecision:
    """
    A single rewrite decision with full context.
    
    This is the GOLD STANDARD data for chunk generation.
    Every field here becomes training signal.
    """
    
    # Identifiers
    id: str
    timestamp: str
    document_id: str
    document_type: str  # "manual", "api", "ui", etc.
    
    # The sentence and context
    sentence: str
    sentence_before: str  # Previous sentence for context
    sentence_after: str   # Next sentence for context
    paragraph: str        # Full paragraph
    
    # Rule that triggered
    rule_id: str
    rule_name: str
    severity: str
    
    # The decision
    decision_type: str  # DecisionType
    suggested_rewrite: Optional[str]
    actual_rewrite: Optional[str]  # What user actually did
    
    # Why this decision was made
    justification: str
    confidence: str  # ConfidenceLevel
    
    # User interaction
    user_accepted: Optional[bool]
    user_rejection_reason: Optional[str]
    time_to_decision_ms: Optional[int]
    
    # Metadata for filtering
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RewriteDecision':
        """Load from dictionary."""
        return cls(**data)


class RewriteHistoryLogger:
    """
    Logs rewrite decisions to JSONL file for later mining.
    
    Integration point: Call this from your main app when suggestions are made.
    """
    
    def __init__(self, log_file: str = "data/rewrite_history.jsonl"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Also maintain in-memory buffer for batch operations
        self.buffer: List[RewriteDecision] = []
        self.buffer_size = 100
    
    def log_decision(self, decision: RewriteDecision):
        """
        Log a single rewrite decision.
        
        Call this from DocScanner whenever a sentence is analyzed.
        """
        # Append to JSONL file
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(decision.to_dict()) + '\n')
        
        # Add to buffer
        self.buffer.append(decision)
        
        # Flush buffer if full
        if len(self.buffer) >= self.buffer_size:
            self.flush_buffer()
    
    def flush_buffer(self):
        """Flush in-memory buffer."""
        logger.info(f"Flushed {len(self.buffer)} decisions to history")
        self.buffer.clear()
    
    def load_history(self, limit: Optional[int] = None) -> List[RewriteDecision]:
        """
        Load all logged decisions.
        
        Use this to mine chunks from history.
        """
        decisions = []
        responses = {}  # Map decision_id to response
        
        if not self.log_file.exists():
            logger.warning(f"History file not found: {self.log_file}")
            return decisions
        
        with open(self.log_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if limit and i >= limit:
                    break
                
                try:
                    data = json.loads(line)
                    
                    # Check if this is a user response or a decision
                    if data.get('type') == 'user_response':
                        # Store response for later merging
                        decision_id = data.get('decision_id')
                        responses[decision_id] = data
                    else:
                        # This is a decision
                        decisions.append(RewriteDecision.from_dict(data))
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse line {i}: {e}")
                except TypeError as e:
                    # Skip malformed entries
                    logger.debug(f"Skipped malformed entry at line {i}: {e}")
        
        # Merge responses into decisions
        for decision in decisions:
            if decision.id in responses:
                response = responses[decision.id]
                decision.user_accepted = response.get('accepted')
                decision.actual_rewrite = response.get('actual_rewrite')
                decision.user_rejection_reason = response.get('rejection_reason')
                decision.time_to_decision_ms = response.get('time_to_decision_ms')
        
        logger.info(f"Loaded {len(decisions)} decisions from history")
        return decisions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about logged decisions."""
        decisions = self.load_history()
        
        if not decisions:
            return {}
        
        stats = {
            "total_decisions": len(decisions),
            "by_decision_type": {},
            "by_rule": {},
            "by_confidence": {},
            "acceptance_rate": 0,
            "rejection_rate": 0,
            "avg_time_to_decision_ms": 0
        }
        
        accepted = 0
        rejected = 0
        total_time = 0
        time_count = 0
        
        for d in decisions:
            # By decision type
            dt = d.decision_type
            stats["by_decision_type"][dt] = stats["by_decision_type"].get(dt, 0) + 1
            
            # By rule
            rule = d.rule_id
            stats["by_rule"][rule] = stats["by_rule"].get(rule, 0) + 1
            
            # By confidence
            conf = d.confidence
            stats["by_confidence"][conf] = stats["by_confidence"].get(conf, 0) + 1
            
            # Acceptance/rejection
            if d.user_accepted is True:
                accepted += 1
            elif d.user_accepted is False:
                rejected += 1
            
            # Time to decision
            if d.time_to_decision_ms:
                total_time += d.time_to_decision_ms
                time_count += 1
        
        total = len(decisions)
        stats["acceptance_rate"] = accepted / total if total > 0 else 0
        stats["rejection_rate"] = rejected / total if total > 0 else 0
        stats["avg_time_to_decision_ms"] = total_time / time_count if time_count > 0 else 0
        
        return stats


# Integration helper functions
def capture_rewrite_suggestion(
    sentence: str,
    rule_id: str,
    rule_name: str,
    suggested_rewrite: str,
    justification: str,
    confidence: str,
    document_context: Dict[str, Any]
) -> RewriteDecision:
    """
    Capture a rewrite suggestion.
    
    Call this when DocScanner suggests a rewrite.
    
    Example:
        decision = capture_rewrite_suggestion(
            sentence="The document was reviewed by the team.",
            rule_id="PASSIVE_VOICE",
            rule_name="Passive Voice",
            suggested_rewrite="The team reviewed the document.",
            justification="Passive voice obscures the actor.",
            confidence="high",
            document_context={...}
        )
        logger.log_decision(decision)
    """
    return RewriteDecision(
        id=_generate_id(),
        timestamp=datetime.now().isoformat(),
        document_id=document_context.get("doc_id", "unknown"),
        document_type=document_context.get("doc_type", "manual"),
        sentence=sentence,
        sentence_before=document_context.get("sentence_before", ""),
        sentence_after=document_context.get("sentence_after", ""),
        paragraph=document_context.get("paragraph", ""),
        rule_id=rule_id,
        rule_name=rule_name,
        severity=document_context.get("severity", "medium"),
        decision_type=DecisionType.REWRITE_SUGGESTED.value,
        suggested_rewrite=suggested_rewrite,
        actual_rewrite=None,  # Will be filled when user acts
        justification=justification,
        confidence=confidence,
        user_accepted=None,  # Will be filled when user responds
        user_rejection_reason=None,
        time_to_decision_ms=None,
        metadata=document_context.get("metadata", {})
    )


def capture_user_response(
    decision_id: str,
    accepted: bool,
    actual_rewrite: Optional[str] = None,
    rejection_reason: Optional[str] = None,
    time_to_decision_ms: Optional[int] = None
):
    """
    Update a decision with user response.
    
    Call this when user accepts/rejects a suggestion.
    
    This requires updating the JSONL file, which is append-only.
    Instead, log a new "response" entry that references the original decision.
    """
    response = {
        "type": "user_response",
        "decision_id": decision_id,
        "accepted": accepted,
        "actual_rewrite": actual_rewrite,
        "rejection_reason": rejection_reason,
        "time_to_decision_ms": time_to_decision_ms,
        "timestamp": datetime.now().isoformat()
    }
    
    # Append response to history
    log_file = Path("data/rewrite_history.jsonl")
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(response) + '\n')


def _generate_id() -> str:
    """Generate unique ID for decision."""
    from hashlib import md5
    from uuid import uuid4
    return md5(str(uuid4()).encode()).hexdigest()[:16]


# Global instance
_history_logger = None

def get_history_logger() -> RewriteHistoryLogger:
    """Get global history logger instance."""
    global _history_logger
    if _history_logger is None:
        _history_logger = RewriteHistoryLogger()
    return _history_logger


if __name__ == "__main__":
    # Test the logging system
    logger = get_history_logger()
    
    # Simulate some decisions
    decision = capture_rewrite_suggestion(
        sentence="The document was reviewed by the team.",
        rule_id="PASSIVE_VOICE",
        rule_name="Passive Voice",
        suggested_rewrite="The team reviewed the document.",
        justification="Passive voice obscures the actor. Active voice is clearer.",
        confidence="high",
        document_context={
            "doc_id": "test_doc_001",
            "doc_type": "manual",
            "sentence_before": "This is the context before.",
            "sentence_after": "This is the context after.",
            "paragraph": "This is the context before. The document was reviewed by the team. This is the context after.",
            "severity": "medium"
        }
    )
    
    logger.log_decision(decision)
    
    # Simulate user acceptance
    capture_user_response(
        decision_id=decision.id,
        accepted=True,
        actual_rewrite="The team reviewed the document.",
        time_to_decision_ms=2500
    )
    
    # Show statistics
    stats = logger.get_statistics()
    print(json.dumps(stats, indent=2))

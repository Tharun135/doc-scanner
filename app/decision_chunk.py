"""
Decision Chunk Schema - The core building block for DocScanner RAG system.

Every chunk MUST be able to answer its question field independently.
Every chunk MUST have clear metadata indicating its purpose and constraints.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Literal, Dict, Any
from datetime import datetime
import hashlib
import re


@dataclass
class DecisionChunk:
    """
    A decision unit for the RAG knowledge base.
    
    Each chunk represents a single, answerable question about writing rules,
    patterns, or decisions. Chunks are the atomic units of retrieval.
    
    Design principles:
    1. Single question per chunk
    2. Complete answer within chunk
    3. Clear metadata for filtering
    4. Explicit rewrite permissions
    """
    
    # Core identifiers
    id: str
    title: str
    
    # The decision question this chunk answers
    question: str
    
    # The complete answer (must be self-contained)
    answer: str
    
    # Classification
    knowledge_type: Literal["rule", "example", "exception", "pattern", "negative"]
    
    # Rule association (if applicable)
    rule_id: Optional[str] = None
    
    # Critical decision flags
    rewrite_allowed: bool = True
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    
    # Document context
    doc_type: Literal["manual", "api", "safety", "ui", "legal", "pattern", "rewrite_history"] = "manual"
    
    # Metadata for enrichment
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Automatic timestamps
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Validate chunk after creation."""
        # Validate required fields are not empty
        if not self.question or not self.question.strip():
            raise ValueError(f"Chunk {self.id}: question cannot be empty")
        
        if not self.answer or not self.answer.strip():
            raise ValueError(f"Chunk {self.id}: answer cannot be empty")
        
        # Validate answer length (must be concise)
        word_count = len(self.answer.split())
        if word_count > 200:
            raise ValueError(
                f"Chunk {self.id}: answer too long ({word_count} words). "
                f"Maximum 200 words. Split into multiple chunks."
            )
        
        # Validate title
        if not self.title or not self.title.strip():
            raise ValueError(f"Chunk {self.id}: title cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/embedding."""
        return asdict(self)
    
    def get_embedding_text(self) -> str:
        """
        Get the text to embed for semantic search.
        Combines question and answer for optimal retrieval.
        """
        return f"{self.question}\n\n{self.answer}"
    
    def get_token_count(self) -> int:
        """Approximate token count (rough estimate: 1 token ≈ 4 chars)."""
        text = self.get_embedding_text()
        return len(text) // 4
    
    def get_metadata_for_filtering(self) -> Dict[str, Any]:
        """Get metadata suitable for filtering during retrieval. ChromaDB requires no None values."""
        metadata = {
            "knowledge_type": self.knowledge_type,
            "rewrite_allowed": self.rewrite_allowed,
            "severity": self.severity,
            "doc_type": self.doc_type,
        }
        
        # Only include rule_id if it's not None (ChromaDB doesn't accept None)
        if self.rule_id is not None:
            metadata["rule_id"] = self.rule_id
            
        return metadata
    
    @staticmethod
    def generate_id(title: str, question: str) -> str:
        """Generate a deterministic ID from title and question."""
        content = f"{title}|{question}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    @classmethod
    def create(cls, title: str, question: str, answer: str, 
               knowledge_type: str, **kwargs) -> 'DecisionChunk':
        """
        Factory method to create a DecisionChunk with automatic ID generation.
        
        Example:
            chunk = DecisionChunk.create(
                title="Passive voice definition",
                question="When is a sentence considered passive voice?",
                answer="A sentence is passive when the subject receives...",
                knowledge_type="rule",
                rule_id="PASSIVE_VOICE",
                severity="medium"
            )
        """
        chunk_id = cls.generate_id(title, question)
        return cls(
            id=chunk_id,
            title=title,
            question=question,
            answer=answer,
            knowledge_type=knowledge_type,
            **kwargs
        )


def validate_chunk_collection(chunks: list[DecisionChunk]) -> tuple[bool, list[str]]:
    """
    Validate a collection of chunks before indexing.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # Check for duplicate IDs
    ids = [chunk.id for chunk in chunks]
    duplicates = [id for id in ids if ids.count(id) > 1]
    if duplicates:
        errors.append(f"Duplicate chunk IDs found: {set(duplicates)}")
    
    # Check for duplicate questions (potential redundancy)
    questions = [chunk.question for chunk in chunks]
    dup_questions = [q for q in questions if questions.count(q) > 1]
    if dup_questions:
        errors.append(f"Duplicate questions found: {set(dup_questions)}")
    
    # Validate each chunk
    for i, chunk in enumerate(chunks):
        try:
            # Post-init validation already ran, but double-check
            assert chunk.question.strip(), f"Empty question at index {i}"
            assert chunk.answer.strip(), f"Empty answer at index {i}"
            assert chunk.get_token_count() < 300, f"Chunk {chunk.id} exceeds token limit"
        except AssertionError as e:
            errors.append(str(e))
    
    return len(errors) == 0, errors


# Pre-defined templates for common chunk patterns
class ChunkTemplates:
    """Common templates for generating consistent chunks."""
    
    @staticmethod
    def rule_definition(rule_id: str, rule_name: str, definition: str) -> DecisionChunk:
        """Template for rule definition chunks."""
        return DecisionChunk.create(
            title=f"{rule_name} - Definition",
            question=f"What is the {rule_name.lower()} rule?",
            answer=definition,
            knowledge_type="rule",
            rule_id=rule_id,
            doc_type="manual"
        )
    
    @staticmethod
    def rule_why_matters(rule_id: str, rule_name: str, reason: str, severity: str = "medium") -> DecisionChunk:
        """Template for explaining why a rule matters."""
        return DecisionChunk.create(
            title=f"{rule_name} - Importance",
            question=f"Why does the {rule_name.lower()} rule matter?",
            answer=reason,
            knowledge_type="rule",
            rule_id=rule_id,
            severity=severity,
            doc_type="manual"
        )
    
    @staticmethod
    def rule_exception(rule_id: str, rule_name: str, exception_case: str) -> DecisionChunk:
        """Template for rule exceptions."""
        return DecisionChunk.create(
            title=f"{rule_name} - Exception",
            question=f"When should the {rule_name.lower()} rule NOT be applied?",
            answer=exception_case,
            knowledge_type="exception",
            rule_id=rule_id,
            doc_type="manual"
        )
    
    @staticmethod
    def rewrite_example(rule_id: str, before: str, after: str, explanation: str) -> DecisionChunk:
        """Template for rewrite examples."""
        answer = f"Before: {before}\n\nAfter: {after}\n\nWhy: {explanation}"
        return DecisionChunk.create(
            title=f"{rule_id} - Rewrite Example",
            question=f"How should text violating {rule_id} be rewritten?",
            answer=answer,
            knowledge_type="example",
            rule_id=rule_id,
            rewrite_allowed=True,
            doc_type="rewrite_history"
        )
    
    @staticmethod
    def negative_knowledge(context: str, forbidden_action: str, reason: str, 
                          doc_type: str = "ui", severity: str = "high") -> DecisionChunk:
        """Template for negative knowledge (what NOT to do)."""
        return DecisionChunk.create(
            title=f"Do NOT rewrite: {context}",
            question=f"Should {context} be rewritten?",
            answer=f"NO. {reason}",
            knowledge_type="negative",
            rewrite_allowed=False,
            severity=severity,
            doc_type=doc_type
        )

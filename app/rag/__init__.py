"""
app/rag/__init__.py
Exposes the public API of the corrected RAG pipeline.
"""

from app.rag.rule_vectorstore import get_rule_vectorstore, RuleVectorStore
from app.rag.sentence_reviewer import (
    review_sentence,
    review_document_sentences,
    classify_sentence,
    retrieve_and_rerank,
)

__all__ = [
    "get_rule_vectorstore",
    "RuleVectorStore",
    "review_sentence",
    "review_document_sentences",
    "classify_sentence",
    "retrieve_and_rerank",
]

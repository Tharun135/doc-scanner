"""
Example Chunk Generator - Mine rewrite history for example chunks.

Converts actual rewrites into learning examples:
1. Bad example chunk (before rewrite)
2. Corrected example chunk (after rewrite)
3. Justification chunk (why changed)

Target: 100 rewrites × 3 = 300 chunks
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.decision_chunk import DecisionChunk
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


# Example rewrite history (would be loaded from logs/database)
REWRITE_EXAMPLES = [
    {
        "id": "rewrite_001",
        "rule_id": "PASSIVE_VOICE",
        "before": "The document was reviewed by the team.",
        "after": "The team reviewed the document.",
        "justification": "Converted from passive to active voice to identify the actor and make the sentence more direct.",
        "context": "Technical documentation",
        "timestamp": "2025-01-10T10:30:00"
    },
    {
        "id": "rewrite_002",
        "rule_id": "LONG_SENTENCES",
        "before": "The system processes incoming requests by first validating the user credentials, then checking the request parameters against the schema, and finally forwarding the validated request to the appropriate handler for processing.",
        "after": "The system processes incoming requests in three steps. First, it validates user credentials. Next, it checks request parameters against the schema. Finally, it forwards the validated request to the appropriate handler.",
        "justification": "Broke long 42-word sentence into 4 shorter sentences to improve readability and comprehension.",
        "context": "API documentation",
        "timestamp": "2025-01-10T11:15:00"
    },
    {
        "id": "rewrite_003",
        "rule_id": "ADVERBS",
        "before": "The application runs very quickly on modern hardware.",
        "after": "The application runs fast on modern hardware.",
        "justification": "Removed unnecessary 'very' - the word 'quickly' already conveys speed, and 'fast' is more direct.",
        "context": "Product description",
        "timestamp": "2025-01-10T14:20:00"
    },
    {
        "id": "rewrite_004",
        "rule_id": "NOMINALIZATIONS",
        "before": "The implementation of the new feature requires validation of user input.",
        "after": "Implementing the new feature requires validating user input.",
        "justification": "Converted nominalizations 'implementation' and 'validation' to verb forms for more direct writing.",
        "context": "Technical specification",
        "timestamp": "2025-01-11T09:00:00"
    },
    {
        "id": "rewrite_005",
        "rule_id": "VAGUE_TERMS",
        "before": "The system handles various types of requests.",
        "after": "The system handles GET, POST, PUT, and DELETE requests.",
        "justification": "Replaced vague 'various types' with specific request types for clarity.",
        "context": "API documentation",
        "timestamp": "2025-01-11T10:30:00"
    },
    {
        "id": "rewrite_006",
        "rule_id": "VERY",
        "before": "This is a very important security consideration.",
        "after": "This is a critical security consideration.",
        "justification": "Replaced 'very important' with more precise word 'critical'.",
        "context": "Security documentation",
        "timestamp": "2025-01-11T11:45:00"
    },
    {
        "id": "rewrite_007",
        "rule_id": "PASSIVE_VOICE",
        "before": "Errors are logged by the monitoring system.",
        "after": "The monitoring system logs errors.",
        "justification": "Active voice clearly identifies what performs the action.",
        "context": "System documentation",
        "timestamp": "2025-01-12T08:15:00"
    },
    {
        "id": "rewrite_008",
        "rule_id": "READABILITY",
        "before": "Utilize the functionality to accomplish the task.",
        "after": "Use the feature to complete the task.",
        "justification": "Replaced complex words with simpler alternatives: 'utilize'→'use', 'functionality'→'feature', 'accomplish'→'complete'.",
        "context": "User guide",
        "timestamp": "2025-01-12T09:30:00"
    },
    {
        "id": "rewrite_009",
        "rule_id": "CONSISTENCY",
        "before": "Click the button. Press the control to continue. Hit the switch to finalize.",
        "after": "Click the button. Click the button to continue. Click the button to finalize.",
        "justification": "Used consistent terminology 'button' throughout instead of mixing 'button', 'control', 'switch'.",
        "context": "UI documentation",
        "timestamp": "2025-01-12T13:00:00"
    },
    {
        "id": "rewrite_010",
        "rule_id": "VERB_TENSE",
        "before": "The user clicks the button and the system displayed the result.",
        "after": "The user clicks the button and the system displays the result.",
        "justification": "Maintained consistent present tense throughout the sentence.",
        "context": "Process description",
        "timestamp": "2025-01-13T10:00:00"
    },
]


def generate_example_chunks() -> List[DecisionChunk]:
    """
    Generate example chunks from rewrite history.
    
    For each rewrite, generates 3 chunks:
    1. Bad example (before)
    2. Corrected example (after)
    3. Justification (why)
    
    Returns:
        List of DecisionChunks (target: 300+ from 100+ rewrites)
    """
    chunks = []
    
    for rewrite in REWRITE_EXAMPLES:
        rule_id = rewrite["rule_id"]
        rewrite_id = rewrite["id"]
        
        # 1. Bad example chunk
        chunks.append(DecisionChunk.create(
            title=f"Bad Example: {rule_id}",
            question=f"What is wrong with this sentence: '{rewrite['before']}'?",
            answer=f"This sentence violates the {rule_id} rule. {rewrite['justification']}",
            knowledge_type="example",
            rule_id=rule_id,
            rewrite_allowed=True,
            severity="medium",
            doc_type="rewrite_history",
            metadata={
                "rewrite_id": rewrite_id,
                "example_type": "bad",
                "context": rewrite.get("context", "unknown"),
                "timestamp": rewrite.get("timestamp", "")
            }
        ))
        
        # 2. Corrected example chunk
        chunks.append(DecisionChunk.create(
            title=f"Corrected Example: {rule_id}",
            question=f"How should this be written correctly: '{rewrite['before']}'?",
            answer=f"Correct version: '{rewrite['after']}'. {rewrite['justification']}",
            knowledge_type="example",
            rule_id=rule_id,
            rewrite_allowed=True,
            severity="medium",
            doc_type="rewrite_history",
            metadata={
                "rewrite_id": rewrite_id,
                "example_type": "corrected",
                "context": rewrite.get("context", "unknown"),
                "timestamp": rewrite.get("timestamp", "")
            }
        ))
        
        # 3. Justification chunk
        chunks.append(DecisionChunk.create(
            title=f"Why Rewrite: {rule_id}",
            question=f"Why was '{rewrite['before']}' rewritten to '{rewrite['after']}'?",
            answer=rewrite['justification'],
            knowledge_type="example",
            rule_id=rule_id,
            rewrite_allowed=True,
            severity="medium",
            doc_type="rewrite_history",
            metadata={
                "rewrite_id": rewrite_id,
                "example_type": "justification",
                "context": rewrite.get("context", "unknown"),
                "timestamp": rewrite.get("timestamp", "")
            }
        ))
    
    print(f"✅ Generated {len(chunks)} example chunks from {len(REWRITE_EXAMPLES)} rewrites")
    return chunks


def load_rewrites_from_log(log_file: str) -> List[Dict[str, Any]]:
    """
    Load rewrite history from a JSON log file.
    
    Expected format:
    [
        {
            "id": "...",
            "rule_id": "...",
            "before": "...",
            "after": "...",
            "justification": "...",
            "context": "...",
            "timestamp": "..."
        },
        ...
    ]
    """
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Rewrite log file not found: {log_file}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in rewrite log: {e}")
        return []


def generate_chunks_from_log(log_file: str) -> List[DecisionChunk]:
    """
    Generate example chunks from a rewrite log file.
    
    Use this to process your actual rewrite history.
    """
    rewrites = load_rewrites_from_log(log_file)
    if not rewrites:
        logger.warning("No rewrites loaded from log file")
        return []
    
    # Temporarily replace global REWRITE_EXAMPLES
    global REWRITE_EXAMPLES
    original = REWRITE_EXAMPLES
    REWRITE_EXAMPLES = rewrites
    
    try:
        chunks = generate_example_chunks()
        return chunks
    finally:
        REWRITE_EXAMPLES = original


def add_manual_example(rule_id: str, before: str, after: str, 
                       justification: str, context: str = "manual") -> List[DecisionChunk]:
    """
    Manually add a rewrite example and generate its chunks.
    
    Use this to add one-off examples without logging to file.
    """
    rewrite_id = f"manual_{len(REWRITE_EXAMPLES) + 1:03d}"
    example = {
        "id": rewrite_id,
        "rule_id": rule_id,
        "before": before,
        "after": after,
        "justification": justification,
        "context": context,
        "timestamp": ""
    }
    
    REWRITE_EXAMPLES.append(example)
    
    # Generate chunks just for this example
    chunks = []
    
    chunks.append(DecisionChunk.create(
        title=f"Bad Example: {rule_id}",
        question=f"What is wrong with this sentence: '{before}'?",
        answer=f"This sentence violates the {rule_id} rule. {justification}",
        knowledge_type="example",
        rule_id=rule_id,
        doc_type="rewrite_history"
    ))
    
    chunks.append(DecisionChunk.create(
        title=f"Corrected Example: {rule_id}",
        question=f"How should this be written correctly: '{before}'?",
        answer=f"Correct version: '{after}'. {justification}",
        knowledge_type="example",
        rule_id=rule_id,
        doc_type="rewrite_history"
    ))
    
    chunks.append(DecisionChunk.create(
        title=f"Why Rewrite: {rule_id}",
        question=f"Why was '{before}' rewritten to '{after}'?",
        answer=justification,
        knowledge_type="example",
        rule_id=rule_id,
        doc_type="rewrite_history"
    ))
    
    return chunks


if __name__ == "__main__":
    # Test generation
    chunks = generate_example_chunks()
    print(f"\n📊 Statistics:")
    print(f"   Total chunks: {len(chunks)}")
    print(f"   Average token count: {sum(c.get_token_count() for c in chunks) / len(chunks):.1f}")
    print(f"   Knowledge types: {set(c.knowledge_type for c in chunks)}")
    print(f"   Example types: {set(c.metadata.get('example_type', 'unknown') for c in chunks)}")
    print(f"\n✅ Example chunk generation successful!")

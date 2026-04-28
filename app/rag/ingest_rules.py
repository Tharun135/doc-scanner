"""
ingest_rules.py
================
One-time (and idempotent) script to populate the ChromaDB rule vector store.

Run this after installing dependencies:
    python -m app.rag.ingest_rules

Or call `ingest_style_rules()` programmatically from app startup.
"""

import logging
import sys
import os

# Allow running as a standalone script from the project root
_PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ingest_rules")


def ingest_style_rules(force: bool = False) -> int:
    """
    Populate the ChromaDB rule vector store from rules.json.

    Args:
        force: If True, deletes and re-ingests all rules.

    Returns:
        Number of rules now in the store.
    """
    from app.rag.rule_vectorstore import get_rule_vectorstore

    store = get_rule_vectorstore()

    if not store.is_ready():
        logger.error("Rule vector store is not ready. Check ChromaDB installation.")
        return 0

    count_before = store.count()
    logger.info(f"Rules in store before ingestion: {count_before}")

    ingested = store.ingest_rules(force_reingest=force)

    logger.info(f"✅ Rule store now contains {ingested} rules.")
    return ingested


def verify_retrieval():
    """Quick smoke-test: retrieve rules for a few known-bad sentences."""
    from app.rag.rule_vectorstore import get_rule_vectorstore

    store = get_rule_vectorstore()

    test_cases = [
        ("The configuration should be updated by the user.", ["PASSIVE"]),
        ("Click on the Save button.", ["UI_001", "UI_002"]),
        ("Don't close the window.", ["CONTRACTION_001"]),
        ("The system shall start automatically.", ["TENSE_001"]),
        ("You may click Save.", ["TENSE_002"]),
        ("Simply configure the settings.", ["ADV_001"]),
        ("I will configure the system.", ["PERSON_001"]),
    ]

    print("\n--- Retrieval Smoke Test ---")
    for sentence, expected_rules in test_cases:
        results = store.retrieve_rules(sentence, top_k=3)
        found = [r["rule_id"] for r in results]
        scores = [round(r["score"], 3) for r in results]
        top_hit = found[0] if found else "None"
        print(f"\n  Sentence: \"{sentence}\"")
        print(f"  Retrieved: {found} | Scores: {scores}")
        hits = [e for e in expected_rules if e in " ".join(found)]
        print(f"  {'✅' if hits else '⚠️ '} Expected {expected_rules}, top hit: {top_hit}")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest style rules into ChromaDB")
    parser.add_argument("--force", action="store_true", help="Force re-ingestion (deletes existing rules)")
    parser.add_argument("--verify", action="store_true", help="Run retrieval smoke test after ingestion")
    args = parser.parse_args()

    count = ingest_style_rules(force=args.force)

    if args.verify and count > 0:
        verify_retrieval()

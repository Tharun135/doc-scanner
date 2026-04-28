"""
rule_vectorstore.py
====================
Ingests STYLE RULES (not document text) into ChromaDB.

This is the corrected RAG knowledge-base design for DocScanner.
The vector store holds rules, not document chunks.
Each record = one style rule, embedded as its description + examples.

When a sentence triggers a flag, we query this store to retrieve
the most relevant rules. The LLM then evaluates the sentence specifically
against those rules — giving structured, rule-grounded feedback.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional deps — fail gracefully so Flask still starts
# ---------------------------------------------------------------------------
try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("[RuleVectorStore] chromadb not installed — rule retrieval disabled")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("[RuleVectorStore] sentence_transformers not installed — falling back to ChromaDB default embedding")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(__file__)
_RULES_JSON = os.path.normpath(os.path.join(_THIS_DIR, "..", "rules", "rules.json"))
_DB_PATH = os.path.normpath(os.path.join(_THIS_DIR, "..", "..", "docscanner_rules_db"))
_COLLECTION_NAME = "style_rules_v2"

# ---------------------------------------------------------------------------
# Extended rule definitions (these supplement rules.json with richer text)
# ---------------------------------------------------------------------------

# These map rule_id → embeddable text that captures the rule's semantic intent.
# The embedding text should be rich enough that a sentence matching the pattern
# surfaces this rule via cosine similarity.
RULE_EMBED_TEMPLATES = {
    "TENSE_001": (
        "Avoid future tense constructions 'going to' and 'shall' in technical procedures. "
        "Use simple present or 'will' for system actions instead. "
        "Bad: 'The system shall start automatically.' "
        "Good: 'The system starts automatically.'"
    ),
    "TENSE_002": (
        "Modal verbs like may, could, might, should, would weaken procedural clarity. "
        "Use 'can' for user abilities or imperative present tense for direct instructions. "
        "Bad: 'You may click Save.' Good: 'Click Save.'"
    ),
    "UI_001": (
        "Do not use articles or the word 'button' when referencing UI labels in instructions. "
        "Bad: 'Click the Save button.' Good: 'Click Save.'"
    ),
    "UI_002": (
        "Do not use 'on' after UI action verbs like click, select, press, tap. "
        "Bad: 'Click on Save.' Good: 'Click Save.'"
    ),
    "SAFETY_001": (
        "NOTICE safety alerts must not include safety symbols. "
        "NOTICE is for property damage risk only, not personal injury. "
        "Bad: 'NOTICE ⚠️ Handle device carefully.' Good: 'NOTICE Handle device carefully.'"
    ),
    "SAFETY_002": (
        "WARNING, DANGER, and CAUTION safety alerts must include a safety symbol such as ⚠️. "
        "Bad: 'WARNING High voltage present.' Good: '⚠️ WARNING High voltage present.'"
    ),
    "PERSON_001": (
        "Avoid first-person singular pronouns I, my, me in technical documentation. "
        "Use second-person you for users or first-person plural we for the application. "
        "Bad: 'I will configure the system.' Good: 'You configure the system.'"
    ),
    "IMPERATIVE_001": (
        "Start procedural steps with imperative action verbs, not with 'To', 'In order to', or 'For'. "
        "Bad: 'To save the file, click Save.' Good: 'Click Save.'"
    ),
    "ADV_001": (
        "Avoid imprecise adverbs like simply, easily, quickly, basically, very, really, extremely, actually, just. "
        "These reduce precision in technical writing. "
        "Bad: 'Simply click the button.' Good: 'Click the button.'"
    ),
    "OXFORD_001": (
        "Use the Oxford comma in lists of three or more items before the final conjunction. "
        "Bad: 'Save, compile and deploy the file.' Good: 'Save, compile, and deploy the file.'"
    ),
    "PVERB_001": (
        "Avoid phrasal verbs that hinder localization and translation. "
        "Replace set up, shut down, turn on, turn off, log in, log out, back up, carry out with single precise verbs. "
        "Bad: 'Set up the configuration.' Good: 'Configure the system.'"
    ),
    "VAGUE_001": (
        "Vague terms like stuff, things, something, somehow, somewhat, etc. reduce precision in technical writing. "
        "Use specific nouns or explicit lists instead. "
        "Bad: 'Configure the settings and stuff.' Good: 'Configure the network, display, and security settings.'"
    ),
    "ACTION_001": (
        "Each procedural step should contain only one action. "
        "Multiple actions in a single step confuse readers. "
        "Bad: 'Click Save. Then close the dialog.' Good: '1. Click Save. 2. Close the dialog.'"
    ),
    "CONDITIONAL_001": (
        "Separate conditional statements from actions for better clarity. "
        "Bad: 'If error occurs, click Retry.' Good: 'When an error occurs: 1. Click Retry.'"
    ),
    "PLURAL_001": (
        "Reference specific singular UI elements by their exact label, not generic plurals. "
        "Bad: 'Click one of the buttons.' Good: 'Click Save or Cancel.'"
    ),
    "GENDER_001": (
        "Avoid gender-specific language. Use gender-neutral alternatives. "
        "Bad: 'The user can update his settings.' Good: 'Users can update their settings.'"
    ),
    "CONTRACTION_001": (
        "Avoid contractions in technical documentation. Use full forms. "
        "Bad: 'Don't close the window.' Good: 'Do not close the window.'"
    ),
    "JARGON_001": (
        "Avoid corporate jargon or unnecessarily complex words like utilize, leverage, facilitate, synergy, paradigm. "
        "Use simpler alternatives: use, apply, build, enable, improve. "
        "Bad: 'Utilize the configuration utility.' Good: 'Use the configuration utility.'"
    ),
    "LIST_001": (
        "Split multiple actions joined by 'and then' into separate numbered steps. "
        "Bad: 'Click Save and then restart.' Good: '1. Click Save. 2. Restart.'"
    ),
    "TRANS_001": (
        "Avoid idioms that harm localization clarity. Use literal phrasing. "
        "Bad: 'At the end of the day, the device restarts.' Good: 'Finally, the device restarts.'"
    ),
    "TRANS_002": (
        "Replace ambiguous quantity words like various, multiple, different with specific values or context. "
        "Bad: 'The device supports multiple modes.' Good: 'The device supports three modes.'"
    ),
    "CONSIST_001": (
        "Use UI action verbs consistently within the same procedure. Do not mix Click and Select. "
        "Bad: 'Click Save. then select Exit.' Good: 'Click Save. Click Exit.'"
    ),
}

# Category to retrieval keyword mapping (for hybrid BM25-style boost)
CATEGORY_KEYWORDS = {
    "tense":        ["future tense", "shall", "going to", "will", "present tense"],
    "ui-label":     ["button", "click", "select", "press", "tap", "UI label", "interface"],
    "safety":       ["warning", "caution", "danger", "notice", "safety", "symbol"],
    "voice":        ["imperative", "first person", "pronoun", "I", "my", "passive", "active"],
    "adverb":       ["adverb", "simply", "easily", "very", "really", "quickly"],
    "punctuation":  ["comma", "Oxford comma", "series", "list"],
    "phrasal-verb": ["phrasal verb", "set up", "shut down", "log in"],
    "clarity":      ["vague", "jargon", "stuff", "things", "utilize"],
    "procedure":    ["step", "action", "procedure", "numbered", "list"],
    "inclusivity":  ["gender", "inclusive", "neutral", "he", "she"],
    "formality":    ["contraction", "don't", "won't"],
    "translation":  ["idiom", "localization", "ambiguous", "various"],
    "consistency":  ["consistent", "verb", "UI action"],
}


class RuleVectorStore:
    """
    Manages a ChromaDB collection that stores style rules (not document text).
    Use `ingest_rules()` once to populate, then `retrieve_rules(sentence)` at runtime.
    """

    def __init__(
        self,
        db_path: str = _DB_PATH,
        collection_name: str = _COLLECTION_NAME,
        rules_json_path: str = _RULES_JSON,
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        self.db_path = db_path
        self.collection_name = collection_name
        self.rules_json_path = rules_json_path
        self.embedding_model_name = embedding_model
        self._client: Optional[Any] = None
        self._collection: Optional[Any] = None
        self._embedding_model: Optional[Any] = None
        self._ready = False
        self._init()

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def _init(self):
        if not CHROMADB_AVAILABLE:
            logger.warning("[RuleVectorStore] ChromaDB not available — store disabled")
            return
        try:
            self._client = chromadb.PersistentClient(path=self.db_path)
            logger.info(f"[RuleVectorStore] Connected to ChromaDB at {self.db_path}")
        except Exception as exc:
            logger.error(f"[RuleVectorStore] ChromaDB init failed: {exc}")
            return

        try:
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={
                    "description": "DocScanner style rules — rule-first RAG knowledge base",
                    "version": "2.0",
                },
            )
            logger.info(
                f"[RuleVectorStore] Collection '{self.collection_name}' ready "
                f"({self._collection.count()} rules)"
            )
        except Exception as exc:
            logger.error(f"[RuleVectorStore] Collection init failed: {exc}")
            return

        # Load embedding model if available
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self._embedding_model = SentenceTransformer(self.embedding_model_name)
                logger.info(f"[RuleVectorStore] Embedding model '{self.embedding_model_name}' loaded")
            except Exception as exc:
                logger.warning(f"[RuleVectorStore] Embedding model load failed: {exc}")

        self._ready = True

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_rules(self, force_reingest: bool = False) -> int:
        """
        Populate the vector store with style rules from rules.json.
        Each rule becomes one document in ChromaDB.

        Args:
            force_reingest: If True, clears existing rules and re-ingests.

        Returns:
            Number of rules successfully ingested.
        """
        if not self._ready:
            logger.error("[RuleVectorStore] Store not ready — skipping ingestion")
            return 0

        existing_count = self._collection.count()
        if existing_count > 0 and not force_reingest:
            logger.info(f"[RuleVectorStore] {existing_count} rules already in store — skipping (use force_reingest=True to override)")
            return existing_count

        # Load rules.json
        rules = self._load_rules_json()
        if not rules:
            logger.error("[RuleVectorStore] No rules loaded from rules.json")
            return 0

        if force_reingest and existing_count > 0:
            logger.info(f"[RuleVectorStore] Force re-ingest: deleting {existing_count} existing rules")
            self._client.delete_collection(self.collection_name)
            self._collection = self._client.create_collection(
                name=self.collection_name,
                metadata={"description": "DocScanner style rules v2", "version": "2.0"},
            )

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for rule in rules:
            rule_id = rule.get("rule_id", "UNKNOWN")
            category = rule.get("category", "general")
            severity = rule.get("severity", "warn")
            message = rule.get("message", "")
            suggestion = rule.get("suggestion", "")
            example_bad = rule.get("example_violation", "")
            example_good = rule.get("example_correction", "")

            # Build the embeddable text: rich description + examples + category keywords
            embed_text = RULE_EMBED_TEMPLATES.get(rule_id) or (
                f"{message} {suggestion} "
                f"Bad example: {example_bad} "
                f"Good example: {example_good} "
                f"Category: {category}"
            )

            # Add category keyword boosting text
            kw = " ".join(CATEGORY_KEYWORDS.get(category, []))
            embed_text = f"{embed_text} {kw}".strip()

            ids.append(rule_id)
            documents.append(embed_text)
            metadatas.append({
                "rule_id": rule_id,
                "category": category,
                "severity": severity,
                "message": message,
                "suggestion": suggestion,
                "example_violation": example_bad,
                "example_correction": example_good,
            })

        try:
            self._collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
            count = self._collection.count()
            logger.info(f"[RuleVectorStore] ✅ Ingested {count} style rules into '{self.collection_name}'")
            return count
        except Exception as exc:
            logger.error(f"[RuleVectorStore] Ingestion failed: {exc}")
            return 0

    def _load_rules_json(self) -> List[Dict[str, Any]]:
        """Load rules from rules.json."""
        if not os.path.exists(self.rules_json_path):
            logger.error(f"[RuleVectorStore] rules.json not found at {self.rules_json_path}")
            return []
        try:
            with open(self.rules_json_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            logger.info(f"[RuleVectorStore] Loaded {len(data)} rules from {self.rules_json_path}")
            return data
        except Exception as exc:
            logger.error(f"[RuleVectorStore] Failed to parse rules.json: {exc}")
            return []

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve_rules(
        self,
        sentence: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        severity_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant style rules for a given sentence.

        Args:
            sentence:         The sentence to evaluate.
            top_k:            Number of rules to retrieve.
            category_filter:  Optional ChromaDB $eq filter on category.
            severity_filter:  Optional ChromaDB $eq filter on severity.

        Returns:
            List of dicts: {rule_id, category, severity, message, suggestion,
                            example_violation, example_correction, score}
        """
        if not self._ready:
            logger.warning("[RuleVectorStore] Store not ready — returning empty results")
            return []

        if not sentence or not sentence.strip():
            return []

        # Build where clause
        where = self._build_where_clause(category_filter, severity_filter)

        try:
            kwargs: Dict[str, Any] = {
                "query_texts": [sentence],
                "n_results": min(top_k, self._collection.count() or 1),
                "include": ["documents", "metadatas", "distances"],
            }
            if where:
                kwargs["where"] = where

            results = self._collection.query(**kwargs)
        except Exception as exc:
            logger.error(f"[RuleVectorStore] Query failed: {exc}")
            return []

        out: List[Dict[str, Any]] = []
        if not results or not results.get("ids") or not results["ids"][0]:
            return out

        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            # ChromaDB can return L2 distances (range 0..∞) or cosine distances (0..2).
            # Normalise to [0,1] using: score = 1 / (1 + distance)
            # This is monotonically decreasing in distance and always ∈ (0,1].
            score = 1.0 / (1.0 + float(dist))
            out.append({
                "rule_id": meta.get("rule_id", "?"),
                "category": meta.get("category", "general"),
                "severity": meta.get("severity", "warn"),
                "message": meta.get("message", ""),
                "suggestion": meta.get("suggestion", ""),
                "example_violation": meta.get("example_violation", ""),
                "example_correction": meta.get("example_correction", ""),
                "embed_text": doc,
                "score": round(score, 4),
            })

        logger.debug(f"[RuleVectorStore] {len(out)} rules retrieved for: '{sentence[:60]}'")
        return out

    def _build_where_clause(
        self,
        category: Optional[str],
        severity: Optional[str],
    ) -> Optional[Dict]:
        """Construct ChromaDB where clause from optional filters."""
        conditions = []
        if category:
            conditions.append({"category": {"$eq": category}})
        if severity:
            conditions.append({"severity": {"$eq": severity}})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def count(self) -> int:
        """Return number of rules in the store."""
        if not self._ready:
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0

    def is_ready(self) -> bool:
        return self._ready


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_store: Optional[RuleVectorStore] = None


def get_rule_vectorstore() -> RuleVectorStore:
    """Return the module-level singleton RuleVectorStore (lazy init)."""
    global _store
    if _store is None:
        _store = RuleVectorStore()
        # Auto-ingest rules on first use if store is empty
        if _store.is_ready() and _store.count() == 0:
            logger.info("[RuleVectorStore] Auto-ingesting rules on first use...")
            _store.ingest_rules()
    return _store

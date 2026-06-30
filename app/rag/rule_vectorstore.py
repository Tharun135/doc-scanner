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
CHROMADB_AVAILABLE = False
SENTENCE_TRANSFORMERS_AVAILABLE = False
logger.warning("[RuleVectorStore] RAG replaced with JSON lookup to save memory")

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
        # Memory-optimized: We no longer initialize ChromaDB or SentenceTransformers
        # We will just load the JSON directly when needed
        self._ready = True
        logger.info("[RuleVectorStore] Initialized in JSON-only mode for Community Edition")

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_rules(self, force_reingest: bool = False) -> int:
        # In JSON-only mode, we don't ingest into a vector DB
        rules = self._load_rules_json()
        self._cached_rules = rules
        logger.info(f"[RuleVectorStore] ✅ Loaded {len(rules)} style rules into memory")
        return len(rules)

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
        if not hasattr(self, '_cached_rules') or not self._cached_rules:
            self.ingest_rules()
            
        if not sentence or not sentence.strip():
            return []

        out = []
        s_lower = sentence.lower()
        
        for rule in getattr(self, '_cached_rules', []):
            if category_filter and rule.get("category") != category_filter:
                continue
            if severity_filter and rule.get("severity") != severity_filter:
                continue
                
            rule_id = rule.get("rule_id", "?")
            category = rule.get("category", "general")
            
            # Simple keyword matching score
            score = 0.1 # Base score
            
            # Match keywords
            keywords = CATEGORY_KEYWORDS.get(category, [])
            for kw in keywords:
                if kw.lower() in s_lower:
                    score += 0.2
            
            # If we matched some keywords or it's a general match, include it
            if score > 0.1:
                out.append({
                    "rule_id": rule_id,
                    "category": category,
                    "severity": rule.get("severity", "warn"),
                    "message": rule.get("message", ""),
                    "suggestion": rule.get("suggestion", ""),
                    "example_violation": rule.get("example_violation", ""),
                    "example_correction": rule.get("example_correction", ""),
                    "embed_text": f"Rule {rule_id}: {rule.get('message')}",
                    "score": min(1.0, score),
                })
        
        # Sort by score descending and take top_k
        out.sort(key=lambda x: x["score"], reverse=True)
        return out[:top_k]

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
        if not hasattr(self, '_cached_rules') or not self._cached_rules:
            return 0
        return len(self._cached_rules)

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
    return _store

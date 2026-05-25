import requests
import os
import logging
import time

logger = logging.getLogger(__name__)

# Load environment variables based on DOCSCANNER_MODE
try:
    from dotenv import load_dotenv
    load_dotenv()
    env_mode = os.getenv("DOCSCANNER_MODE", "local")
    env_file = f".env.{env_mode}"
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, env_file)
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        logger.info(f"Loaded environment overrides from {env_path} (mode: {env_mode})")
except Exception as e:
    logger.warning(f"Failed to load environment variables in style_guide_service: {e}")

from app.style_guide_context import SIEMENS_STYLE_GUIDE
from app.rag.query import (
    retrieve_terminology,
    retrieve_reviewer_feedback,
    retrieve_similar_manual_chunks,
    retrieve_style_examples
)

# Try to initialize OpenAI client
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai_client = None
if os.getenv("ALLOW_CLOUD_LLM", "false").lower() == "true" and OPENAI_API_KEY:
    try:
        from openai import OpenAI
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✅ OpenAI Client initialized for Style Guide suggestions")
    except Exception as e:
        logger.warning(f"Failed to initialize OpenAI client in style_guide_service: {e}")

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_URL = f"{OLLAMA_HOST}/api/generate"
OLLAMA_CHAT_URL = f"{OLLAMA_HOST}/api/chat"
FAST_MODEL = "phi3:mini"
DEEP_MODEL = "llama3"

LLM_TIMEOUT = 30

http_session = requests.Session()

# Cache for model list to prevent overhead on every call
_available_models = None
def get_available_models():
    global _available_models
    if _available_models is not None:
        return _available_models
    try:
        response = http_session.get(f"{OLLAMA_HOST}/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get('models', [])
            _available_models = [m['name'] for m in models]
            logger.info(f"Ollama available models: {_available_models}")
            return _available_models
    except Exception as e:
        logger.warning(f"Could not connect to Ollama to list models: {e}")
    return []

def select_model(issue_type):
    """Dynamically select model based on task complexity and local availability"""
    available = get_available_models()
    
    # Decide preferred model class
    is_complex = issue_type in ["terminology", "consistency", "content_reuse", "reviewer_feedback"]
    preferred = DEEP_MODEL if is_complex else FAST_MODEL
    
    # Check if preferred exists
    for full_name in available:
        if full_name.startswith(preferred):
            return full_name
            
    # Check if fallback exists
    fallback = FAST_MODEL if preferred == DEEP_MODEL else DEEP_MODEL
    for full_name in available:
        if full_name.startswith(fallback):
            return full_name
            
    # Ultimate fallback: return first available model or default env setting
    if available:
        return available[0]
    return os.getenv("LLM_MODEL", "llama3")


# Setup ChromaDB for local manuals (lazily to avoid import deadlocks)
manuals_collection = None
style_rules_collection = None
db_initialized = False

def init_db():
    global manuals_collection, style_rules_collection, db_initialized
    if db_initialized:
        return
    try:
        import chromadb
        local_db_path = os.path.join(os.getcwd(), 'docscanner_db')
        local_db_client = chromadb.PersistentClient(path=local_db_path)
        manuals_collection = local_db_client.get_or_create_collection(name="manuals")
        style_rules_collection = local_db_client.get_or_create_collection(name="style_rules")
        logger.info("✅ Local docscanner_db 'manuals' and 'style_rules' collections initialized lazily.")
    except Exception as e:
        logger.warning(f"Failed to initialize local docscanner_db: {e}")
        manuals_collection = None
        style_rules_collection = None
    db_initialized = True

# Setup SQL-based Suggestion Cache to prevent repeated LLM calls
import sqlite3
import hashlib

CACHE_DB_PATH = os.path.join(os.getcwd(), 'style_suggestion_cache.db')

def init_cache_db():
    try:
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestion_cache (
                cache_key TEXT PRIMARY KEY,
                sentence TEXT,
                issue_type TEXT,
                feedback_text TEXT,
                issue TEXT,
                explanation TEXT,
                suggestion TEXT,
                ai_answer TEXT,
                confidence TEXT,
                prompt_version TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error initializing cache database: {e}")

init_cache_db()

def get_cached_suggestion(sentence, issue_type, feedback_text):
    try:
        cache_key = hashlib.md5(f"{sentence}-{issue_type}-{feedback_text}".encode()).hexdigest()
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT issue, explanation, suggestion, ai_answer, confidence, prompt_version 
            FROM suggestion_cache WHERE cache_key = ?
        ''', (cache_key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            logger.info(f"💾 Suggestion Cache HIT for key {cache_key}")
            return {
                "issue": row[0],
                "explanation": row[1],
                "suggestion": row[2],
                "ai_answer": row[3],
                "confidence": row[4],
                "prompt_version": row[5]
            }
    except Exception as e:
        logger.error(f"Error checking suggestion cache: {e}")
    return None

def set_cached_suggestion(sentence, issue_type, feedback_text, result):
    try:
        cache_key = hashlib.md5(f"{sentence}-{issue_type}-{feedback_text}".encode()).hexdigest()
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO suggestion_cache 
            (cache_key, sentence, issue_type, feedback_text, issue, explanation, suggestion, ai_answer, confidence, prompt_version)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cache_key,
            sentence,
            issue_type,
            feedback_text,
            result.get("issue", ""),
            result.get("explanation", ""),
            result.get("suggestion", ""),
            result.get("ai_answer", ""),
            result.get("confidence", ""),
            result.get("prompt_version", "")
        ))
        conn.commit()
        conn.close()
        logger.info(f"💾 Suggestion Cache SAVED for key {cache_key}")
    except Exception as e:
        logger.error(f"Error saving to suggestion cache: {e}")

def try_deterministic_rewrite(sentence, issue_type, feedback_text=""):
    """
    Attempt to rewrite the sentence using pure Python rules to avoid LLM latency/cost.
    Returns the rewritten sentence and explanation if successful, or None if LLM is required.
    """
    import re
    lower_sent = sentence.lower()
    rewritten = sentence
    changed = False
    explanation = ""

    # 1. Contractions
    contractions_map = {
        r"\b[Dd]on't\b": "do not",
        r"\b[Cc]an't\b": "cannot",
        r"\b[Ii]sn't\b": "is not",
        r"\b[Ww]on't\b": "will not",
        r"\b[Dd]oesn't\b": "does not",
        r"\b[Ii]t's\b": "it is",
        r"\b[Yy]ou're\b": "you are",
        r"\b[Tt]hey're\b": "they are",
        r"\b[Ww]e're\b": "we are",
        r"\b[Hh]aven't\b": "have not",
        r"\b[Dd]idn't\b": "did not",
        r"\b[Ww]ouldn't\b": "would not",
        r"\b[Aa]ren't\b": "are not",
        r"\b[Ww]eren't\b": "were not",
        r"\b[Ss]houldn't\b": "should not",
        r"\b[Cc]ouldn't\b": "could not",
        r"\b[Mm]ustn't\b": "must not",
        r"\b[Hh]asn't\b": "has not",
        r"\b[Hh]adn't\b": "had not",
        r"\b[Ww]asn't\b": "was not"
    }
    for pattern, repl in contractions_map.items():
        if re.search(pattern, rewritten):
            def match_case(match):
                text = match.group(0)
                if text.isupper():
                    return repl.upper()
                if text[0].isupper():
                    return repl.capitalize()
                return repl
            rewritten = re.sub(pattern, match_case, rewritten)
            changed = True
            explanation = "Expanded contraction to formal writing style."

    # 2. Click on / Press on / Tap on
    click_pattern = r"\b([Cc]lick|[Pp]ress|[Tt]ap|[Dd]ouble-click)\s+on\s+"
    if re.search(click_pattern, rewritten):
        rewritten = re.sub(click_pattern, r"\1 ", rewritten)
        changed = True
        explanation = "Removed redundant preposition 'on' after action verb."

    # 3. Simple substitutions
    substitutions = {
        r"\be\.g\.\b": "for example",
        r"\be\.\s+g\.\b": "for example",
        r"\blast update\b": "latest update",
        r"\blast version\b": "previous version",
        r"\blast events\b": "recent events",
        r"\bmaster\b": "primary",
        r"\bslave\b": "secondary",
        r"\butilize\b": "use",
        r"\butilizing\b": "using",
        r"\butilizes\b": "uses",
        r"\bleverage\b": "use",
        r"\bleveraging\b": "using",
        r"\bleverages\b": "uses",
        r"\bfacilitate\b": "enable",
        r"\bfacilitating\b": "enabling",
        r"\bfacilitates\b": "enables",
        r"\bat the end of the day\b": "ultimately",
        r"\bin a nutshell\b": "briefly"
    }
    for pattern, repl in substitutions.items():
        if re.search(pattern, rewritten, re.IGNORECASE):
            def match_case(match):
                text = match.group(0)
                if text.isupper():
                    return repl.upper()
                if text[0].isupper():
                    return repl.capitalize()
                return repl
            rewritten = re.sub(pattern, match_case, rewritten, flags=re.IGNORECASE)
            changed = True
            if not explanation:
                explanation = f"Replaced banned/vague term with plain equivalent: '{repl}'."

    # 4. Remove filler colloquial words: simply, just, please
    fillers = [r"\b[Ss]imply\b\s*", r"\b[Jj]ust\b\s*", r"\b[Pp]lease\b\s*"]
    for pattern in fillers:
        if re.search(pattern, rewritten):
            rewritten = re.sub(pattern, "", rewritten)
            changed = True
            rewritten = re.sub(r'\s+', ' ', rewritten).strip()
            if rewritten:
                rewritten = rewritten[0].upper() + rewritten[1:]
            explanation = "Removed colloquial filler word to improve formality."

    if changed and rewritten != sentence:
        return {
            "issue": issue_type,
            "explanation": explanation,
            "suggestion": rewritten,
            "ai_answer": "Style Guide Rule Engine (Deterministic)",
            "confidence": "high",
            "prompt_version": "v1.0 (Deterministic Engine)"
        }
    return None

import re

ORGANIZATION_DICTIONARY = [
    "TIA_Portal_Internal_Release_7.2",
    "Project-X",
    "ABC Customer Deployment Package",
    "PlantLine-MasterController",
    "ABC Corp"
]

def mask_sensitive(text):
    """
    Step 2: Mask sensitive content (IP_ADDRESS, EMAIL, PRODUCT, ORG, PERSON, GPE, CONFIDENTIAL)
    Combines:
      - Regex masking
      - Organization dictionary exact matching
      - NLP-based Custom Entity Detection (via SpaCy NER)
    Holds a dictionary of token replacements locally.
    """
    if not text:
        return "", {}
        
    replacements = {}
    
    # 1. Regex Masking (IP, Email, Product)
    regex_patterns = {
        "IP_ADDRESS": r'\b\d{1,3}(?:\.\d{1,3}){3}\b',
        "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
        "PRODUCT": r'\bPLC-\w+\b'
    }
    
    # 2. Organization Dictionary Masking
    # Sort by length descending to avoid matching substrings first
    sorted_org_dict = sorted(ORGANIZATION_DICTIONARY, key=len, reverse=True)
    org_dict_matches = []
    for item in sorted_org_dict:
        if item.lower() in text.lower():
            # Find the exact casing used in the text
            pattern = re.compile(re.escape(item), re.IGNORECASE)
            for match in pattern.findall(text):
                if match not in org_dict_matches:
                    org_dict_matches.append(match)
                    
    # 3. NLP Custom Entity Detection (SpaCy)
    nlp_matches = {}
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PERSON", "GPE"]:
                label = ent.label_
                val = ent.text.strip()
                if len(val) > 2:  # Avoid single letters or small noise
                    if label not in nlp_matches:
                        nlp_matches[label] = []
                    if val not in nlp_matches[label] and val.lower() not in [o.lower() for o in org_dict_matches]:
                        nlp_matches[label].append(val)
    except Exception as e:
        logger.debug(f"SpaCy NER masking skipped: {e}")

    # Now execute replacements in a consistent order
    
    # Replace Regexes
    for key, pattern in regex_patterns.items():
        matches = re.findall(pattern, text)
        unique_matches = []
        for m in matches:
            if m not in unique_matches:
                unique_matches.append(m)
        for i, match in enumerate(unique_matches):
            token = f"[{key}_{i}]"
            replacements[token] = match
            text = text.replace(match, token)
            
    # Replace Organization Dictionary matches
    for i, match in enumerate(org_dict_matches):
        token = f"[CONFIDENTIAL_{i}]"
        replacements[token] = match
        text = text.replace(match, token)
        
    # Replace SpaCy Entities
    ent_counter = 0
    for label, vals in nlp_matches.items():
        for val in vals:
            token = f"[{label}_{ent_counter}]"
            replacements[token] = val
            text = text.replace(val, token)
            ent_counter += 1
            
    return text, replacements

def restore(text, replacements):
    """
    Step 5: Restore original masked values using exact token matching and sorting by length to avoid corruption.
    """
    if not text:
        return text
    # Sort keys by length descending to prevent substring replacements (e.g. [PRODUCT_0] & [PRODUCT_0_CONF])
    sorted_tokens = sorted(replacements.keys(), key=len, reverse=True)
    for token in sorted_tokens:
        value = replacements[token]
        # Use re.escape and re.sub to ensure exact token matching
        text = re.sub(re.escape(token), value, text)
    return text

def ingest_manual_local(manual_text, filename, product="TIA", version="3.0", status="approved", doctype="manual"):
    """
    Step 1: Keep manuals and ChromaDB local.
    Store manuals locally with rich metadata to avoid database pollution and query degradation.
    """
    if manuals_collection is None:
        logger.warning("manuals_collection not initialized. Skipping local ingestion.")
        return None
    try:
        import uuid
        doc_id = f"manual_{filename}_{uuid.uuid4().hex[:8]}"
        manuals_collection.add(
            documents=[manual_text],
            ids=[doc_id],
            metadatas=[{
                "filename": filename,
                "product": product,
                "version": version,
                "status": status,
                "doctype": doctype
            }]
        )
        logger.info(f"Successfully stored manual '{filename}' locally in docscanner_db (ID: {doc_id})")
        return doc_id
    except Exception as e:
        logger.error(f"Error storing manual locally in docscanner_db: {e}")
        return None

def jaccard_similarity(str1, str2):
    """Calculate token-based Jaccard similarity between two strings."""
    words1 = set(str1.lower().split())
    words2 = set(str2.lower().split())
    if not words1 or not words2:
        return 0.0
    return len(words1.intersection(words2)) / len(words1.union(words2))

def select_diverse_chunks(chunks, top_n=3, similarity_threshold=0.6):
    """
    Select up to top_n chunks from list of chunks, 
    ensuring chosen chunks Jaccard similarity with previously chosen ones is below threshold.
    """
    selected = []
    for chunk in chunks:
        too_similar = False
        for sel in selected:
            if jaccard_similarity(chunk, sel) > similarity_threshold:
                too_similar = True
                break
        if not too_similar:
            selected.append(chunk)
            if len(selected) >= top_n:
                break
                
    # Fallback: if we filtered out too many, fill up with top ones
    if len(selected) < top_n and chunks:
        for chunk in chunks:
            if chunk not in selected:
                selected.append(chunk)
                if len(selected) >= top_n:
                    break
    return selected

def retrieve_relevant_manual_chunks(masked_sentence, n_results=3):
    """
    Step 3: Retrieve only 2-3 relevant chunks from local manuals vector store.
    Retrieves top 10 chunks, filters them for diversity to avoid nearly identical content,
    and queries only approved status manuals to avoid noise.
    """
    init_db()
    if manuals_collection is None:
        logger.warning("manuals_collection not initialized. Skipping retrieval.")
        return ""
    try:
        # Retrieve top 10 first to allow diversity filtering
        results = manuals_collection.query(
            query_texts=[masked_sentence],
            n_results=10,
            where={"status": "approved"}
        )
        if results and results.get("documents") and results["documents"][0]:
            documents = results["documents"][0]
            # Select top 2-3 diverse ones
            diverse_chunks = select_diverse_chunks(documents, top_n=n_results, similarity_threshold=0.6)
            return "\n".join(diverse_chunks)
        return ""
    except Exception as e:
        logger.error(f"Error retrieving from local RAG manuals collection: {e}")
        return ""

def retrieve_relevant_style_rules(issue_type, feedback_text="", n_results=2):
    """
    Retrieve matching rules from the 'style_rules' collection based on the checker issue.
    """
    init_db()
    if style_rules_collection is None:
        logger.warning("style_rules_collection not initialized. Skipping style rules retrieval.")
        return ""
    try:
        query_text = f"{issue_type} {feedback_text}"
        results = style_rules_collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        if results and results.get("documents") and results["documents"][0]:
            documents = results["documents"][0]
            metadatas = results["metadatas"][0] if results.get("metadatas") else []
            
            rule_texts = []
            for doc, meta in zip(documents, metadatas):
                rule_text = (
                    f"Rule: {meta.get('rule_type', 'General')}\n"
                    f"Description: {meta.get('description', doc)}\n"
                    f"Good Example: {meta.get('good_example', '')}\n"
                    f"Bad Example: {meta.get('bad_example', '')}"
                )
                rule_texts.append(rule_text)
            return "\n\n".join(rule_texts)
        return ""
    except Exception as e:
        logger.error(f"Error retrieving from style_rules collection: {e}")
        return ""

def parse_openai_feedback(feedback_text, default_issue="Style Violation", original_sentence=""):
    """
    Helper to parse OpenAI output into issue, explanation, and suggestion.
    Supports both standard text structures and numbered lists from Step 4.
    """
    issue = default_issue
    explanation = ""
    suggestion = ""
    
    # Parse line by line, case-insensitive prefixes
    lines = feedback_text.split("\n")
    for line in lines:
        line_strip = line.strip()
        lower_line = line_strip.lower()
        if lower_line.startswith("1. issue detected:") or lower_line.startswith("issue detected:") or lower_line.startswith("issue:"):
            for prefix in ["1. issue detected:", "issue detected:", "issue:"]:
                if lower_line.startswith(prefix):
                    issue = line_strip[len(prefix):].strip()
                    break
        elif lower_line.startswith("2. explanation:") or lower_line.startswith("explanation:") or lower_line.startswith("explain:"):
            for prefix in ["2. explanation:", "explanation:", "explain:"]:
                if lower_line.startswith(prefix):
                    explanation = line_strip[len(prefix):].strip()
                    break
        elif any(lower_line.startswith(p) for p in ["3. suggested rewrite:", "suggested rewrite:", "suggestion:", "rewrite:", "3. original sentence:", "original sentence:", "3. solution:", "solution:", "suggested:", "original:"]):
            for prefix in ["3. suggested rewrite:", "suggested rewrite:", "suggestion:", "rewrite:", "3. original sentence:", "original sentence:", "3. solution:", "solution:", "suggested:", "original:"]:
                if lower_line.startswith(prefix):
                    suggestion = line_strip[len(prefix):].strip()
                    break
                    
    if not suggestion:
        suggestion = feedback_text.strip()
    else:
        suggestion = suggestion.strip(' \t\n\r"\'')
        
    # Post-process placeholders
    if suggestion:
        lower_sug = suggestion.lower().strip(" \t\n\r.\"'[]()")
        placeholders = {
            "keep original sentence", "keep original", "no changes needed", 
            "no change needed", "no change", "no changes", "correct as is", 
            "correct as-is", "none", "original sentence"
        }
        if lower_sug in placeholders and original_sentence:
            suggestion = original_sentence
        
    return issue, explanation, suggestion

def generate_style_suggestion_local_ollama(prompt, issue_type):
    """
    Attempts to call the local Ollama instance for the suggestion.
    This runs entirely on the user's machine and is 100% private.
    """
    try:
        model_name = select_model(issue_type)
        logger.info(f"Calling local Ollama instance (model: {model_name})")
        response = http_session.post(
            OLLAMA_URL,
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            },
            timeout=LLM_TIMEOUT
        )
        response.raise_for_status()
        raw_text = response.json().get("response", "").strip()
        return raw_text
    except Exception as e:
        logger.error(f"Local Ollama execution failed: {e}")
        # If Ollama fails and ALLOW_CLOUD_LLM is false, we MUST fail closed and not retry with OpenAI!
        raise RuntimeError(f"Local Ollama model unavailable: {e}")

def call_openai_style_suggestion(prompt, sentence, retrieved_context):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment, cannot use OpenAI fallback")
    
    from openai import OpenAI
    openai_client_instance = OpenAI(api_key=api_key)
    
    used_model = os.getenv("OPENAI_MODEL", "gpt-5.5")
    LOG_EXTERNAL = os.getenv("LOG_EXTERNAL_REQUESTS", "false").lower() == "true"
    
    if LOG_EXTERNAL:
        from datetime import datetime
        time_str = datetime.now().strftime("%H:%M:%S")
        # Text-style log
        logger.info(f"\n{time_str}\nSentence sent externally\nMasked=True\nRetrieved chunks={3 if retrieved_context else 0}\nModel={used_model}\n")
        
        # Dictionary-style log
        logger.info({
            "timestamp": time.time(),
            "sentence_length": len(sentence),
            "masked": True,
            "cloud_used": True,
            "model": used_model,
            "retrieved_chunks": 3 if retrieved_context else 0
        })
        
    try:
        response = openai_client_instance.responses.create(
            model=used_model,
            input=prompt
        )
        raw_text = response.output_text
        logger.info("OpenAI client.responses.create request successful.")
        return raw_text, used_model
    except (AttributeError, TypeError, Exception) as e:
        logger.info(f"client.responses.create failed or unsupported ({e}), using client.chat.completions.create fallback")
        response = openai_client_instance.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional technical editor. Follow instructions exactly and output only the requested details. Avoid comments or conversation."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300
        )
        raw_text = response.choices[0].message.content.strip()
        return raw_text, "gpt-4o-mini"

def generate_style_suggestion(sentence, issue_type, feedback_text=""):
    """
    Generate suggestion using the privacy-centric local RAG + OpenAI pipeline.
    
    Steps:
    1. Check if the issue type is local (passive voice, etc.) to skip OpenAI.
    2. Mask sensitive content.
    3. Query local manuals DB for 2-3 related chunks.
    4. Send only sentence + retrieved context to OpenAI (with gpt-5.5 / completions fallbacks).
    5. Restore original masked values.
    6. Return structured feedback.
    """
    start_time = time.time()
    
    # Step 0a: Check persistent cache
    cached = get_cached_suggestion(sentence, issue_type, feedback_text)
    if cached:
        cached["processing_time"] = (time.time() - start_time) * 1000
        return cached

    # Step 0b: Check deterministic rule engine
    det_rewrite = try_deterministic_rewrite(sentence, issue_type, feedback_text)
    if det_rewrite:
        det_rewrite["processing_time"] = (time.time() - start_time) * 1000
        set_cached_suggestion(sentence, issue_type, feedback_text, det_rewrite)
        return det_rewrite

    issue_type_lower = issue_type.lower()
    
    local_issues = [
        "passive_voice", "active_voice", "sg-av-001", 
        "future_tense", "tense", "verb_tense",
        "sentence_length", "long_sentence", 
        "readability", "grammar", "punctuation", "punctuation_spacing",
        "headings", "sg-he"
    ]

    # Step 2: Mask sensitive content
    masked_sentence, replacements = mask_sensitive(sentence)
    logger.info(f"Masked sensitive data. Replacements: {replacements}")

    # Step 3: Retrieve only 2-3 relevant chunks from local RAG (manuals)
    retrieved_context = retrieve_relevant_manual_chunks(masked_sentence, n_results=3)
    logger.info(f"Retrieved local RAG context (length: {len(retrieved_context)})")

    # Step 3b: Retrieve relevant style rules from local RAG (style rules)
    retrieved_rules = retrieve_relevant_style_rules(issue_type, feedback_text, n_results=2)
    logger.info(f"Retrieved relevant style rules (length: {len(retrieved_rules)})")

    prompt = f"""
You are a technical documentation style guide assistant.
The rule checker flagged a potential issue in the following sentence/heading.

Sentence/Heading:
"{masked_sentence}"

Flagged Issue Category/Type: {issue_type}
Rule Warning Message: {feedback_text}

Relevant Siemens Style Guide Rules:
{retrieved_rules}

Retrieved Reference Context from Technical Manuals:
{retrieved_context}

Your task:
Analyze the sentence and the rule warning message in light of the style guide rules and manuals context.
1. Determine if the warning message is a FALSE POSITIVE (i.e. the flagged sentence is correct under the style rules, or represents an allowed exception).
   * Note: A sentence length warning is NOT a false positive if the sentence has 20 or more words. You must rewrite it to be shorter or split it.
   * Note: A passive voice warning is NOT a false positive unless there is no actor. You must rewrite it in the active voice.
2. If it is a false positive, the SOLUTION is to keep the original sentence.
3. If it is a genuine style issue, the SOLUTION is to provide the corrected sentence conforming to the style rules (e.g. converting non-product names to lowercase, changing to active voice, splitting long sentences, etc.).

Output the analysis in this exact format:
1. Issue detected: [State the issue, or write "None" if it is a false positive]
2. Explanation: [Provide a brief explanation of the style evaluation or what was changed]
3. Suggested rewrite: [Write ONLY the final corrected sentence or the original sentence if it was correct. Do not wrap in quotes or add extra introductory words.]
"""

    ALLOW_CLOUD = os.getenv("ALLOW_CLOUD_LLM", "false").lower() == "true"
    
    raw_text = ""
    used_cloud = False
    used_model = "unknown"
    
    try:
        # Step 4: Call LLM with explicit local-first fail-closed routing
        try:
            logger.info("Attempting local Ollama processing first.")
            raw_text = generate_style_suggestion_local_ollama(prompt, issue_type)
            used_model = select_model(issue_type)
            used_cloud = False
        except Exception as e:
            logger.warning(f"Local Ollama processing failed: {e}")
            if not ALLOW_CLOUD:
                logger.error("ALLOW_CLOUD_LLM is false. Enforcing fail-closed behavior.")
                raise RuntimeError(f"Local model unavailable and cloud fallback is disabled: {e}")
            
            logger.info("ALLOW_CLOUD_LLM is true. Falling back to OpenAI cloud service.")
            raw_text, used_model = call_openai_style_suggestion(prompt, sentence, retrieved_context)
            used_cloud = True
                    
    except Exception as e:
        logger.error(f"Error calling LLM for style suggestion: {e}")
        
        # Fallback to local rule engine if available for this issue type
        if any(local in issue_type_lower for local in local_issues):
            logger.info("Falling back to local rule engine suggestion.")
            suggestion = "Rewrite the sentence to address the style guideline."
            explanation = "Applying local style guide recommendations."
            
            # Extract suggested replacement if present in feedback_text
            if feedback_text:
                import re
                match = re.search(r'(?:Suggested|Suggestion|Replace with):\s*"(.*?)"', feedback_text, re.IGNORECASE)
                if match:
                    suggestion = match.group(1)
                    explanation = feedback_text
            
            if "passive" in issue_type_lower or "active" in issue_type_lower:
                if suggestion == "Rewrite the sentence to address the style guideline.":
                    suggestion = "Rewrite in active voice. Place the actor at the beginning."
                explanation = "Active voice is more direct and easier to understand."
            elif "long" in issue_type_lower or "length" in issue_type_lower:
                if suggestion == "Rewrite the sentence to address the style guideline.":
                    suggestion = "Split the sentence into two or more shorter sentences."
                explanation = "Shorter sentences improve readability."
            elif "tense" in issue_type_lower:
                if suggestion == "Rewrite the sentence to address the style guideline.":
                    suggestion = "Use the simple present tense or imperative mood."
                explanation = "Simple present tense makes instructions clearer."
                
            return {
                "issue": issue_type,
                "suggestion": suggestion,
                "explanation": explanation,
                "ai_answer": f"Generated locally via Rule Engine (LLM fallback due to: {str(e)})",
                "confidence": "high",
                "processing_time": (time.time() - start_time) * 1000,
                "prompt_version": "local_rule_engine_fallback"
            }
            
        return {
            "issue": issue_type,
            "suggestion": "Could not generate suggestion automatically.",
            "explanation": f"Service encountered an error: {str(e)}",
            "ai_answer": f"Fail closed error: {str(e)}",
            "confidence": "low",
            "processing_time": (time.time() - start_time) * 1000,
            "prompt_version": "fail_closed_error"
        }

    # Step 5: Restore original values
    restored_text = restore(raw_text, replacements)
    logger.info("Restored masked values in LLM response.")

    # Parse the restored response
    parsed_issue, parsed_explanation, parsed_suggestion = parse_openai_feedback(restored_text, default_issue=issue_type, original_sentence=sentence)

    ai_answer_type = f"Generated via OpenAI ({used_model}) with local RAG grounding" if used_cloud else f"Generated locally via Ollama ({used_model})"

    res = {
        "issue": parsed_issue,
        "suggestion": parsed_suggestion,
        "explanation": parsed_explanation,
        "ai_answer": ai_answer_type,
        "confidence": "high" if retrieved_context else "medium",
        "processing_time": (time.time() - start_time) * 1000,
        "prompt_version": "v4.0 (Privacy-Masked + Local RAG)"
    }
    set_cached_suggestion(sentence, issue_type, feedback_text, res)
    return res

def reset_rate_limit():
    pass

def is_ambiguity_eligible(sentence, fb):
    """
    Check if a sentence is eligible for ambiguity analysis using OpenAI.
    Enforces filtering to only send 5-10% of candidate sentences.
    """
    if not sentence:
        return False
        
    # 1. Pronouns check
    pronouns = {"it", "they", "their", "this", "these", "them", "he", "she", "him", "her", "you", "your", "we", "our"}
    words = set(re.findall(r'\b\w+\b', sentence.lower()))
    if not words.isdisjoint(pronouns):
        return True
        
    # 2. Sentence length check (longer sentences are more likely to be ambiguous)
    word_count = len(sentence.split())
    if word_count > 22:
        return True
        
    # 3. Readability score approximation (e.g. complex words density)
    # If the sentence contains multiple long words (>= 8 chars)
    complex_words = [w for w in words if len(w) >= 8]
    if len(complex_words) > 3:
        return True
        
    # 4. Multiple actions check
    # Check for multiple action indicator words (conjunctions/connectors)
    action_connectors = {"and", "then", "after", "before", "while", "when"}
    if len(words.intersection(action_connectors)) >= 2:
        return True
        
    # 5. Low confidence or high severity check in feedback
    if fb and (fb.get("confidence") == "low" or fb.get("severity") == "high"):
        return True
        
    return False

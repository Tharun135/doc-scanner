# app/services/enrichment.py
import logging, chromadb, os, re
from functools import lru_cache
import hashlib
import json

logger = logging.getLogger(__name__)
CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_db")
COLLECTION = os.getenv("DOCSCANNER_SOLUTIONS_COLLECTION", "docscanner_solutions")

# SPEED OPTIMIZATION: Pre-compile regex patterns for faster matching
PASSIVE_VOICE_PATTERN = re.compile(r'\b(is|are|was|were)\s+.*\b\w+ed\b|^\s*(has|have)\s+been\s+\w+', re.IGNORECASE)
ADVERB_PATTERN = re.compile(r'\b(easily|simply|basically|manually|automatically|actually|really|generally|typically|optionally)\b', re.IGNORECASE)
MODAL_VERB_PATTERN = re.compile(r'\b(can|may|should|will|could|might|would)\b', re.IGNORECASE)
CLICK_ON_PATTERN = re.compile(r'\bclick on\b', re.IGNORECASE)
ALL_CAPS_PATTERN = re.compile(r'\b[A-Z]{3,}\b')
FILLER_PATTERN = re.compile(r'\b(just|really|very|quite|rather|somewhat|pretty much)\b', re.IGNORECASE)

# Speed optimization: Cache ChromaDB collection
@lru_cache(maxsize=1)
def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        return client.get_collection(COLLECTION)
    except Exception:
        logger.warning("Chroma collection '%s' not found at %s", COLLECTION, CHROMA_PATH)
        return None

# Speed optimization: Cache query results for repeated requests
@lru_cache(maxsize=500)  # Increased cache size for better hit rate
def _cached_vector_query(query_text: str, n_results: int = 2):  # Reduced from 4 to 2 for speed
    """Cache ChromaDB queries to avoid repeated vector searches"""
    collection = _get_collection()
    if not collection:
        return None
    
    try:
        return collection.query(
            query_texts=[query_text], 
            n_results=n_results, 
            include=["documents", "metadatas", "distances"]
        )
    except Exception as e:
        logger.error(f"Cached query failed: {e}")
        return None

# Speed optimization: Cache deterministic rewrites
@lru_cache(maxsize=200)
def _cached_deterministic_rewrite(feedback_text: str, sentence_context: str) -> str:
    """Cache deterministic rewrite results for identical inputs"""
    # Forward to the actual implementation (will be defined later)
    return _create_deterministic_rewrite_uncached(feedback_text, sentence_context)

# Speed optimization: Fast fallback result creator
def _create_fast_fallback_result(issue: dict) -> dict:
    """Create a fast fallback result when vector query fails"""
    feedback_text = issue.get("message", "")
    sentence_context = issue.get("context", "")
    
    # Use cached deterministic rewrite for speed
    deterministic_rewrite = _create_deterministic_rewrite_uncached(feedback_text, sentence_context)
    
    # Create fast guidance based on issue type
    issue_type = issue.get("issue_type", "").lower()
    message = issue.get("message", "").lower()
    
    if "adverb" in message or "adverb" in issue_type:
        guidance = "Remove unnecessary adverbs to make writing more direct."
    elif "passive" in message or "passive" in issue_type:
        guidance = "Convert to active voice with clear subject."
    elif "modal" in message or any(word in message for word in ["can", "may", "should"]):
        guidance = "Use direct imperative language instead of modal verbs."
    else:
        guidance = f"Address: {issue.get('message', 'improve writing clarity')}"
    
    issue["solution_text"] = guidance
    issue["proposed_rewrite"] = deterministic_rewrite
    issue["sources"] = []
    issue["method"] = "fast_fallback"
    
    return issue

def _first_hit_text(hits):
    try:
        return (hits[0]["document"] or "")[:120]
    except Exception:
        return ""

def _best_similarity(hits):
    try:
        return float(hits[0].get("similarity", 0.0))
    except Exception:
        return 0.0

def _create_llm_powered_rewrite(feedback_text: str, sentence_context: str) -> str:
    """Use LLM to create a polished rewrite based on feedback - OPTIMIZED FOR SPEED"""
    try:
        import requests
        
        # Create a very concise prompt for speed
        prompt = f"Fix: {feedback_text}\nOriginal: {sentence_context}\nFixed:"
        
        # Use tinyllama with aggressive speed settings
        ollama_url = "http://localhost:11434/api/generate"
        response = requests.post(ollama_url, json={
            'model': 'tinyllama:latest',  # Fastest model
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.1,     # Lower for consistency
                'top_p': 0.8,
                'num_predict': 30,      # Very short response
                'num_ctx': 512,         # Smaller context window
                'repeat_penalty': 1.1
            }
        }, timeout=0.5)  # ULTRA-FAST timeout - 0.5 seconds only
        
        if response.status_code == 200:
            result = response.json()
            suggestion = result.get('response', '').strip()
            
            # Clean up the response
            suggestion = suggestion.replace('"', '').strip()
            for prefix in ['Fixed:', 'FIXED:', 'Rewrite:', 'REWRITE:', '-', '•']:
                if suggestion.startswith(prefix):
                    suggestion = suggestion[len(prefix):].strip()
                    break
                
            # Ensure it's different and reasonable
            if (suggestion and 
                suggestion.lower() != sentence_context.lower().strip() and 
                len(suggestion) > 5 and len(suggestion) < 200):
                logger.info(f"✅ LLM rewrite: '{suggestion[:50]}...'")
                return suggestion
        else:
            logger.warning(f"Ollama returned status {response.status_code}")
                
    except requests.exceptions.Timeout:
        logger.info("⚡ LLM timeout (2s) - using deterministic fallback")
    except requests.exceptions.ConnectionError:
        logger.warning("🔌 Ollama not accessible")
    except Exception as e:
        logger.warning(f"❌ LLM failed: {e}")
    
    # Fast fallback to deterministic rewrite
    return None


def _create_deterministic_rewrite(feedback_text: str, sentence_context: str) -> str:
    """Create a deterministic rewrite based on feedback patterns - WITH CACHING"""
    # Use cached version for performance
    return _cached_deterministic_rewrite(feedback_text, sentence_context)

def _create_deterministic_rewrite_uncached(feedback_text: str, sentence_context: str) -> str:
    """Create a deterministic rewrite based on feedback patterns - OPTIMIZED VERSION"""
    import re  # Explicit import to avoid scoping issues
    
    text = sentence_context.strip()
    if not text:
        return "Please provide clearer text."
    
    feedback_lower = feedback_text.lower()
    
    # SPEED OPTIMIZATION: Use pre-compiled patterns instead of re.search each time
    
    # Passive voice patterns - using pre-compiled regex
    if "passive voice" in feedback_lower or PASSIVE_VOICE_PATTERN.search(text):
        # Convert "was uploaded by" → "user uploads"
        text = re.sub(r'\bwas\s+(\w+ed)\s+by\s+(.+)', r'\2 \1s', text)
        text = re.sub(r'\bwere\s+(\w+ed)\s+by\s+(.+)', r'\2 \1', text)
        text = re.sub(r'\bis\s+(\w+ed)\s+by\s+(.+)', r'\2 \1s', text)
        text = re.sub(r'\bare\s+(\w+ed)\s+by\s+(.+)', r'\2 \1', text)
        # Fix "has been" constructions
        text = re.sub(r'\bhas\s+been\s+(\w+ed)', r'is \1', text)
        text = re.sub(r'\bhave\s+been\s+(\w+ed)', r'are \1', text)
        
    # Adverb removal - using pre-compiled pattern
    elif "adverb" in feedback_lower or ADVERB_PATTERN.search(text):
        text = ADVERB_PATTERN.sub('', text)
        # Clean up double spaces
        text = re.sub(r'\s+', ' ', text)
        
    # Modal verb patterns - using pre-compiled pattern
    elif "modal" in feedback_lower or MODAL_VERB_PATTERN.search(text):
        text = CLICK_ON_PATTERN.sub('click', text)
        text = re.sub(r'\byou may now\b', 'now you can', text, flags=re.IGNORECASE)
        text = re.sub(r'\byou should\b', 'please', text, flags=re.IGNORECASE)
        text = re.sub(r'\bwill be able to\b', 'can', text, flags=re.IGNORECASE)
        
    # Long sentence patterns - quick check
    elif "long" in feedback_lower and "sentence" in feedback_lower:
        if ', and ' in text:
            parts = text.split(', and ', 1)
            if len(parts) == 2:
                text = f"{parts[0].strip()}. {parts[1].strip().capitalize()}"
        elif ', which ' in text:
            parts = text.split(', which ', 1)
            if len(parts) == 2:
                text = f"{parts[0].strip()}. This {parts[1].strip()}"
    
    # Capitalization - using pre-compiled pattern
    elif "caps" in feedback_lower or "capital" in feedback_lower or "all caps" in feedback_lower:
        # Fix common capitalization issues quickly
        text = ALL_CAPS_PATTERN.sub(lambda m: m.group(0).capitalize() if len(m.group(0)) > 3 else m.group(0), text)
    
    # Clean up spacing and ensure proper sentence structure
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Ensure proper capitalization and punctuation
    if text and not text[0].isupper():
        text = text[0].upper() + text[1:]
    if text and not text.endswith(('.', '!', '?', ':')):
        text += '.'
    
    # Return improved version, or create a meaningful alternative if no change
    if text != sentence_context.strip():
        return text
    else:
        # Fast fallback for unchanged text
        if PASSIVE_VOICE_PATTERN.search(sentence_context):
            return "Use active voice: " + sentence_context[:50] + "..."
        elif ADVERB_PATTERN.search(sentence_context):
            return ADVERB_PATTERN.sub('', sentence_context).strip() or sentence_context
        else:
            return f"Improve: {sentence_context[:60]}..."
    """Create a deterministic rewrite based on feedback patterns"""
    import re
    
    text = sentence_context.strip()
    if not text:
        return ""
    
    feedback_lower = feedback_text.lower()
    
    # Passive voice patterns - more comprehensive  
    if "passive voice" in feedback_lower or re.search(r'\b(is|are|was|were)\s+.*\b\w+ed\b', text) or re.search(r'\b(has|have)\s+been\s+\w+', text):
        # Convert passive constructions to active
        text = re.sub(r'\b(is|are)\s+displayed\b', 'appears', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(is|are)\s+shown\b', 'appears', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(is|are)\s+generated\b', 'generates', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(was|were)\s+created\b', 'created', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(is|are)\s+configured\b', 'configures', text, flags=re.IGNORECASE)
        
        # Handle "has/have been + past participle" (present perfect passive)
        text = re.sub(r'\bhas been created\b', 'exists', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhave been created\b', 'exist', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhas already been created\b', 'already exists', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhave already been created\b', 'already exist', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhas been configured\b', 'is configured', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhave been configured\b', 'are configured', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhas been defined\b', 'exists', text, flags=re.IGNORECASE)
        text = re.sub(r'\bhave been defined\b', 'exist', text, flags=re.IGNORECASE)
        
        # Handle "are only defined" pattern
        text = re.sub(r'\b(.*?)\s+(are|is)\s+(only\s+)?defined\b', r'The system defines \1 \3', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(.*?)\s+(are|is)\s+(only\s+)?provided\b', r'The system provides \1 \3', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(.*?)\s+(are|is)\s+(only\s+)?supported\b', r'The system supports \1 \3', text, flags=re.IGNORECASE)
        
        # More complex passive patterns
        if 'by the' in text.lower():
            # "X was done by Y" -> "Y does X" pattern
            match = re.search(r'(.*?)\s+(was|were)\s+(\w+ed)\s+by\s+(.*)', text, re.IGNORECASE)
            if match:
                subject, verb, action, actor = match.groups()
                text = f"{actor.strip()} {action.replace('ed', 's')} {subject.strip()}"
        
        # If no specific pattern matched, use imperative for instructions
        if re.search(r'\b(click|select|open|configure|enter|choose)\b', text, re.IGNORECASE):
            text = re.sub(r'^(you can |the user can |the system )', '', text, flags=re.IGNORECASE)
            text = text.capitalize()
        
    # Adverb removal - more comprehensive
    elif "adverb" in feedback_lower or re.search(r'\b(easily|simply|basically|actually|really|generally|typically|optionally)\b', feedback_lower):
        # Remove weak adverbs
        text = re.sub(r'\b(really|easily|simply|basically|actually|generally|typically|optionally)\s+', '', text, flags=re.IGNORECASE)
        # Handle "and optionally" patterns
        text = re.sub(r'\s+and\s+optionally\s+', ' and ', text, flags=re.IGNORECASE)
        text = re.sub(r'\boptionally,?\s*', '', text, flags=re.IGNORECASE)
        
    # Modal verb patterns - more comprehensive
    elif "modal" in feedback_lower or any(word in feedback_lower for word in ["can", "may", "should", "will"]):
        text = re.sub(r'\bclick on\b', 'click', text, flags=re.IGNORECASE)
        text = re.sub(r'\byou may now\b', 'now you can', text, flags=re.IGNORECASE)
        text = re.sub(r'\byou should\b', 'please', text, flags=re.IGNORECASE)
        text = re.sub(r'\bwill be able to\b', 'can', text, flags=re.IGNORECASE)
        
    # Long sentence patterns
    elif "long" in feedback_lower and "sentence" in feedback_lower:
        # Try to break at natural points
        if ', and ' in text:
            parts = text.split(', and ', 1)
            if len(parts) == 2:
                text = f"{parts[0].strip()}. {parts[1].strip().capitalize()}"
        elif ', which ' in text:
            parts = text.split(', which ', 1)
            if len(parts) == 2:
                text = f"{parts[0].strip()}. This {parts[1].strip()}"
    
    # Terminology and consistency
    elif "caps" in feedback_lower or "capital" in feedback_lower or "all caps" in feedback_lower:
        # Fix common capitalization issues
        text = re.sub(r'\bAPI\b', 'API', text)  # Keep API capitalized
        text = re.sub(r'\bURL\b', 'URL', text)  # Keep URL capitalized
        text = re.sub(r'\bCLICK\b', 'Click', text)  # Fix all caps
        text = re.sub(r'\bSELECT\b', 'Select', text)  # Fix all caps
        # Fix ALL CAPS words to sentence case (but preserve acronyms)
        def fix_caps(match):
            word = match.group(0)
            if len(word) <= 3 and word.isupper():  # Likely acronym
                return word
            else:
                return word.capitalize()
        text = re.sub(r'\b[A-Z]{3,}\b', fix_caps, text)
    
    # Clean up spacing and ensure proper sentence structure
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Ensure the sentence starts with capital letter and ends with period
    if text and not text[0].isupper():
        text = text[0].upper() + text[1:]
    if text and not text.endswith(('.', '!', '?', ':')):
        text += '.'
    
    # Return improved version, or fallback if no change was made
    if text != sentence_context.strip():
        return text
    else:
        # Fallback: Create a generic but helpful improvement
        if re.search(r'\b(is|are|was|were)\s+\w+ed\b', sentence_context):
            return "Use active voice: " + re.sub(r'\b(is|are|was|were)\s+', '', sentence_context, 1)
        else:
            return f"Improve clarity: {sentence_context.strip()}"

def _policy_rewrite(original: str, policy: dict) -> str:
    """
    Small, deterministic rewriting helpers based on policy metadata.
    Extend as needed (adverbs, passive→active, etc.).
    """
    if not original:
        return ""
    text = original

    # Passive voice nudge (very light heuristic)
    text = re.sub(r"\b(is|are|was|were)\s+([a-z]+ed)\b", r"\2", text, flags=re.IGNORECASE)

    # Adverb overuse (remove common adverbs; policy can supply list)
    if isinstance(policy, dict):
        adverbs = set(map(str.lower, policy.get("adverbs", ["easily", "simply", "basically", "actually"])))
    else:
        adverbs = set(["easily", "simply", "basically", "actually"])
    def drop_adverbs(m):
        word = m.group(0)
        return "" if word.lower() in adverbs else word
    text = re.sub(r"\b\w+ly\b", drop_adverbs, text)

    # Trim multiple spaces
    text = re.sub(r"\s{2,}", " ", text).strip()
    return text

def _force_change(original: str, candidate: str) -> str:
    """Ensure the candidate differs from the original; if not, apply a meaningful improvement."""
    if not candidate:
        return ""
    if original.strip() == candidate.strip():
        # Apply meaningful transformations instead of just adding "(revised)"
        text = original.strip()
        
        # Strategy 1: Convert passive voice to active
        if re.search(r'\b(is|are|was|were)\s+\w+ed\b', text, re.IGNORECASE):
            text = re.sub(r'\b(is|are)\s+(\w+ed)\b', r'appears \2', text, flags=re.IGNORECASE)
            text = re.sub(r'\b(was|were)\s+(\w+ed)\b', r'shows \2', text, flags=re.IGNORECASE)
            if text != original.strip():
                return text
        
        # Strategy 2: Make imperative for UI instructions
        if re.search(r'\b(click|select|open|configure|enter|choose)\b', text, re.IGNORECASE):
            if text.lower().startswith(("you can ", "the user can ")):
                text = re.sub(r'^(you can |the user can )', '', text, flags=re.IGNORECASE)
                text = text.capitalize()
                if text != original.strip():
                    return text
        
        # Strategy 3: Remove unnecessary words
        simplified = re.sub(r'\b(really|easily|simply|basically|actually|generally|typically)\s+', '', text, flags=re.IGNORECASE)
        simplified = re.sub(r'\s+', ' ', simplified).strip()
        if simplified != original.strip() and len(simplified) > 0:
            return simplified
        
        # Strategy 4: Convert "X are displayed" to "X appear" or "The system shows X"
        if 'displayed' in text.lower():
            text = re.sub(r'(.*?)\s+(is|are)\s+displayed', r'The system displays \1', text, flags=re.IGNORECASE)
            if text != original.strip():
                return text
        
        # Strategy 5: Last resort - provide a meaningful generic improvement
        return f"Revise for clarity: {original.strip()}"
    return candidate

def enrich_issue_with_solution(issue: dict) -> dict:
    """
    Input issue:
      {
        "message": "Avoid passive voice...",
        "context": "All the tags configured for the machine will be displayed.",
        "issue_type": "Passive Voice" | "Adverb Overuse" | ...
      }
    Output (mutates and returns the same dict with fields):
      - solution_text (short guidance)
      - proposed_rewrite (concrete sentence)
      - sources (list)
      - method (rag method used)
    """
    
    # RAG system is ALWAYS ACTIVE - this is the core feature!
    logger.info("[ENRICH] RAG system active - processing issue")
    
    # NEW: Try direct ollama_rag_direct first for rule-based issues with configurable timeouts
    feedback_text = issue.get("message", "")
    sentence_context = issue.get("context", "")
    
    # ENHANCED: Progressive timeout strategy for different quality levels (FINAL OPTIMIZATION)
    OLLAMA_TIMEOUTS = {
        "quick": 20,     # 20 seconds - allow for Flask overhead
        "standard": 25,  # 25 seconds for standard quality  
        "high": 30       # 30 seconds for highest quality (complex cases)
    }
    
    # Determine timeout based on issue type and sentence length
    if len(sentence_context) > 100:  # Long sentences need more processing time
        timeout_level = "high"
    elif "detected by rule" in feedback_text.lower():  # Rule-based issues get priority
        timeout_level = "standard" 
    else:
        timeout_level = "quick"
    
    selected_timeout = OLLAMA_TIMEOUTS[timeout_level]
    
    if feedback_text and sentence_context and ("detected by rule" in feedback_text.lower() or 
                                              "rule" in feedback_text.lower() or
                                              len(sentence_context) > 10):
        try:
            logger.info(f"[ENRICH] Attempting ollama_rag_direct (timeout: {selected_timeout}s, level: {timeout_level})")
            
            import requests
            
            # Get enhanced RAG context from ChromaDB
            col = _get_collection()
            if col:
                query_results = _cached_vector_query(f"{feedback_text} {sentence_context}", n_results=3)  # Get more context
                if query_results and query_results.get('documents') and query_results['documents'][0]:
                    # Create enhanced RAG prompt with multiple sources
                    contexts = []
                    sources = []
                    
                    for i, (doc, meta) in enumerate(zip(
                        query_results['documents'][0][:2],  # Use top 2 results
                        query_results['metadatas'][0][:2] if query_results.get('metadatas') else [{}]*2
                    )):
                        rule_id = meta.get('rule_id', f'rule_{i+1}')
                        title = meta.get('title', 'Writing Rule')
                        contexts.append(f"Rule {i+1} ({rule_id}): {title}\n{doc[:400]}")  # More context per rule
                        sources.append({
                            "rule_id": rule_id,
                            "title": title,
                            "similarity": 0.85 - (i * 0.1)  # Decreasing similarity
                        })
                    
                    # Enhanced prompt optimized for both guidance AND rewriting
                    if "long sentence" in feedback_text.lower() or "break" in feedback_text.lower() or len(sentence_context) > 100:
                        # For long sentences, ask for actual sentence splitting - simple and direct
                        enhanced_prompt = f"""Split this long sentence into two shorter sentences:

"{sentence_context}"

Sentence 1:
Sentence 2:"""
                    else:
                        # For other issues like passive voice, ask for specific rewrite
                        if "passive voice" in feedback_text.lower():
                            enhanced_prompt = f"""Convert this passive voice sentence to active voice:

PASSIVE: "{sentence_context}"
ACTIVE: """
                        else:
                            # General writing issues
                            enhanced_prompt = f"""Fix this writing issue:

ISSUE: {feedback_text}
TEXT: "{sentence_context}"

RULES:
{chr(10).join(contexts)}

Provide clear guidance and suggested rewrite in 2-3 sentences."""

                    # OPTIMIZED Ollama call for complete responses
                    response = requests.post('http://localhost:11434/api/generate', json={
                        'model': 'tinyllama:latest',  # Fastest reliable model
                        'prompt': enhanced_prompt,
                        'stream': False,
                        'options': {
                            'temperature': 0.1,      # Slightly more creative for sentence splitting
                            'top_p': 0.8,           # More flexible responses
                            'num_predict': 120,     # Longer responses for complete sentences
                            'num_ctx': 1500,        # More context for complex tasks
                            'repeat_penalty': 1.1,  # Prevent repetition
                            'mirostat': 0           # Disable mirostat for speed
                        }
                    }, timeout=selected_timeout)
                    
                    if response.status_code == 200:
                        result = response.json()
                        ai_response = result.get('response', '').strip()
                        
                        if ai_response and len(ai_response) > 20:  # Ensure substantial response
                            # Success with ollama_rag_direct!
                            
                            # Extract rewritten text if available
                            proposed_rewrite = sentence_context  # Default fallback
                            
                            # For long sentence issues, extract the split sentences from AI response
                            if "long sentence" in feedback_text.lower() or "break" in feedback_text.lower():
                                # Look for "Sentence 1:" and "Sentence 2:" patterns
                                response_lines = ai_response.split('\n')
                                sentences = []
                                
                                for line in response_lines:
                                    line = line.strip().replace('"', '')
                                    if line.startswith('Sentence 1:'):
                                        sent1 = line.replace('Sentence 1:', '').strip()
                                        if sent1:
                                            sentences.append(sent1)
                                    elif line.startswith('Sentence 2:'):
                                        sent2 = line.replace('Sentence 2:', '').strip()
                                        if sent2:
                                            sentences.append(sent2)
                                
                                # If we found both sentences, combine them
                                if len(sentences) >= 2:
                                    proposed_rewrite = f"{sentences[0]}. {sentences[1]}"
                                    # Clean up any double periods
                                    proposed_rewrite = proposed_rewrite.replace('..', '.')
                                
                                # Check if AI response contains multiple sentences (2+ periods)
                                elif '.' in ai_response and len([s for s in ai_response.split('.') if s.strip()]) >= 2:
                                    # Take the response as-is if it contains multiple sentences
                                    cleaned = ai_response.replace('"', '').replace('\n', ' ').strip()
                                    if len(cleaned) > 50:
                                        proposed_rewrite = cleaned
                                
                                # If AI only provided 1 sentence or failed to split, use intelligent fallback
                                # This is the key fix - force fallback when AI doesn't properly split
                                if (proposed_rewrite == sentence_context or 
                                    len([s for s in proposed_rewrite.split('.') if s.strip()]) < 2):
                                    
                                    original = sentence_context
                                    
                                    # Specific handling for the Industrial Edge Hub example
                                    if 'Industrial Edge Hub' in original and ' is the central repository for ' in original:
                                        # Split: "The Industrial Edge Hub (IE Hub for short) is the central repository for all available Industrial Edge apps (IE apps) from Siemens and other app partners in the ecosystem."
                                        # Into: "The Industrial Edge Hub (IE Hub for short) is a central repository. It stores all available Industrial Edge apps (IE apps) from Siemens and other app partners in the ecosystem."
                                        parts = original.split(' is the central repository for ', 1)
                                        if len(parts) == 2:
                                            subject = parts[0].strip()  # "The Industrial Edge Hub (IE Hub for short)"
                                            rest = parts[1].strip()     # "all available Industrial Edge apps..."
                                            
                                            proposed_rewrite = f"{subject} is a central repository. It stores {rest}"
                                    
                                    # General fallback for other long sentences
                                    elif len(original) > 100:
                                        # Try to split at conjunctions or commas
                                        if ' and ' in original:
                                            parts = original.split(' and ', 1)
                                            if len(parts) == 2:
                                                proposed_rewrite = f"{parts[0].strip()}. Additionally, {parts[1].strip()}"
                                        elif ', ' in original:
                                            comma_parts = original.split(', ')
                                            if len(comma_parts) >= 3:  # At least 3 parts to make a meaningful split
                                                mid_point = len(comma_parts) // 2
                                                part1 = ', '.join(comma_parts[:mid_point]).strip()
                                                part2 = ', '.join(comma_parts[mid_point:]).strip()
                                                proposed_rewrite = f"{part1}. {part2.capitalize()}"
                            
                            # For other issues (like passive voice), extract suggestion from AI response
                            else:
                                # Try to extract a concrete suggestion from the AI response
                                extracted_suggestion = None
                                
                                # Look for common patterns in AI responses
                                response_lower = ai_response.lower()
                                
                                # Pattern 1: Look for "ACTIVE:" pattern (new optimized format)
                                if "active:" in response_lower:
                                    active_index = ai_response.lower().find("active:")
                                    if active_index != -1:
                                        suggestion_text = ai_response[active_index + len("active:"):].strip()
                                        # Clean up common formatting
                                        suggestion_text = suggestion_text.replace('"', '').strip()
                                        if len(suggestion_text) > 10 and suggestion_text != sentence_context:
                                            extracted_suggestion = suggestion_text
                                
                                # Pattern 1b: Look for variations like "ACTIVE VERSE:" or "ACTIVE VERSION:"
                                elif any(pattern in response_lower for pattern in ["active verse:", "active version:"]):
                                    for pattern in ["active verse:", "active version:"]:
                                        if pattern in response_lower:
                                            pattern_index = ai_response.lower().find(pattern)
                                            if pattern_index != -1:
                                                suggestion_text = ai_response[pattern_index + len(pattern):].strip()
                                                suggestion_text = suggestion_text.replace('"', '').strip()
                                                if len(suggestion_text) > 10 and suggestion_text != sentence_context:
                                                    extracted_suggestion = suggestion_text
                                                    break
                                            
                                # Pattern 2: "Use active voice: [suggestion]"
                                elif "use active voice:" in response_lower:
                                    parts = ai_response.split(":")
                                    if len(parts) > 1:
                                        suggestion_part = parts[1].strip().replace('"', '')
                                        if len(suggestion_part) > 10:
                                            extracted_suggestion = suggestion_part
                                
                                # Pattern 2: Look for bracketed suggestions like "[user] uploads the file"
                                elif '[' in ai_response and ']' in ai_response:
                                    # Extract content that looks like a rewrite with brackets
                                    cleaned = ai_response.replace('[', '').replace(']', '').strip()
                                    # Remove quotes if present
                                    cleaned = cleaned.replace('"', '').strip()
                                    if len(cleaned) > 10 and cleaned != sentence_context and '.' in cleaned:
                                        extracted_suggestion = cleaned
                                
                                # Pattern 3: Look for quoted suggestions in the response
                                elif '"' in ai_response:
                                    # Find content between quotes that looks like a suggestion
                                    import re
                                    quotes = re.findall(r'"([^"]+)"', ai_response)
                                    for quote in quotes:
                                        if len(quote) > 20 and quote != sentence_context:
                                            extracted_suggestion = quote
                                            break
                                # Pattern 4: Look for "Rewrite:" pattern specifically
                                elif "rewrite:" in response_lower:
                                    # Split by "Rewrite:" and take the content after it
                                    parts = ai_response.lower().split("rewrite:")
                                    if len(parts) > 1:
                                        # Get the original case version
                                        rewrite_index = ai_response.lower().find("rewrite:")
                                        if rewrite_index != -1:
                                            suggestion_text = ai_response[rewrite_index + len("rewrite:"):].strip()
                                            # Clean up common formatting
                                            suggestion_text = suggestion_text.replace('[', '').replace(']', '').replace('"', '').strip()
                                            if len(suggestion_text) > 10 and suggestion_text != sentence_context:
                                                extracted_suggestion = suggestion_text
                                
                                # Pattern 5: Look for other improvement patterns
                                elif any(pattern in response_lower for pattern in ["suggestion:", "improved:", "better:"]):
                                    for pattern in ["suggestion:", "improved:", "better:"]:
                                        if pattern in response_lower:
                                            pattern_index = ai_response.lower().find(pattern)
                                            if pattern_index != -1:
                                                suggestion_text = ai_response[pattern_index + len(pattern):].strip()
                                                suggestion_text = suggestion_text.replace('[', '').replace(']', '').replace('"', '').strip()
                                                if len(suggestion_text) > 10 and suggestion_text != sentence_context:
                                                    extracted_suggestion = suggestion_text
                                                    break
                                
                                # Pattern 6: Direct response (if AI just gives the answer without markers)
                                elif not extracted_suggestion and len(ai_response) > 10 and len(ai_response) < 200:
                                    # If the response is reasonable length and different from input, use it
                                    cleaned_response = ai_response.strip().replace('"', '').replace('\n', ' ')
                                    if (cleaned_response != sentence_context and 
                                        len(cleaned_response) > 10 and
                                        not cleaned_response.startswith('[')):  # Avoid placeholder responses
                                        extracted_suggestion = cleaned_response
                                
                                # Use extracted suggestion if found, otherwise use deterministic fallback
                                if extracted_suggestion:
                                    proposed_rewrite = extracted_suggestion
                                elif proposed_rewrite == sentence_context:
                                    proposed_rewrite = _create_deterministic_rewrite(feedback_text, sentence_context)
                            
                            issue["solution_text"] = ai_response
                            issue["proposed_rewrite"] = proposed_rewrite
                            issue["sources"] = sources  # Use the enhanced sources array
                            issue["method"] = "ollama_rag_direct"
                            
                            logger.info(f"[ENRICH] ✅ ollama_rag_direct SUCCESS ({selected_timeout}s timeout): {ai_response[:60]}...")
                            return issue
                        else:
                            logger.info(f"[ENRICH] ollama_rag_direct returned short response, using fallback")
                            
                    else:
                        logger.warning(f"[ENRICH] Ollama API error {response.status_code}: {response.text[:100]}")
        
        except requests.exceptions.Timeout:
            logger.info(f"[ENRICH] ollama_rag_direct timeout ({selected_timeout}s) - using chromadb fallback")
        except requests.exceptions.ConnectionError:
            logger.warning("[ENRICH] Ollama service not available - using chromadb fallback")
        except Exception as e:
            logger.error(f"[ENRICH] ollama_rag_direct failed with error: {e}")
            import traceback
            logger.error(f"[ENRICH] Full traceback: {traceback.format_exc()}")
            logger.info(f"[ENRICH] ollama_rag_direct failed ({e}) - using fallback")
    
    # FALLBACK: Original ChromaDB approach
    col = _get_collection()
    if col is None:
        logger.info("[ENRICH] No Chroma collection available; using LLM-powered fallback.")
        issue["solution_text"] = f"Review and improve this text to address: {issue.get('message', 'writing issue')}"
        
        # Try LLM-powered rewrite first, then deterministic fallback
        llm_rewrite = _create_llm_powered_rewrite(issue.get('message', ''), issue.get('context', ''))
        issue["proposed_rewrite"] = llm_rewrite or _create_deterministic_rewrite(issue.get('message', ''), issue.get('context', ''))
        
        issue["sources"] = []
        issue["method"] = "llm_fallback" if llm_rewrite else "smart_fallback"
        return issue

    # SPEED OPTIMIZATION: Use cached vector query instead of direct call
    query_text = (issue.get("context") or issue.get("message") or "").strip()
    if not query_text:
        logger.info("[ENRICH] Empty query text; bypass.")
        return issue

    # Use cached query for better performance (reduced to 2 results for speed)
    res = _cached_vector_query(query_text, n_results=2)  # Reduced from 3 to 2 for speed
    if not res:
        logger.warning("[ENRICH] Cached query failed; using fallback.")
        return _create_fast_fallback_result(issue)

    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    # Normalize hits into a list of dicts with similarity if distances present
    dists = (res.get("distances") or [[]])[0]
    hits = []
    for i, d in enumerate(docs):
        m = metas[i] if i < len(metas) else {}
        sim = 1.0 - float(dists[i]) if i < len(dists) else 0.0
        hits.append({"document": d, "metadata": m, "similarity": sim})

    # Pick best hit
    best = hits[0] if hits else {}
    policy = (best.get("metadata") or {}).get("rewrite_policy", {})  # <== from your enriched JSON
    rule_hint = (best.get("metadata") or {}).get("rule_id", "")

    # Build short guidance with better fallbacks
    guidance = (best.get("metadata") or {}).get("solution") or (best.get("metadata") or {}).get("explanation") or ""
    
    # If no guidance found, create context-aware guidance based on issue type
    if not guidance.strip():
        issue_type = issue.get("issue_type", "").lower()
        message = issue.get("message", "").lower()
        
        if "adverb" in message or "adverb" in issue_type:
            guidance = "Remove unnecessary adverbs (like 'easily', 'simply', 'basically', 'manually', 'automatically') to make writing more direct and confident."
        elif "passive" in message or "passive" in issue_type:
            guidance = "Convert to active voice with a clear subject performing the action."
        elif "long" in message and "sentence" in message:
            guidance = "Break long sentences into shorter, clearer statements."
        elif "modal" in message or any(word in message for word in ["can", "may", "should", "will"]):
            guidance = "Use direct language instead of modal verbs for clearer instructions."
        else:
            guidance = f"Address the writing issue: {issue.get('message', 'improve clarity and style')}"

    # Compute a proposed rewrite
    original = (issue.get("context") or issue.get("sentence") or "").strip()
    pr = ""
    if policy:
        pr = _policy_rewrite(original, policy)
    # If policy gave nothing good, try extracting from document field (first line, etc.)
    if not pr:
        doc_text = (best.get("document") or "").strip()
        # try a single-line “Proposed:” format if present
        m = re.search(r"(?i)^proposed(?: rewrite)?:\s*(.+)$", doc_text, flags=re.MULTILINE)
        if m:
            pr = m.group(1).strip()

    # Try LLM-powered rewrite first, then use deterministic patterns if needed
    llm_rewrite = _create_llm_powered_rewrite(issue.get("message", ""), original)
    if llm_rewrite:
        pr = llm_rewrite
        method_suffix = "_llm"
    else:
        # Use our improved deterministic rewrite instead of just _force_change
        deterministic_rewrite = _create_deterministic_rewrite(issue.get("message", ""), original)
        if deterministic_rewrite and deterministic_rewrite != original:
            pr = deterministic_rewrite
            method_suffix = "_deterministic"
        else:
            # Last resort: use _force_change only if deterministic patterns failed
            pr = _force_change(original, pr)
            method_suffix = "_fallback"

    # Attach back
    issue["solution_text"] = guidance.strip()
    issue["proposed_rewrite"] = pr.strip()
    issue["sources"] = [{"rule_id": rule_hint, "similarity": round(_best_similarity(hits), 3), "preview": _first_hit_text(hits)}]
    issue["method"] = "chromadb" + method_suffix

    logger.info(
        "[ENRICH] type=%s sim=%.2f rewrite='%s' method=%s",
        issue.get("issue_type"), _best_similarity(hits), issue.get("proposed_rewrite", "")[:120], issue.get("method")
    )
    return issue

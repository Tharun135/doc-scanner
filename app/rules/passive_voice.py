import re
import spacy
from bs4 import BeautifulSoup
import html
import json
import requests
import os
import logging
from typing import Optional

<<<<<<< HEAD
# AI functionality now uses OpenAI instead of Ollama
AI_AVAILABLE = True
try:
    import openai
    import os
except ImportError:
    # OpenAI not available, will use offline methods only
    AI_AVAILABLE = False
    openai = None
=======
# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag_advanced, detect_passive_voice_issues
    RAG_HELPER_AVAILABLE = True  # RAG enabled
except ImportError:
    RAG_HELPER_AVAILABLE = False
>>>>>>> 96cc86a16e63ddab59591eb3e60015e1d0b5ea16

logger = logging.getLogger(__name__)

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except OSError:
    logger.warning("spaCy English model not available. Using pattern-based detection only.")
    nlp = None
    SPACY_AVAILABLE = False

def check(content):
    """
    Check for passive voice issues using RAG with smart fallback.
    Primary: RAG-enhanced suggestions
    Fallback: Rule-based passive voice detection
    """
    
    # Use RAG-enhanced checking if available
    if RAG_HELPER_AVAILABLE:
        logger.info("Using RAG-enhanced passive voice checking")
        
        rule_patterns = {
            'detect_function': detect_passive_voice_issues
        }
        
        fallback_suggestions = [
            "Convert passive voice to active voice for clearer, more direct communication. Example: Change 'The report was written by John' to 'John wrote the report'."
        ]
        
        return check_with_rag_advanced(
            content=content,
            rule_patterns=rule_patterns,
            rule_name="passive_voice",
            fallback_suggestions=fallback_suggestions
        )
    
    # Legacy fallback when RAG helper is not available
    logger.warning("RAG helper not available, using legacy passive voice detection")
    return check_legacy_passive_voice(content)

def check_legacy_passive_voice(content):
    """Legacy passive voice detection for fallback when RAG is not available."""
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # If spaCy is available, use it for sentence parsing
    if SPACY_AVAILABLE and nlp:
        try:
            doc = nlp(text_content)
            sentences = list(doc.sents)
        except Exception as e:
            logger.error(f"spaCy processing failed: {e}")
            # Fall back to simple sentence splitting
            sentences = [text_content]  # Process as single text block
    else:
        # Simple sentence splitting fallback
        import re
        sentence_endings = re.split(r'[.!?]+', text_content)
        sentences = [s.strip() for s in sentence_endings if s.strip()]
    
<<<<<<< HEAD
    # Rule: Detect passive voice and provide LLM-generated active voice rewrites
=======
    # Rule: Detect passive voice and provide basic suggestions
>>>>>>> 96cc86a16e63ddab59591eb3e60015e1d0b5ea16
    for sent in sentences:
        if SPACY_AVAILABLE and hasattr(sent, 'text'):
            sent_text = sent.text.strip()
            # Check spaCy-based passive detection
            spacy_passive = any(token.dep_ == "auxpass" for token in sent)
        else:
            sent_text = str(sent).strip()
            spacy_passive = False
        
        # Clean the sentence text
        clean_sentence = BeautifulSoup(sent_text, "html.parser").get_text()
        clean_sentence = html.unescape(clean_sentence)
        
        # Check both spaCy and pattern-based detection
        if spacy_passive or is_passive_voice_pattern(clean_sentence):
            # Identify specific passive construction for clear issue description
            passive_phrase = identify_passive_construction(clean_sentence)
            if passive_phrase:
                suggestions.append(f"Passive voice detected: '{passive_phrase}' - convert to active voice for clearer, more direct communication.")
            else:
                suggestions.append("Passive voice detected - convert to active voice for clearer, more direct communication.")
    
    return suggestions if suggestions else []

def is_passive_voice_pattern(sentence):
    """Additional pattern-based detection for passive voice constructions."""
    passive_patterns = [
        r'\bis\s+\w+ed\b',  # "is needed", "is required"
        r'\bare\s+\w+ed\b',  # "are needed", "are required"
        r'\bwas\s+\w+ed\b', # "was created", "was developed"
        r'\bwere\s+\w+ed\b', # "were created", "were developed"
        r'\bhas\s+been\s+\w+ed\b', # "has been created"
        r'\bhave\s+been\s+\w+ed\b', # "have been created"
        r'\bbeing\s+\w+ed\b', # "being processed"
        r'\bto\s+be\s+\w+ed\b', # "to be processed"
        r'\bit\s+is\s+utilized\b', # "it is utilized"
        r'\bit\s+is\s+used\b', # "it is used"
        r'\bneeds\s+to\s+be\s+\w+ed\b', # "needs to be converted"
        r'\bneed\s+to\s+be\s+\w+ed\b', # "need to be converted"
    ]
    
    for pattern in passive_patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            return True
    return False

def generate_active_voice_with_llm(passive_sentence):
    """
    Use an LLM to convert passive voice to active voice.
    This function tries multiple approaches: LLM, enhanced offline logic, then fallback.
    """
    try:
        # First try LLM-based conversion for most natural results
        llm_result = convert_with_llm_api(passive_sentence)
        if llm_result and llm_result != passive_sentence:
            return llm_result
            
        # If LLM fails, try enhanced offline conversion
        offline_result = convert_with_offline_logic(passive_sentence)
        if offline_result and offline_result != passive_sentence:
            return offline_result
            
        # If all fails, return None to use generic fallback
        return None
        
    except Exception as e:
        logger.error(f"Error in LLM passive voice conversion: {e}")
        return None

def convert_with_llm_api(passive_sentence: str) -> Optional[str]:
    """
    Convert passive voice to active voice using AI (now handled by main AI system).
    This function is deprecated - passive voice conversion is now handled
    by the enhanced AI system in ai_improvement.py
    """
    # Skip AI conversion here - it's now handled by the main AI system
    logger.debug("Passive voice AI conversion now handled by main AI system")
    return None

def convert_with_offline_logic(passive_sentence):
    """
    Enhanced offline logic for converting passive to active voice.
    This uses pattern-based approach when spaCy is not available.
    """
    try:
        # First try the enhanced pattern-based rewriter
        enhanced_result = create_active_voice_rewrite_enhanced(None, passive_sentence)
        if enhanced_result:
            return enhanced_result
        
        # If spaCy is available, try the spaCy-based approach
        if SPACY_AVAILABLE and nlp:
            doc = nlp(passive_sentence)
            
            # Look for passive constructions more broadly
            for token in doc:
                # Find "is/are/was/were + past participle" patterns
                if (token.lemma_ in ["be"] and 
                    token.i + 1 < len(doc) and 
                    doc[token.i + 1].tag_ in ["VBN"]):  # Past participle
                    
                    return create_active_voice_rewrite_enhanced(doc, passive_sentence)
                    
                # Find "has/have been + past participle" patterns
                elif (token.lemma_ in ["have"] and 
                      token.i + 2 < len(doc) and 
                      doc[token.i + 1].lemma_ == "be" and
                      doc[token.i + 2].tag_ == "VBN"):
                    
                    return create_active_voice_rewrite_enhanced(doc, passive_sentence)
        
        return None
        
    except Exception as e:
        logger.error(f"Error in offline passive voice conversion: {e}")
        return None

def create_active_voice_rewrite_enhanced(doc, original_sentence):
    """
    Enhanced active voice rewrite with better pattern recognition.
    """
    try:
        # Common rewrite patterns based on sentence structure
        sentence_lower = original_sentence.lower()
        
        # Pattern 0: "It is utilized when..." -> "Use it when..."
        if re.search(r'it\s+is\s+utilized\s+when', sentence_lower):
            rewrite = re.sub(r'it\s+is\s+utilized\s+when\s+(.+)', 
                           r'Use it when \1', 
                           original_sentence, flags=re.IGNORECASE)
            return rewrite
        
        # Pattern 0b: "It is used when..." -> "Use it when..."
        if re.search(r'it\s+is\s+used\s+when', sentence_lower):
            rewrite = re.sub(r'it\s+is\s+used\s+when\s+(.+)', 
                           r'Use it when \1', 
                           original_sentence, flags=re.IGNORECASE)
            return rewrite
        
        # Pattern 1: "This tool is needed to..." -> "You need this tool to..."
        if re.search(r'this\s+\w+\s+is\s+needed\s+to', sentence_lower):
            rewrite = re.sub(r'this\s+(\w+)\s+is\s+needed\s+to\s+(.+)', 
                           r'You need this \1 to \2', 
                           original_sentence, flags=re.IGNORECASE)
            return rewrite
        
        # Pattern 1b: "X needs to be converted" -> "You need to convert X"
        if re.search(r'(.+?)\s+needs?\s+to\s+be\s+(\w+ed)', sentence_lower):
            match = re.search(r'(.+?)\s+needs?\s+to\s+be\s+(\w+ed)(.+)', sentence_lower)
            if match:
                object_part = match.group(1).strip()
                verb = match.group(2)
                remainder = match.group(3).strip()
                
                verb_active = convert_passive_verb_to_active(verb)
                if remainder:
                    return f"You need to {verb_active} {object_part}{remainder}."
                else:
                    return f"You need to {verb_active} {object_part}."
        
        # Pattern 2: "X is required to..." -> "You must use X to..."
        if re.search(r'\w+\s+is\s+required\s+to', sentence_lower):
            rewrite = re.sub(r'(\w+)\s+is\s+required\s+to\s+(.+)', 
                           r'You must use \1 to \2', 
                           original_sentence, flags=re.IGNORECASE)
            return rewrite
        
        # Pattern 3: "The file was created by X" -> "X created the file"
        by_match = re.search(r'(.+?)\s+was\s+(\w+ed)\s+by\s+(.+)', sentence_lower)
        if by_match:
            object_part = by_match.group(1).strip()
            verb = by_match.group(2)
            actor = by_match.group(3).strip()
            
            # Convert verb to active form and clean up capitalization
            verb_active = convert_passive_verb_to_active(verb)
            actor_clean = actor.replace('.', '').strip()
            
            # Handle proper capitalization for actors
            if not actor_clean.lower().startswith('the'):
                actor_clean = actor_clean.title()
                
            # Use past tense for "was" constructions
            past_tense_verbs = {
                "create": "created", "finish": "finished", "complete": "completed", 
                "generate": "generated", "develop": "developed", "test": "tested"
            }
            verb_final = past_tense_verbs.get(verb_active, verb_active + "d")
            
            result = f"{actor_clean} {verb_final} {object_part}."
            return result[0].upper() + result[1:]  # Ensure first letter is capitalized
        
        # Pattern 4: "Settings are configured..." -> "The administrator configures settings..."
        if re.search(r'(\w+)\s+are\s+(\w+ed)', sentence_lower):
            # Use context-based actor assignment
            actor = determine_likely_actor(original_sentence)
            
            # Extract the main components
            match = re.search(r'(\w+)\s+are\s+(\w+ed)(.+)', sentence_lower)
            if match:
                object_word = match.group(1)
                verb = match.group(2)
                remainder = match.group(3).strip()
                
                verb_active = convert_passive_verb_to_active(verb)
                verb_conjugated = conjugate_verb_for_actor(verb_active, actor)
                
                if remainder and not remainder.startswith('.'):
                    return f"{actor} {verb_conjugated} {object_word} {remainder}."
                else:
                    return f"{actor} {verb_conjugated} {object_word}."
        
        # Pattern 5: "The system is configured..." -> "The administrator configures the system..."
        if re.search(r'the\s+(\w+)\s+is\s+(\w+ed)', sentence_lower):
            actor = determine_likely_actor(original_sentence)
            
            match = re.search(r'the\s+(\w+)\s+is\s+(\w+ed)(.+)', sentence_lower)
            if match:
                object_word = match.group(1)
                verb = match.group(2)
                remainder = match.group(3).strip()
                
                verb_active = convert_passive_verb_to_active(verb)
                verb_conjugated = conjugate_verb_for_actor(verb_active, actor)
                
                if remainder and not remainder.startswith('.'):
                    return f"{actor} {verb_conjugated} the {object_word} {remainder}."
                else:
                    return f"{actor} {verb_conjugated} the {object_word}."
        
        # Pattern 6: "X are required for..." -> "You need X for..."
        if re.search(r'(\w+)\s+are\s+required\s+for', sentence_lower):
            match = re.search(r'(\w+)\s+are\s+required\s+for\s+(.+)', sentence_lower)
            if match:
                object_word = match.group(1)
                remainder = match.group(2).strip()
                return f"You need {object_word} for {remainder}."
                
        # Pattern 6b: "X are required to..." -> "You need X to..."
        if re.search(r'(\w+)\s+are\s+required\s+to', sentence_lower):
            match = re.search(r'(\w+)\s+are\s+required\s+to\s+(.+)', sentence_lower)
            if match:
                object_word = match.group(1)
                remainder = match.group(2).strip()
                return f"You need {object_word} to {remainder}."
        
        # Pattern 7: "X is backed up..." -> "The system backs up X..."
        if re.search(r'the\s+(\w+)\s+is\s+backed\s+up', sentence_lower):
            match = re.search(r'the\s+(\w+)\s+is\s+backed\s+up(.+)', sentence_lower)
            if match:
                object_word = match.group(1)
                remainder = match.group(2).strip()
                actor = "The system"
                verb_conjugated = conjugate_verb_for_actor("back up", actor)
                
                if remainder and not remainder.startswith('.'):
                    return f"{actor} {verb_conjugated} the {object_word} {remainder}."
                else:
                    return f"{actor} {verb_conjugated} the {object_word}."
        
        return None
        
    except Exception:
        return None

def convert_passive_verb_to_active(passive_verb):
    """Convert passive verb forms to active equivalents."""
    verb_conversions = {
        "needed": "need",
        "required": "require", 
        "created": "create",
        "generated": "generate",
        "configured": "configure",
        "developed": "develop",
        "exported": "export",
        "installed": "install",
        "executed": "execute",
        "tested": "test",
        "updated": "update",
        "modified": "modify",
        "processed": "process",
        "analyzed": "analyze",
        "designed": "design",
        "implemented": "implement",
        "written": "write",
        "used": "use",
        "deployed": "deploy",
        "finished": "finish",
        "completed": "complete"
    }
    
    return verb_conversions.get(passive_verb.lower(), passive_verb)

def determine_likely_actor(sentence):
    """Determine the most likely actor based on sentence context."""
    sentence_lower = sentence.lower()
    
    if any(word in sentence_lower for word in ["tool", "utility", "application"]):
        return "You"
    elif any(word in sentence_lower for word in ["system", "server", "network"]):
        return "The administrator"
    elif any(word in sentence_lower for word in ["file", "document", "report"]):
        return "The user"
    elif any(word in sentence_lower for word in ["code", "program", "script"]):
        return "The developer"
    elif any(word in sentence_lower for word in ["configuration", "setting", "parameter"]):
        return "The user"
    elif any(word in sentence_lower for word in ["test", "validation", "verification"]):
        return "The tester"
    else:
        return "The user"

def conjugate_verb_for_actor(verb, actor):
    """Conjugate verb based on the actor (subject)."""
    actor_lower = actor.lower()
    
    # Handle special cases first
    if verb == "back up":
        if actor_lower in ['the user', 'the administrator', 'the developer', 'the tester', 'the system']:
            return "backs up"
        else:
            return "back up"
    
    # Third person singular subjects need 's' ending
    if actor_lower in ['the user', 'the administrator', 'the developer', 'the tester', 'the system']:
        # Add 's' for third person singular
        if verb.endswith('e'):
            return verb + 's'
        elif verb.endswith('y'):
            return verb[:-1] + 'ies'
        elif verb.endswith(('s', 'sh', 'ch', 'x', 'z')):
            return verb + 'es'
        else:
            return verb + 's'
    else:
        # First/second person or plural (you, we, they) - use base form
        return verb

def identify_passive_construction(sentence):
    """Identify the specific passive voice construction in a sentence for clearer feedback."""
    # Common passive voice patterns with their identifying phrases
    passive_patterns = [
        (r'\bis\s+(\w+ed|being\s+\w+ed)\b', 'is'),
        (r'\bare\s+(\w+ed|being\s+\w+ed)\b', 'are'), 
        (r'\bwas\s+(\w+ed|being\s+\w+ed)\b', 'was'),
        (r'\bwere\s+(\w+ed|being\s+\w+ed)\b', 'were'),
        (r'\bhas\s+been\s+(\w+ed)\b', 'has been'),
        (r'\bhave\s+been\s+(\w+ed)\b', 'have been'),
        (r'\bbeing\s+(\w+ed)\b', 'being'),
        (r'\bto\s+be\s+(\w+ed)\b', 'to be'),
        (r'\bwill\s+be\s+(\w+ed)\b', 'will be'),
        (r'\bcan\s+be\s+(\w+ed)\b', 'can be'),
        (r'\bmay\s+be\s+(\w+ed)\b', 'may be'),
        (r'\bmust\s+be\s+(\w+ed)\b', 'must be'),
        (r'\bshould\s+be\s+(\w+ed)\b', 'should be'),
        (r'\bwould\s+be\s+(\w+ed)\b', 'would be'),
        (r'\bcould\s+be\s+(\w+ed)\b', 'could be'),
    ]
    
    for pattern, construction_type in passive_patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            # Return the specific passive construction found
            full_match = match.group(0)
            return full_match
    
    return None
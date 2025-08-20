import re
import spacy
from bs4 import BeautifulSoup
import html
from spacy.language import Language
from spacy.tokens import Span
import logging

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag_advanced, detect_long_sentence_issues
    RAG_HELPER_AVAILABLE = True  # RAG enabled
except ImportError:
    RAG_HELPER_AVAILABLE = False
    RAG_HELPER_AVAILABLE = False  # Temporarily disabled for performance
except ImportError:
    RAG_HELPER_AVAILABLE = False

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

logger = logging.getLogger(__name__)

# Custom sentence segmentation component
@Language.component("custom_sentencizer")
def custom_sentencizer(doc):
    for i, token in enumerate(doc[:-1]):
        if token.text in {".", ":", "-"}:
            doc[i + 1].is_sent_start = True
    return doc

# Add custom sentencizer to the pipeline
nlp.add_pipe("custom_sentencizer", before="parser")

def check(content):
    """
    Check for long sentences using RAG with smart fallback.
    Primary: RAG-enhanced suggestions for sentence breaking
    Fallback: Rule-based long sentence detection with basic splitting suggestions
    """
    
    # Temporarily disable RAG for performance - use legacy approach
    RAG_AVAILABLE_FOR_THIS_RULE = False  # Set to True to re-enable RAG
    
    # Use RAG-enhanced checking if available
    if RAG_HELPER_AVAILABLE and RAG_AVAILABLE_FOR_THIS_RULE:
        logger.info("Using RAG-enhanced long sentence checking")
        
        rule_patterns = {
            'detect_function': detect_long_sentence_issues
        }
        
        fallback_suggestions = [
            "Break this long sentence into shorter ones for better readability. Aim for 15-20 words per sentence."
        ]
        
        return check_with_rag_advanced(
            content=content,
            rule_patterns=rule_patterns,
            rule_name="long_sentences",
            fallback_suggestions=fallback_suggestions
        )
    
    # Legacy fallback when RAG helper is not available
    logger.warning("RAG helper not available, using legacy long sentence detection")
    return check_legacy_long_sentences(content)

def check_legacy_long_sentences(content):
    """Legacy long sentence detection for fallback when RAG is not available."""
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    doc = nlp(text_content)
    
    # Rule 1: Keep sentences under 25 words
    for sent in doc.sents:
        word_count = len([token for token in sent if not token.is_punct])
        if word_count > 25:
            clean_sentence = BeautifulSoup(sent.text.strip(), "html.parser").get_text()
            clean_sentence = html.unescape(clean_sentence)
            
            suggestions.append(f"Issue: Long sentence detected ({word_count} words). Consider breaking this into shorter sentences for better readability.")

    return suggestions if suggestions else []

def break_long_sentence_with_ai(sentence: str, word_count: int) -> str:
    """
    AI-based sentence breaking is now handled by the main AI system.
    This function is deprecated.
    
    Args:
        sentence: The original long sentence
        word_count: Number of words in the sentence
    
    Returns:
        None (AI processing moved to main system)
    """
    # AI sentence breaking is now handled by the enhanced AI system
    logger.debug("AI sentence breaking now handled by main AI system")
    return None
    try:
        # Create a focused prompt for sentence breaking
        prompt = f"""You are a writing expert. Break this long sentence ({word_count} words) into 2-3 shorter, clearer sentences while preserving the exact meaning and all information. Each sentence must be grammatically complete and correct.

Original sentence: "{sentence}"

Rules:
1. Keep all the original information and meaning
2. Make sentences flow naturally and grammatically correct
3. Each sentence must have a subject and verb (complete sentences only)
4. Use proper punctuation and capitalization
5. Aim for 15-20 words per sentence
6. Ensure the second sentence is not a fragment - it should be a complete, standalone sentence
7. Only return the improved text, no explanations

Improved version:"""

        # Try to get AI response
        try:
            response = ollama.chat(
                model='mistral',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.3, 'top_p': 0.9}
            )
            
            improved_text = response['message']['content'].strip()
            
            # Basic validation - ensure we got actual content
            if improved_text and len(improved_text) > 10 and improved_text != sentence:
                # Remove any explanatory text that might have been added
                if improved_text.startswith('"') and improved_text.endswith('"'):
                    improved_text = improved_text[1:-1]
                
                # Clean up any unwanted prefixes
                prefixes_to_remove = [
                    "Improved version:",
                    "Here's the improved version:",
                    "Broken down:",
                    "Revised:",
                ]
                
                for prefix in prefixes_to_remove:
                    if improved_text.startswith(prefix):
                        improved_text = improved_text[len(prefix):].strip()
                
                return improved_text
            
        except Exception as ai_error:
            logger.warning(f"AI service error: {ai_error}")
            
        # Fallback: Basic sentence breaking using logical patterns
        return break_sentence_with_rules(sentence)
        
    except Exception as e:
        logger.error(f"Error in break_long_sentence_with_ai: {e}")
        return break_sentence_with_rules(sentence)

def break_sentence_with_rules(sentence: str) -> str:
    """
    Fallback method to break sentences using rule-based patterns.
    Ensures all broken sentences are grammatically correct and complete.
    """
    
    # Pattern 1: Handle "X is the central repository for Y" pattern
    repository_match = re.search(r'(.+?)\s+is\s+the\s+central\s+repository\s+for\s+(.+)', sentence, re.IGNORECASE)
    if repository_match:
        subject = repository_match.group(1).strip()
        for_clause = repository_match.group(2).strip()
        
        first_sentence = f"{subject} is the central repository"
        second_sentence = f"It contains {for_clause}"
        return f"{first_sentence}. {second_sentence}"
    
    # Pattern 2: Handle "X, which Y, must Z" pattern
    which_must_match = re.search(r'(.+?),\s*which\s+([^,]+),\s*must\s+(.+)', sentence, re.IGNORECASE)
    if which_must_match:
        main_subject = which_must_match.group(1).strip()
        which_clause = which_must_match.group(2).strip()
        must_clause = which_must_match.group(3).strip()
        
        first_sentence = f"{main_subject} {which_clause}"
        second_sentence = f"It must {must_clause}"
        return f"{first_sentence}. {second_sentence}"
    
    # Pattern 3: Handle "X includes A, B, C, and Y" pattern
    includes_match = re.search(r'(.+?)\s+(includes?|contains?)\s+(.+)', sentence, re.IGNORECASE)
    if includes_match and ' and ' in sentence:
        subject = includes_match.group(1).strip()
        verb = includes_match.group(2).strip()
        items = includes_match.group(3).strip()
        
        # Find the last "and" for natural break
        last_and_pos = items.rfind(' and ')
        if last_and_pos > len(items) * 0.4:  # Make sure it's not too early
            first_items = items[:last_and_pos].strip().rstrip(',')  # Remove trailing comma
            last_item = items[last_and_pos + 5:].strip()  # Skip " and "
            
            first_sentence = f"{subject} {verb} {first_items}"
            second_sentence = f"It also {verb.lower()} {last_item}"
            return f"{first_sentence}. {second_sentence}"
    
    # Pattern 4: Handle "X specifies A, B, C, and Y that Z" pattern
    specifies_match = re.search(r'(.+?)\s+(specifies?|defines?)\s+(.+?)\s+that\s+(.+)', sentence, re.IGNORECASE)
    if specifies_match:
        subject = specifies_match.group(1).strip()
        verb = specifies_match.group(2).strip()
        items = specifies_match.group(3).strip()
        that_clause = specifies_match.group(4).strip()
        
        # If there are multiple items, try to break at the last "and"
        if ' and ' in items:
            last_and_pos = items.rfind(' and ')
            if last_and_pos > len(items) * 0.4:
                first_items = items[:last_and_pos].strip().rstrip(',')
                last_item = items[last_and_pos + 5:].strip()
                
                first_sentence = f"{subject} {verb} {first_items}"
                second_sentence = f"It also {verb.lower()} {last_item} that {that_clause}"
                return f"{first_sentence}. {second_sentence}"
        
        # Fallback: split at "that"
        first_sentence = f"{subject} {verb} {items}"
        second_sentence = f"These {that_clause}"
        return f"{first_sentence}. {second_sentence}"
    
    # Pattern 5: Handle "X must be Y" pattern
    must_be_match = re.search(r'(.+?)\s+must\s+be\s+(.+)', sentence, re.IGNORECASE)
    if must_be_match:
        subject_part = must_be_match.group(1).strip()
        config_part = must_be_match.group(2).strip()
        
        # Clean subject of any relative clauses
        clean_subject = re.sub(r',\s*which\s+[^,]+', '', subject_part, flags=re.IGNORECASE)
        
        first_sentence = f"{clean_subject} requires proper configuration"
        second_sentence = f"It must be {config_part}"
        return f"{first_sentence}. {second_sentence}"
    
    # Pattern 6: Simple conjunction break with proper sentence completion
    if ' and ' in sentence and sentence.count(' and ') == 1:
        parts = sentence.split(' and ', 1)
        if len(parts) == 2 and len(parts[0].split()) > 10 and len(parts[1].split()) > 10:
            first_part = parts[0].strip().rstrip(',')
            second_part = parts[1].strip()
            
            # Ensure second part is a complete sentence
            if not re.match(r'^(It|They|These|This|The|A)', second_part, re.IGNORECASE):
                # Add appropriate subject based on context
                if any(word in second_part.lower() for word in ['activities', 'processes', 'operations']):
                    second_part = f"These include {second_part.lower()}"
                elif any(word in second_part.lower() for word in ['capabilities', 'features', 'settings']):
                    second_part = f"These provide {second_part.lower()}"
                else:
                    second_part = f"It also includes {second_part.lower()}"
            
            second_part = second_part.capitalize()
            return f"{first_part}. {second_part}"
    
    # Pattern 7: Ultimate fallback - split at comma or middle with proper sentence structure
    words = sentence.split()
    
    # Try to find a comma break first
    for i in range(len(words) // 3, 2 * len(words) // 3):
        if i < len(words) and words[i].endswith(','):
            first_part = ' '.join(words[:i+1])[:-1]  # Remove the comma
            second_part = ' '.join(words[i+1:])
            
            # Make second part a complete sentence
            if not re.match(r'^(It|They|These|This|The)', second_part, re.IGNORECASE):
                second_part = f"These include {second_part.lower()}"
            
            second_part = second_part.capitalize()
            return f"{first_part}. {second_part}"
    
    # Final fallback - middle split with connector
    mid_point = len(words) // 2
    first_part = ' '.join(words[:mid_point])
    second_part = ' '.join(words[mid_point:])
    
    # Ensure both parts are complete sentences
    if not first_part.endswith('.'):
        first_part += '.'
    
    if not re.match(r'^(It|They|These|This|The)', second_part, re.IGNORECASE):
        second_part = f"Additionally, {second_part.lower()}"
    
    second_part = second_part.capitalize()
    return f"{first_part} {second_part}"


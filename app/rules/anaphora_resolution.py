"""
Anaphora Resolution - Resolve pronouns to their antecedents
Helps convert passive voice by identifying unclear subjects from previous sentences.
"""

import re
import logging
from typing import Optional, Dict, Any

try:
    import spacy
    from app.app import nlp
    SPACY_AVAILABLE = nlp is not None
except ImportError:
    SPACY_AVAILABLE = False

logger = logging.getLogger(__name__)


def resolve_pronoun_subject(current_sentence: str, previous_sentence: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Resolve pronoun subject (like "It") in current sentence by analyzing previous sentence.
    
    Args:
        current_sentence: The sentence containing the pronoun
        previous_sentence: The previous sentence to analyze for the antecedent
    
    Returns:
        Dictionary with:
        - subject: The resolved subject from previous sentence
        - pronoun: The pronoun that was resolved
        - confidence: How confident we are (high/medium/low)
        - explanation: Human-readable explanation
        None if resolution fails
    """
    
    if not previous_sentence or not SPACY_AVAILABLE:
        return None
    
    logger.info(f"🔍 Resolving pronoun in: '{current_sentence}'")
    logger.info(f"📖 Using previous: '{previous_sentence}'")
    
    # Check if current sentence starts with a pronoun
    current_lower = current_sentence.lower().strip()
    pronouns_to_resolve = ['it', 'this', 'that', 'these', 'those']
    
    found_pronoun = None
    for pronoun in pronouns_to_resolve:
        if current_lower.startswith(pronoun + ' '):
            found_pronoun = pronoun
            break
    
    if not found_pronoun:
        logger.info("❌ No resolvable pronoun found at start of sentence")
        return None
    
    logger.info(f"✅ Found pronoun: '{found_pronoun}'")
    
    # Parse previous sentence to find potential antecedents
    try:
        prev_doc = nlp(previous_sentence)
        
        # Strategy 1: Look for the main subject (nsubj) of previous sentence
        subjects = []
        for token in prev_doc:
            if token.dep_ in ['nsubj', 'nsubjpass']:  # Subject or passive subject
                # Get the full noun phrase
                subject_phrase = _get_full_noun_phrase(token)
                if subject_phrase:
                    subjects.append({
                        'text': subject_phrase,
                        'type': 'main_subject',
                        'confidence': 'high'
                    })
        
        # Strategy 2: If no subject found, look for objects
        if not subjects:
            for token in prev_doc:
                if token.dep_ in ['dobj', 'pobj', 'obj']:  # Direct/prepositional object
                    object_phrase = _get_full_noun_phrase(token)
                    if object_phrase:
                        subjects.append({
                            'text': object_phrase,
                            'type': 'object',
                            'confidence': 'medium'
                        })
        
        # Strategy 3: Last resort - look for any noun
        if not subjects:
            nouns = [token for token in prev_doc if token.pos_ == 'NOUN' or token.pos_ == 'PROPN']
            if nouns:
                # Take the last significant noun (more likely to be the antecedent)
                last_noun = nouns[-1]
                noun_phrase = _get_full_noun_phrase(last_noun)
                if noun_phrase:
                    subjects.append({
                        'text': noun_phrase,
                        'type': 'noun',
                        'confidence': 'low'
                    })
        
        # Return the best candidate
        if subjects:
            best_subject = subjects[0]  # Take first (highest confidence)
            logger.info(f"✅ Resolved '{found_pronoun}' → '{best_subject['text']}' (confidence: {best_subject['confidence']})")
            
            return {
                'subject': best_subject['text'],
                'pronoun': found_pronoun,
                'confidence': best_subject['confidence'],
                'explanation': f"The pronoun '{found_pronoun}' likely refers to '{best_subject['text']}' from the previous sentence."
            }
        else:
            logger.warning("❌ No suitable antecedent found in previous sentence")
            return None
    
    except Exception as e:
        logger.error(f"❌ Error resolving pronoun: {e}")
        return None


def _get_full_noun_phrase(token) -> Optional[str]:
    """
    Extract the full noun phrase including determiners and adjectives.
    
    E.g., "the SIMATIC S7+ Connector" instead of just "Connector"
    """
    if not token:
        return None
    
    # Collect all tokens that are part of this noun phrase
    phrase_tokens = [token]
    
    # Add left children (determiners, adjectives, compounds)
    for child in token.lefts:
        if child.dep_ in ['det', 'amod', 'compound', 'poss']:
            phrase_tokens.insert(0, child)
    
    # Add right children (prepositional phrases, relative clauses - but limit to avoid too long phrases)
    for child in token.rights:
        if child.dep_ in ['prep']:  # Only include prep, not full clauses
            phrase_tokens.append(child)
            # Add children of prep (the object of preposition)
            for prep_child in child.children:
                if prep_child.dep_ == 'pobj':
                    phrase_tokens.append(prep_child)
                    # Add modifiers of pobj
                    for pobj_child in prep_child.children:
                        if pobj_child.dep_ in ['det', 'amod', 'compound']:
                            phrase_tokens.insert(len(phrase_tokens)-1, pobj_child)
    
    # Build the phrase text
    phrase = ' '.join([t.text for t in sorted(phrase_tokens, key=lambda x: x.i)])
    
    # Clean up the phrase
    phrase = phrase.strip()
    
    # Filter out very short or uninformative phrases
    if len(phrase) < 2 or phrase.lower() in ['it', 'this', 'that', 'these', 'those']:
        return None
    
    return phrase


def should_convert_to_active(current_sentence: str, resolved_subject: Optional[Dict[str, Any]] = None) -> tuple[bool, str]:
    """
    Determine if passive voice should be converted to active voice.
    
    Returns:
        (should_convert, reason)
    """
    
    # Rule 1: If we successfully resolved a clear subject, conversion is beneficial
    if resolved_subject and resolved_subject.get('confidence') in ['high', 'medium']:
        return True, f"Subject '{resolved_subject['subject']}' identified from context - active voice will be clearer"
    
    # Rule 2: If subject is unclear and no resolution, passive might be clearer
    current_lower = current_sentence.lower()
    
    # Check for "by" phrase - indicates actor is present
    if ' by ' in current_lower:
        # Actor is explicit, so active voice is appropriate
        return True, "Actor is explicit in 'by' phrase - active voice recommended"
    
    # Rule 3: Check for modal + be constructions (can be, should be, etc.)
    if any(modal in current_lower for modal in ['can be', 'should be', 'must be', 'may be', 'will be']):
        # These are often clearer in active form
        if resolved_subject:
            return True, "Modal passive construction - active voice with resolved subject is clearer"
        else:
            return False, "Modal passive without clear actor - passive voice is acceptable"
    
    # Rule 4: Scientific/technical contexts may prefer passive
    if any(keyword in current_lower for keyword in ['result', 'data', 'measurement', 'analysis', 'observation']):
        if not resolved_subject:
            return False, "Scientific context without clear actor - passive voice is conventional"
    
    # Rule 5: If no subject resolved and no "by" phrase, passive might be clearer
    if not resolved_subject and ' by ' not in current_lower:
        return False, "Actor unclear and cannot be inferred from context - passive voice may be appropriate"
    
    # Default: attempt conversion if we have some context
    if resolved_subject:
        return True, "Resolved subject available - active voice will improve clarity"
    else:
        return False, "Insufficient context for conversion - keep passive voice"


def convert_passive_with_context(
    current_sentence: str,
    previous_sentence: Optional[str] = None,
    next_sentence: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Convert passive voice to active voice using context from adjacent sentences.
    
    Returns:
        Dictionary with:
        - suggestion: The active voice version
        - explanation: Why this conversion was made
        - confidence: Confidence level
        - method: How it was converted
        None if conversion not recommended
    """
    
    # Step 1: Try to resolve the subject
    resolved = resolve_pronoun_subject(current_sentence, previous_sentence)
    
    # Step 2: Check if conversion is beneficial
    should_convert, reason = should_convert_to_active(current_sentence, resolved)
    
    if not should_convert:
        logger.info(f"⚠️ Conversion not recommended: {reason}")
        return {
            'suggestion': current_sentence,
            'explanation': f"No conversion needed. {reason}",
            'confidence': 'high',
            'method': 'conversion_not_required',
            'conversion_required': False
        }
    
    # Step 3: Perform the conversion
    if resolved:
        suggestion = _convert_with_resolved_subject(current_sentence, resolved['subject'])
        
        return {
            'suggestion': suggestion,
            'explanation': f"Converted to active voice using '{resolved['subject']}' from previous sentence for clarity.",
            'confidence': resolved['confidence'],
            'method': 'context_resolution',
            'conversion_required': True,
            'resolved_subject': resolved['subject']
        }
    else:
        # Try simple conversion without context
        suggestion = _simple_passive_to_active(current_sentence)
        
        if suggestion != current_sentence:
            return {
                'suggestion': suggestion,
                'explanation': "Converted to active voice using pattern matching.",
                'confidence': 'medium',
                'method': 'pattern_based',
                'conversion_required': True
            }
        else:
            return None


def _convert_with_resolved_subject(sentence: str, subject: str) -> str:
    """Convert passive sentence to active using the resolved subject."""
    
    # Pattern: "It is [verb]ed" → "[Subject] [verb]s"
    pattern1 = r'^(It|This|That)\s+(is|are|was|were)\s+(\w+ed|shown|displayed|integrated|provided|configured)\b(.*)$'
    match = re.match(pattern1, sentence, re.IGNORECASE)
    
    if match:
        verb_past = match.group(3)
        remainder = match.group(4).strip()
        
        # Convert past participle to present tense
        verb_present = _past_participle_to_present(verb_past, is_plural='and' in subject.lower())
        
        # Build active voice sentence
        if remainder:
            return f"{subject} {verb_present}{remainder}"
        else:
            return f"{subject} {verb_present}."
    
    # If pattern doesn't match, return with simple subject replacement
    sentence_lower = sentence.lower()
    if sentence_lower.startswith('it '):
        return subject + sentence[2:]  # Replace "It" with subject
    elif sentence_lower.startswith('this '):
        return subject + sentence[4:]  # Replace "This" with subject
    
    return sentence


def _simple_passive_to_active(sentence: str) -> str:
    """Simple pattern-based passive to active conversion (fallback)."""
    
    # Pattern: "[Something] is [verb]ed by [actor]" → "[Actor] [verb]s [something]"
    by_pattern = r'^(.+?)\s+(is|are|was|were)\s+(\w+ed|shown|displayed)\s+by\s+(.+?)([.,!?])?$'
    match = re.match(by_pattern, sentence, re.IGNORECASE)
    
    if match:
        object_phrase = match.group(1).strip()
        verb_past = match.group(3)
        actor = match.group(4).strip()
        punct = match.group(5) or '.'
        
        verb_present = _past_participle_to_present(verb_past, is_plural='and' in actor.lower())
        
        return f"{actor.capitalize()} {verb_present} {object_phrase.lower()}{punct}"
    
    return sentence


def _past_participle_to_present(past_participle: str, is_plural: bool = False) -> str:
    """Convert past participle to present tense."""
    
    verb_map = {
        'shown': 'shows' if not is_plural else 'show',
        'displayed': 'displays' if not is_plural else 'display',
        'integrated': 'integrates' if not is_plural else 'integrate',
        'provided': 'provides' if not is_plural else 'provide',
        'configured': 'configures' if not is_plural else 'configure',
        'created': 'creates' if not is_plural else 'create',
        'generated': 'generates' if not is_plural else 'generate',
    }
    
    past_lower = past_participle.lower()
    
    if past_lower in verb_map:
        return verb_map[past_lower]
    
    # Default: remove 'ed' and add 's' for singular
    if past_lower.endswith('ed'):
        base = past_lower[:-2]
        return base + 's' if not is_plural else base
    
    return past_participle

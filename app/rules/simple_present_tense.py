import re
import spacy
from bs4 import BeautifulSoup
import html

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    
    # Rule 1: Check for future tense constructions (will + verb)
    for token in doc:
        if token.text.lower() == "will" and token.dep_ == "aux":
            next_token = token.nbor(1) if token.i + 1 < len(doc) else None
            if next_token and next_token.pos_ == "VERB":
                sentence = token.sent.text.strip()
                if not _is_conditional_or_example(sentence):
                    suggestions.append(f"Consider using simple present tense instead of future tense. Replace 'will {next_token.text}' with '{next_token.text}' or '{_get_present_form(next_token.text)}'.")
    
    # Rule 2: Check for continuous tense (be + ing verbs)
    for token in doc:
        if token.lemma_ == "be" and token.pos_ == "AUX":
            next_token = token.nbor(1) if token.i + 1 < len(doc) else None
            if next_token and next_token.tag_ == "VBG":  # Present participle (-ing form)
                sentence = token.sent.text.strip()
                if not _is_ongoing_action_context(sentence):
                    base_verb = _get_present_form(next_token.lemma_)
                    suggestions.append(f"Consider using simple present tense instead of continuous tense. Replace '{token.text} {next_token.text}' with '{base_verb}'.")
    
    # Rule 3: Check for perfect tense constructions (have/has + past participle)
    for token in doc:
        if token.lemma_ == "have" and token.pos_ == "AUX":
            next_token = token.nbor(1) if token.i + 1 < len(doc) else None
            if next_token and next_token.tag_ == "VBN":  # Past participle
                sentence = token.sent.text.strip()
                if not _is_experience_or_result_context(sentence):
                    base_verb = _get_present_form(next_token.lemma_)
                    suggestions.append(f"Consider using simple present tense instead of perfect tense. Replace '{token.text} {next_token.text}' with '{base_verb}'.")
    
    # Rule 5: Check for modal verbs that could be simplified
    modal_verbs = ["would", "should", "could", "might", "must", "can"]
    for token in doc:
        if token.text.lower() in modal_verbs and token.pos_ == "AUX":
            next_token = token.nbor(1) if token.i + 1 < len(doc) else None
            if next_token and next_token.pos_ == "VERB":
                sentence = token.sent.text.strip()
                if not _is_conditional_or_hypothetical(sentence):
                    # Provide specific rewrite suggestions for modal verbs
                    rewritten_sentence = _rewrite_modal_sentence(sentence, token.text, next_token.text)
                    suggestions.append(f"Consider rewriting to describe the action instead of using '{token.text.lower()}'. Original: \"{sentence}\" → Suggested: \"{rewritten_sentence}\"")
    
    # Rule 6: Check for passive voice that could be active simple present
    for token in doc:
        if token.lemma_ == "be" and token.pos_ == "AUX":
            next_token = token.nbor(1) if token.i + 1 < len(doc) else None
            if next_token and next_token.tag_ == "VBN":  # Past participle in passive construction
                sentence = token.sent.text.strip()
                if not _has_explicit_agent(sentence):
                    suggestions.append(f"Consider converting from passive to active voice using simple present tense.")

    return suggestions if suggestions else []

def _is_narrative_or_example(sentence):
    """Check if sentence is describing past events, stories, or examples"""
    narrative_indicators = ["yesterday", "last", "ago", "in the past", "previously", "earlier", "once upon", "example:", "for instance"]
    return any(indicator in sentence.lower() for indicator in narrative_indicators)

def _is_conditional_or_example(sentence):
    """Check if sentence contains conditional or hypothetical language"""
    conditional_indicators = ["if", "when", "unless", "suppose", "imagine", "example", "scenario"]
    return any(indicator in sentence.lower() for indicator in conditional_indicators)

def _is_ongoing_action_context(sentence):
    """Check if continuous tense is appropriate (ongoing actions)"""
    ongoing_indicators = ["currently", "now", "at the moment", "right now", "while", "during"]
    return any(indicator in sentence.lower() for indicator in ongoing_indicators)

def _is_experience_or_result_context(sentence):
    """Check if perfect tense is appropriate (experience or completed actions with present relevance)"""
    experience_indicators = ["ever", "never", "already", "just", "recently", "so far", "until now", "experience"]
    return any(indicator in sentence.lower() for indicator in experience_indicators)

def _is_conditional_or_hypothetical(sentence):
    """Check if modal usage is appropriate for conditionals or hypotheticals"""
    conditional_indicators = ["if", "unless", "suppose", "imagine", "hypothetically", "potentially", "possibly"]
    return any(indicator in sentence.lower() for indicator in conditional_indicators)

def _has_explicit_agent(sentence):
    """Check if passive sentence has an explicit agent (by someone/something)"""
    return " by " in sentence.lower()

def _rewrite_modal_sentence(sentence, modal_verb, main_verb):
    """Rewrite sentences with modal verbs to use direct action language"""
    modal_lower = modal_verb.lower()
    sentence_lower = sentence.lower()
    
    # Handle "can" specifically - convert to direct action
    if modal_lower == "can":
        # Replace "you can [verb]" with direct instruction
        if "you can" in sentence_lower:
            # Convert to imperative form
            rewritten = re.sub(r'\byou can\s+(\w+)', r'\1', sentence, flags=re.IGNORECASE)
            # Capitalize first letter if it's the start of sentence
            if rewritten and rewritten[0].islower():
                rewritten = rewritten[0].upper() + rewritten[1:]
            return rewritten
        # Replace "can be [verb]" with "is/are [verb]"
        elif "can be" in sentence_lower:
            return re.sub(r'\bcan be\b', 'is', sentence, flags=re.IGNORECASE)
        # Replace "[subject] can [verb]" with "[subject] [verb]s"
        else:
            # Find the subject before "can"
            pattern = r'(\w+)\s+can\s+(\w+)'
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                subject = match.group(1)
                verb = match.group(2)
                # Convert to third person singular if needed (only for singular third person subjects)
                if subject.lower() not in ['i', 'you', 'we', 'they'] and not subject.lower().endswith('s'):
                    verb_form = _get_third_person_singular(verb)
                else:
                    verb_form = verb
                return re.sub(pattern, f'{subject} {verb_form}', sentence, flags=re.IGNORECASE)
    
    # Handle "could" - convert to present possibility
    elif modal_lower == "could":
        if "you could" in sentence_lower:
            return re.sub(r'\byou could\s+(\w+)', r'you \1', sentence, flags=re.IGNORECASE)
        else:
            return re.sub(r'\bcould\s+(\w+)', r'\1', sentence, flags=re.IGNORECASE)
    
    # Handle "would" - convert to present action
    elif modal_lower == "would":
        if "would" in sentence_lower:
            return re.sub(r'\bwould\s+(\w+)', r'\1s', sentence, flags=re.IGNORECASE)
    
    # Handle "should" - convert to recommendation
    elif modal_lower == "should":
        if "you should" in sentence_lower:
            return re.sub(r'\byou should\s+(\w+)', r'\1', sentence, flags=re.IGNORECASE)
        else:
            return re.sub(r'\bshould\s+(\w+)', r'\1', sentence, flags=re.IGNORECASE)
    
    # Handle "might" - convert to possibility
    elif modal_lower == "might":
        if "might" in sentence_lower:
            return re.sub(r'\bmight\s+(\w+)', r'may \1', sentence, flags=re.IGNORECASE)
    
    # Handle "must" - convert to requirement
    elif modal_lower == "must":
        if "you must" in sentence_lower:
            return re.sub(r'\byou must\s+(\w+)', r'\1', sentence, flags=re.IGNORECASE)
        else:
            return re.sub(r'\bmust\s+(\w+)', r'\1', sentence, flags=re.IGNORECASE)
    
    # Fallback: just remove the modal
    return re.sub(f'\\b{modal_lower}\\s+', '', sentence, flags=re.IGNORECASE)

def _get_third_person_singular(verb):
    """Convert verb to third person singular form"""
    verb_lower = verb.lower()
    
    # Handle irregular verbs
    irregular_third_person = {
        "be": "is", "have": "has", "do": "does", "go": "goes",
        "try": "tries", "fly": "flies", "cry": "cries", "study": "studies"
    }
    
    if verb_lower in irregular_third_person:
        return irregular_third_person[verb_lower]
    
    # Regular rules for third person singular
    if verb_lower.endswith(('s', 'sh', 'ch', 'x', 'z')):
        return verb + "es"
    elif verb_lower.endswith('y') and len(verb_lower) > 1 and verb_lower[-2] not in 'aeiou':
        return verb[:-1] + "ies"
    else:
        return verb + "s"

def _get_present_form(verb):
    """Get the simple present form of a verb"""
    # Simple mapping for common irregular verbs
    irregular_verbs = {
        "was": "is", "were": "are", "been": "is", "had": "has", "did": "does",
        "went": "goes", "came": "comes", "took": "takes", "made": "makes",
        "said": "says", "got": "gets", "saw": "sees", "knew": "knows",
        "thought": "thinks", "found": "finds", "gave": "gives", "told": "tells",
        "worked": "works", "looked": "looks", "used": "uses", "wanted": "wants",
        "called": "calls", "asked": "asks", "tried": "tries", "needed": "needs"
    }
    
    verb_lower = verb.lower()
    
    # Check irregular verbs first
    if verb_lower in irregular_verbs:
        return irregular_verbs[verb_lower]
    
    # Handle regular past tense (-ed endings)
    if verb_lower.endswith("ed"):
        # Remove -ed ending
        base = verb_lower[:-2]
        # Handle doubled consonants (e.g., "stopped" -> "stop")
        if len(base) >= 2 and base[-1] == base[-2] and base[-1] in "bcdfghjklmnpqrstvwxyz":
            base = base[:-1]
        return base
    
    # Handle -ing endings (present participle)
    if verb_lower.endswith("ing"):
        base = verb_lower[:-3]
        # Handle doubled consonants
        if len(base) >= 2 and base[-1] == base[-2] and base[-1] in "bcdfghjklmnpqrstvwxyz":
            base = base[:-1]
        # Handle dropped 'e' (e.g., "making" -> "make")
        elif not base.endswith("e") and len(base) >= 2:
            # Check if we need to add 'e' back
            if base[-1] in "cglnrsz" and base[-2] not in "aeiou":
                base += "e"
        return base
    
    # Return as-is if no transformation needed
    return verb

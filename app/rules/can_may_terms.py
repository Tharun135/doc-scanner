import re
import spacy
from bs4 import BeautifulSoup
import html

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []
    processed_sentences = set()  # Track processed sentences to avoid duplicates

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    
    # Rule 1: Check for "can" usage and provide specific rewrite suggestions
    for token in doc:
        if token.text.lower() == "can" and token.dep_ == "aux":
            sentence = token.sent.text.strip()
            sentence_key = f"can_{sentence}"
            
            # Skip if we already processed this sentence for "can" usage
            if sentence_key in processed_sentences:
                continue
            
            # Provide specific rewrite suggestion for "can"
            if "you can" in sentence.lower():
                # Convert to imperative form
                rewritten = re.sub(r'\byou can\s+(\w+)', r'\1', sentence, flags=re.IGNORECASE)
                if rewritten and rewritten[0].islower():
                    rewritten = rewritten[0].upper() + rewritten[1:]
                suggestions.append(f"Consider rewriting to describe the action instead of using 'can'. Original: \"{sentence}\" → Suggested: \"{rewritten}\"")
                processed_sentences.add(sentence_key)
            elif "can be" in sentence.lower():
                rewritten = re.sub(r'\bcan be\b', 'is', sentence, flags=re.IGNORECASE)
                suggestions.append(f"Consider rewriting to describe the action instead of using 'can'. Original: \"{sentence}\" → Suggested: \"{rewritten}\"")
                processed_sentences.add(sentence_key)
            else:
                # Handle other patterns of "can"
                pattern = r'(\w+)\s+can\s+(\w+)'
                match = re.search(pattern, sentence, re.IGNORECASE)
                if match:
                    subject = match.group(1)
                    verb = match.group(2)
                    if subject.lower() not in ['i', 'you', 'we', 'they'] and not subject.lower().endswith('s'):
                        verb_form = verb + "s" if not verb.endswith('s') else verb
                    else:
                        verb_form = verb
                    rewritten = re.sub(pattern, f'{subject} {verb_form}', sentence, flags=re.IGNORECASE)
                    suggestions.append(f"Consider rewriting to describe the action instead of using 'can'. Original: \"{sentence}\" → Suggested: \"{rewritten}\"")
                    processed_sentences.add(sentence_key)
    
    # Rule 1b: Check for "can" being used to express permission (additional specific case)
    for token in doc:
        if token.text.lower() == "can" and token.dep_ == "aux":
            sentence = token.sent.text.strip()
            sentence_key = f"can_permission_{sentence}"
            
            # Skip if we already processed this sentence for general "can" usage
            if f"can_{sentence}" in processed_sentences:
                continue
            
            # Skip if we already processed this sentence for "can" permission usage
            if sentence_key in processed_sentences:
                continue
            
            # Flag permission-related usage of "can" with additional context
            if "permission" in sentence.lower() or "allowed" in sentence.lower() or "authorize" in sentence.lower():
                suggestions.append("When expressing permission, consider using 'allowed to' or 'able to' instead of 'can'.")
                processed_sentences.add(sentence_key)
    
    # Rule 2: Check for proper use of "may" and suggest replacing it with "might"
    may_pattern = r'\bmay\b'
    processed_may_sentences = set()
    matches = re.finditer(may_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Find which sentence this match belongs to
        match_pos = match.start()
        target_sentence = None
        for sent in doc.sents:
            if sent.start_char <= match_pos <= sent.end_char:
                target_sentence = sent.text.strip()
                break
        
        if target_sentence:
            sentence_key = f"may_{target_sentence}"
            if sentence_key not in processed_may_sentences:
                suggestions.append("Avoid using 'may' as it can imply permission. Consider using 'might' to express possibility.")
                processed_may_sentences.add(sentence_key)

    # Rule 3: Ensure "could" is used only for the past and not as a substitute for "can"
    could_pattern = r'\bcould\b'
    processed_could_sentences = set()
    matches = re.finditer(could_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Find which sentence this match belongs to
        match_pos = match.start()
        target_sentence = None
        for sent in doc.sents:
            if sent.start_char <= match_pos <= sent.end_char:
                target_sentence = sent.text.strip()
                break
        
        if target_sentence:
            sentence_key = f"could_{target_sentence}"
            if sentence_key not in processed_could_sentences:
                context_window = 30
                start = max(0, match.start() - context_window)
                end = min(len(content), match.end() + context_window)
                context = content[start:end]
                if "past" not in context.lower():
                    suggestions.append("Ensure 'could' is only used to describe the past. Use 'can' for present actions.")
                processed_could_sentences.add(sentence_key)

    # Rule 4: Detect overuse of "can" and suggest rewording
    can_count = len([token for token in doc if token.text.lower() == "can"])
    if can_count > 3:  # Threshold for overuse (customizable)
        suggestions.append("Consider rephrasing to avoid overusing 'can'.")

    return suggestions if suggestions else []
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
                suggestions.append(f"Issue: Use of modal verb 'can' - should describe direct action\nOriginal sentence: {sentence}\nAI suggestion: {rewritten}")
                processed_sentences.add(sentence_key)
            elif "can be" in sentence.lower():
                rewritten = re.sub(r'\bcan be\b', 'is', sentence, flags=re.IGNORECASE)
                suggestions.append(f"Issue: Use of modal verb 'can be' - should describe direct state\nOriginal sentence: {sentence}\nAI suggestion: {rewritten}")
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
                    suggestions.append(f"Issue: Use of modal verb 'can' - should describe direct action\nOriginal sentence: {sentence}\nAI suggestion: {rewritten}")
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
                suggestions.append(f"Issue: Use of 'can' for permission context\nOriginal sentence: {sentence}\nAI suggestion: When expressing permission, consider using 'allowed to' or 'able to' instead of 'can'.")
                processed_sentences.add(sentence_key)

    # Rule 2: Check all "may" usage and provide context-aware suggestions
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
                # Check if it's permission context
                permission_indicators = [
                    r'\bmay\s+(access|enter|use|modify|delete|create|edit|view|download|upload)',
                    r'(you|users?|they)\s+may\s+',
                    r'\bmay\s+(be\s+)?(allowed|permitted|authorized)',
                    r'(permission|authorize|grant|allow).*\bmay\b',
                    r'\bmay\s+(only|not)\s+'
                ]
                
                is_permission_context = any(re.search(pattern, target_sentence, re.IGNORECASE) 
                                          for pattern in permission_indicators)
                
                # Check if it's possibility context
                possibility_patterns = [
                    r'(may\s+take|may\s+require|may\s+cause|may\s+result|may\s+occur)',
                    r'(may\s+be\s+(necessary|required|needed|different|slow|fast))',
                    r'(process|loading|operation|function).*may\s+',
                    r'may\s+(vary|differ|change|fluctuate)',
                    r'(it|this|that|process|loading|operation).*may\s+'
                ]
                
                is_possibility_context = any(re.search(pattern, target_sentence, re.IGNORECASE) 
                                           for pattern in possibility_patterns)
                
                # Always flag "may" usage, but provide different messages based on context
                if is_permission_context and not is_possibility_context:
                    suggestions.append(f"Issue: Use of 'may' for permission context\nOriginal sentence: {target_sentence}\nAI suggestion: Consider using 'can' or 'are allowed to' for permissions")
                elif is_possibility_context:
                    suggestions.append(f"Issue: Modal verb usage - 'may' for possibility\nOriginal sentence: {target_sentence}\nAI suggestion: Review if 'may' is the best choice for expressing possibility")
                else:
                    # General "may" usage - let AI decide
                    suggestions.append(f"Issue: Modal verb 'may' usage\nOriginal sentence: {target_sentence}\nAI suggestion: Review modal verb usage - determine if expressing permission or possibility")
                
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
            if sent.start_char <= match_pos <= match.end_char:
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
                    suggestions.append(f"Issue: Use of 'could' for non-past context\nOriginal sentence: {target_sentence}\nAI suggestion: Ensure 'could' is only used to describe the past. Use 'can' for present actions.")
                processed_could_sentences.add(sentence_key)

    # Rule 4: Detect overuse of "can" and suggest rewording
    can_count = len([token for token in doc if token.text.lower() == "can"])
    if can_count > 3:  # Threshold for overuse (customizable)
        # Find a sentence with multiple "can" usage
        sample_sentence = ""
        for sent in doc.sents:
            can_in_sentence = len([token for token in sent if token.text.lower() == "can"])
            if can_in_sentence > 0:
                sample_sentence = sent.text.strip()
                break
        suggestions.append(f"Issue: Overuse of modal verb 'can' ({can_count} instances)\nOriginal sentence: {sample_sentence}\nAI suggestion: Consider rephrasing to avoid overusing 'can'.")

    return suggestions if suggestions else []

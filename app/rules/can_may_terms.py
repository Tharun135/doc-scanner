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

    # Rule 1: Check all "may" usage and provide context-aware suggestions
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
                    suggestions.append({
                        "text": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "message": f"Use of 'may' for permission context. Replace 'may' with 'can' or 'are allowed to' for permissions. Sentence: {target_sentence}"
                    })
                elif is_possibility_context:
                    suggestions.append({
                        "text": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "message": f"Modal verb 'may' for possibility. Keep 'may' - it correctly expresses possibility/uncertainty. Sentence: {target_sentence}"
                    })
                else:
                    # General "may" usage - let AI decide
                    suggestions.append({
                        "text": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "message": f"Modal verb 'may' usage. Determine context: keep 'may' for possibility, use 'can' for permission. Sentence: {target_sentence}"
                    })
                
                processed_may_sentences.add(sentence_key)

    # Rule 2: Ensure "could" is used only for the past and not as a substitute for "can"
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
                    suggestions.append({
                        "text": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                        "message": f"Use of 'could' for non-past context. Ensure 'could' is only used to describe the past. Use 'can' for present actions. Sentence: {target_sentence}"
                    })
                processed_could_sentences.add(sentence_key)

    # Rule 3: Detect overuse of "can" and suggest rewording
    can_count = len([token for token in doc if token.text.lower() == "can"])
    if can_count > 3:  # Threshold for overuse (customizable)
        # Find a sentence with multiple "can" usage
        sample_sentence = ""
        for sent in doc.sents:
            can_in_sentence = len([token for token in sent if token.text.lower() == "can"])
            if can_in_sentence > 0:
                sample_sentence = sent.text.strip()
                break
        suggestions.append({
            "text": "can",
            "start": 0,
            "end": 3,
            "message": f"Overuse of modal verb 'can' ({can_count} instances). Consider rephrasing to avoid overusing 'can'. Example sentence: {sample_sentence}"
        })

    return suggestions if suggestions else []

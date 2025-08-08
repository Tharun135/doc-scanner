import re
from .spacy_utils import get_nlp_model
from bs4 import BeautifulSoup
import html

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

# Global variable to hold the spaCy model
nlp = None

def get_nlp():
    """Load spaCy model with error handling"""
    global nlp
    if nlp is None:
        try:
            nlp = get_nlp_model()
        except Exception as e:
            print(f"Warning: Could not load spaCy model: {e}")
            print("Some advanced features may not work. Install with: python -m spacy download en_core_web_sm")
            nlp = False  # Mark as failed to avoid retrying
    return nlp if nlp is not False else None

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Get spaCy model with error handling
    nlp_model = get_nlp()
    if nlp_model:
        doc = nlp_model(text_content)
    else:
        doc = None  # Fallback if spaCy is not available
    # Rule 1: Use 'sign in' instead of 'log in' or 'log on'
    login_patterns = [r'\blog\s?in\b', r'\blog\s?on\b']
    for pattern in login_patterns:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
#            line_number = get_line_number(content, match.start())
            suggestions.append("Use 'sign in' instead of '{match.group()}'.")
    
    # Rule 2: Use 'malware' instead of 'virus' unless specifically referring to a virus
    virus_pattern = r'\bvirus(es)?\b'
    matches = re.finditer(virus_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # Determine if 'virus' is being used generically
        context_window = 50  # Number of characters before and after the match
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end].lower()
        if 'trojan' in context or 'worm' in context or 'malware' in context:
            # If context includes other types of malware, suggest using 'malware'
#            line_number = get_line_number(content, match.start())
            suggestions.append("Consider using 'malware' instead of '{match.group()}' when referring to malware in general.")
        else:
            # If specifically about viruses, no suggestion needed
            pass
    
    # Rule 3: Use 'antimalware' instead of 'antivirus' unless specifically referring to viruses
    antivirus_pattern = r'\banti[-\s]?virus(es)?\b'
    matches = re.finditer(antivirus_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 50  # Number of characters before and after the match
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end].lower()
        # Check for general malware context
        malware_terms = ['malware', 'spyware', 'ransomware', 'trojan', 'worm', 'phishing', 'adware', 'rootkit']
        if any(term in context for term in malware_terms):
#            line_number = get_line_number(content, match.start())
            suggestions.append("Use 'antimalware' instead of '{match.group()}' when referring to protection against various types of malware.")
        else:
            # If specifically about viruses, no action needed
            pass

    # Rule 4: Use 'antispyware' appropriately
    antispyware_pattern = r'\banti[-\s]?spyware\b'
    matches = re.finditer(antispyware_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 50  # Number of characters before and after the match
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end].lower()
        # Check if context mentions other malware types
        if 'malware' in context or 'virus' in context or 'ransomware' in context or 'trojan' in context:
#            line_number = get_line_number(content, match.start())
            suggestions.append("Consider using 'antimalware' instead of '{match.group()}' when referring to protection against various types of malware.")
        else:
            # If specifically about spyware, no action needed
            pass

    # Rule 5: Use 'phishing' appropriately
    phishing_pattern = r'\bphishing\b'
    matches = re.finditer(phishing_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # No action needed unless 'phishing' is misspelled
        pass
    
    # Rule 6: Use 'two-factor authentication' or 'multifactor authentication' instead of 'two-step verification'
    two_step_pattern = r'\btwo[-\s]?step\s+verification\b'
    matches = re.finditer(two_step_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'two-factor authentication' or 'multifactor authentication' instead of '{match.group()}'.")
    
    # Rule 7: Use 'attacker' or 'unauthorized user' instead of 'hacker' unless necessary
    hacker_pattern = r'\bhacker(s)?\b'
    matches = re.finditer(hacker_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Consider using 'attacker' or 'unauthorized user' instead of '{match.group()}'.")
    
    # Rule 8: Use 'compromised' instead of 'hacked'
    hacked_pattern = r'\bhacked\b'
    matches = re.finditer(hacked_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'compromised' instead of '{match.group()}'.")
    
    # Rule 9: Use 'firewall' correctly
    firewall_pattern = r'\bfire\s+wall\b'
    matches = re.finditer(firewall_pattern, content, flags=re.IGNORECASE)
    for match in matches:
#        line_number = get_line_number(content, match.start())
        suggestions.append("Use 'firewall' as one word instead of '{match.group()}'.")
    
    # Rule 10: Use 'secure' instead of 'safe' when referring to security
    safe_pattern = r'\bsafe\b'
    matches = re.finditer(safe_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        context_window = 50  # Number of characters before and after the match
        start = max(0, match.start() - context_window)
        end = min(len(content), match.end() + context_window)
        context = content[start:end].lower()
        if 'secure' not in context and ('security' in context or 'protect' in context):
#            line_number = get_line_number(content, match.start())
            suggestions.append("Use 'secure' instead of 'safe' when referring to security.")
    
    # Rule 11: Avoid sensational or fear-mongering language
    sensational_terms = ['catastrophe', 'disaster', 'devastating', 'massive attack']
    for term in sensational_terms:
        pattern = rf'\b{term}\b'
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
#            line_number = get_line_number(content, match.start())
            suggestions.append("Avoid sensational language like '{match.group()}'. Use neutral terms.")
    
    # Rule 12: Use 'ransomware' appropriately
    ransomware_pattern = r'\bransomware\b'
    matches = re.finditer(ransomware_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        # No action needed unless misused
    
        return suggestions if suggestions else []
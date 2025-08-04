"""
Rule for checking spelling errors and suggesting corrections.
Detects misspelled words using multiple approaches and provides correction suggestions.
"""

import re
from bs4 import BeautifulSoup
import html
from .spacy_utils import get_nlp_model, process_text

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

# Try to import spell checking libraries
SPELL_CHECKERS_AVAILABLE = {
    'pyspellchecker': False,
    'spacy': False
}

try:
    from spellchecker import SpellChecker
    SPELL_CHECKERS_AVAILABLE['pyspellchecker'] = True
except ImportError:
    SpellChecker = None

def check(content):
    """Check for spelling errors and suggest corrections."""
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Use RAG system if available
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(
            content,
            "spelling_checker",
            "Check for spelling errors and suggest corrections while being aware of technical terminology and proper nouns."
        )
        if rag_suggestions:
            return rag_suggestions

    # Fallback to rule-based spelling checking
    if SPELL_CHECKERS_AVAILABLE['pyspellchecker']:
        suggestions.extend(check_spelling_pyspellchecker(text_content))
    elif SPELL_CHECKERS_AVAILABLE['spacy']:
        suggestions.extend(check_spelling_spacy(text_content))
    else:
        suggestions.extend(check_common_misspellings(text_content))

    return suggestions if suggestions else []

def check_spelling_pyspellchecker(text_content):
    """Use pyspellchecker library for comprehensive spell checking."""
    suggestions = []
    
    # Initialize spell checker
    spell = SpellChecker()
    
    # Add common technical terms to avoid false positives
    technical_terms = get_technical_whitelist()
    spell.word_frequency.load_words(technical_terms)
    
    # Extract words from text
    words = extract_words_for_spelling(text_content)
    
    # Find misspelled words
    misspelled = spell.unknown(words)
    
    for word in misspelled:
        # Skip if it's likely a proper noun, acronym, or technical term
        if should_skip_word_for_spelling(word):
            continue
            
        # Get correction candidates
        candidates = spell.candidates(word)
        if candidates:
            # Get the most likely correction
            correction = spell.correction(word)
            if correction and correction != word:
                # Get context for better suggestions
                context = get_word_context_in_text(text_content, word)
                suggestions.append(f"Spelling: '{word}' may be misspelled. Suggested correction: '{correction}'. Context: ...{context}...")
            
            # If there are multiple good candidates, mention them
            if len(candidates) > 1:
                top_candidates = list(candidates)[:3]  # Top 3 candidates
                if len(top_candidates) > 1:
                    alternatives = "', '".join(top_candidates)
                    suggestions.append(f"Multiple spelling options for '{word}': '{alternatives}'")
    
    return suggestions

def check_spelling_spacy(text_content):
    """Use spaCy for spell checking when available."""
    suggestions = []
    
    doc = process_text(text_content)
    if not doc:
        return suggestions
    
    # This is a placeholder for spaCy-based spell checking
    # spaCy doesn't have built-in spell checking, but can be extended
    # For now, fall back to common misspellings
    return check_common_misspellings(text_content)

def check_common_misspellings(text_content):
    """Check for common misspellings using a predefined list."""
    suggestions = []
    
    # Common misspellings in technical writing
    common_misspellings = {
        # General misspellings
        'recieve': 'receive',
        'seperate': 'separate',
        'definately': 'definitely',
        'occured': 'occurred',
        'occurence': 'occurrence',
        'begining': 'beginning',
        'accomodate': 'accommodate',
        'neccessary': 'necessary',
        'recomend': 'recommend',
        'acheive': 'achieve',
        'beleive': 'believe',
        'conscientous': 'conscientious',
        'embarass': 'embarrass',
        'existance': 'existence',
        'independant': 'independent',
        'maintainance': 'maintenance',
        'occurrance': 'occurrence',
        'priviledge': 'privilege',
        'refering': 'referring',
        'succesful': 'successful',
        'tommorow': 'tomorrow',
        'untill': 'until',
        'thier': 'their',
        'reccomend': 'recommend',
        
        # Technical misspellings
        'compatability': 'compatibility',
        'accessability': 'accessibility',
        'responsiveness': 'responsiveness',  # Often misspelled as 'responiveness'
        'performace': 'performance',
        'confguration': 'configuration',
        'authentification': 'authentication',
        'autorization': 'authorization',
        'implemenation': 'implementation',
        'intialization': 'initialization',
        'synchronisation': 'synchronization',
        'paramater': 'parameter',
        'algoritm': 'algorithm',
        'heirarchy': 'hierarchy',
        'persistance': 'persistence',
        'dependancy': 'dependency',
        'consistancy': 'consistency',
        'efficency': 'efficiency',
        'availabilty': 'availability',
        'scalabilty': 'scalability',
        'usabilty': 'usability',
        'integeration': 'integration',
        'migeration': 'migration',
        'configuraton': 'configuration',
        
        # Programming terms
        'lenght': 'length',
        'heigth': 'height',
        'widht': 'width',
        'postion': 'position',
        'indeces': 'indices',
        'sucess': 'success',
        'faild': 'failed',
        'excecute': 'execute',
        'proccess': 'process',
        'addres': 'address',
        'methof': 'method',
        'varriable': 'variable',
        'fucntion': 'function',
        'calss': 'class',
        'objet': 'object',
        'libary': 'library',
        'framwork': 'framework',
        'databse': 'database',
        'querty': 'query',
        'responce': 'response',
        'requets': 'request',
    }
    
    # Check for misspellings
    words = extract_words_for_spelling(text_content)
    
    for word in words:
        word_lower = word.lower()
        if word_lower in common_misspellings:
            correct_spelling = common_misspellings[word_lower]
            # Preserve original case
            if word.isupper():
                correct_spelling = correct_spelling.upper()
            elif word[0].isupper():
                correct_spelling = correct_spelling.capitalize()
            
            context = get_word_context_in_text(text_content, word)
            suggestions.append(f"Spelling: '{word}' should be '{correct_spelling}'. Context: ...{context}...")
    
    return suggestions

def extract_words_for_spelling(text):
    """Extract words from text for spell checking, filtering out non-words."""
    # Remove common non-word patterns
    text = re.sub(r'https?://[^\s]+', '', text)  # URLs
    text = re.sub(r'\w+@\w+\.\w+', '', text)    # Email addresses
    text = re.sub(r'\b\d+\b', '', text)         # Numbers
    text = re.sub(r'[^\w\s]', ' ', text)        # Punctuation
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]+\b', text)
    
    # Filter out very short words and common abbreviations
    filtered_words = []
    for word in words:
        if len(word) >= 3 and not is_common_abbreviation(word):
            filtered_words.append(word)
    
    return filtered_words

def should_skip_word_for_spelling(word):
    """Determine if a word should be skipped in spell checking."""
    # Skip very short words
    if len(word) < 3:
        return True
    
    # Skip likely acronyms (all caps, 2-5 letters)
    if word.isupper() and 2 <= len(word) <= 5:
        return True
    
    # Skip likely proper nouns (capitalized single words in certain contexts)
    if word[0].isupper() and len(word) > 3:
        return True
    
    # Skip words with numbers
    if any(char.isdigit() for char in word):
        return True
    
    # Skip common technical abbreviations
    if is_common_abbreviation(word.lower()):
        return True
    
    # Skip words that are likely technical terms
    if is_likely_technical_term(word):
        return True
    
    return False

def is_common_abbreviation(word):
    """Check if word is a common abbreviation."""
    common_abbrevs = {
        'api', 'url', 'uri', 'http', 'https', 'html', 'css', 'xml', 'json',
        'sql', 'gui', 'cli', 'ide', 'sdk', 'jdk', 'npm', 'pip', 'git',
        'ssh', 'ftp', 'tcp', 'udp', 'dns', 'vpn', 'cdn', 'aws', 'gcp',
        'ui', 'ux', 'qa', 'dev', 'prod', 'admin', 'auth', 'config',
        'db', 'os', 'cpu', 'gpu', 'ram', 'ssd', 'hdd', 'usb', 'wifi',
        'pdf', 'doc', 'docx', 'xlsx', 'ppt', 'pptx', 'jpg', 'png', 'gif',
        'zip', 'exe', 'dll', 'sys', 'tmp', 'log', 'cfg', 'ini', 'env'
    }
    return word.lower() in common_abbrevs

def is_likely_technical_term(word):
    """Check if word is likely a technical term that might not be in dictionary."""
    # Words with certain patterns that are common in tech
    tech_patterns = [
        r'^[a-z]+[A-Z]',  # camelCase
        r'.*[Tt]ech.*',   # Contains 'tech'
        r'.*[Ss]ync.*',   # Contains 'sync'
        r'.*[Aa]uth.*',   # Contains 'auth'
        r'.*[Cc]onfig.*', # Contains 'config'
        r'.*[Aa]pi.*',    # Contains 'api'
        r'.*[Dd]ata.*',   # Contains 'data'
        r'.*[Ss]erver.*', # Contains 'server'
        r'.*[Cc]lient.*', # Contains 'client'
    ]
    
    return any(re.match(pattern, word) for pattern in tech_patterns)

def get_technical_whitelist():
    """Get a list of technical terms to add to spell checker dictionary."""
    return [
        # Programming languages
        'javascript', 'typescript', 'python', 'java', 'csharp', 'cpp', 'golang',
        'rust', 'kotlin', 'swift', 'php', 'ruby', 'scala', 'clojure',
        
        # Frameworks and libraries
        'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask',
        'spring', 'laravel', 'rails', 'bootstrap', 'jquery', 'webpack',
        
        # Technologies
        'kubernetes', 'docker', 'jenkins', 'gitlab', 'github', 'bitbucket',
        'terraform', 'ansible', 'nginx', 'apache', 'redis', 'mongodb',
        'postgresql', 'mysql', 'elasticsearch', 'kafka', 'rabbitmq',
        
        # Cloud platforms
        'aws', 'azure', 'gcp', 'heroku', 'vercel', 'netlify', 'cloudflare',
        
        # Development tools
        'vscode', 'intellij', 'sublime', 'atom', 'vim', 'emacs', 'nano',
        'postman', 'insomnia', 'figma', 'sketch', 'photoshop', 'illustrator',
        
        # Common tech terms
        'api', 'rest', 'graphql', 'json', 'xml', 'yaml', 'markdown',
        'oauth', 'jwt', 'ssl', 'tls', 'cors', 'csrf', 'xss', 'sql',
        'nosql', 'crud', 'mvc', 'mvp', 'mvvm', 'spa', 'pwa', 'seo',
        'cdn', 'dns', 'https', 'tcp', 'udp', 'websocket', 'ajax',
        'regex', 'utf', 'ascii', 'unicode', 'base64', 'hash', 'encryption',
    ]

def get_word_context_in_text(text, word, context_size=30):
    """Get context around a word in text for better error reporting."""
    # Find the word in text (case insensitive)
    pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
    match = pattern.search(text)
    
    if not match:
        return "context not found"
    
    start = max(0, match.start() - context_size)
    end = min(len(text), match.end() + context_size)
    
    context = text[start:end].strip()
    
    # Clean up context
    context = re.sub(r'\s+', ' ', context)  # Normalize whitespace
    
    return context[:100] + "..." if len(context) > 100 else context

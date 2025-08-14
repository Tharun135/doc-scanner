"""
Terminology Rules
- Consistency, capitalization of product names, glossary use
"""
import re
from bs4 import BeautifulSoup
import html

# Import LlamaIndex AI system
try:
    from .llamaindex_helper import get_ai_suggestion
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    import logging
    logging.warning("LlamaIndex AI not available for terminology rules")

# Import custom terminology system
try:
    from ..simple_terminology import is_whitelisted_term
    TERMINOLOGY_AVAILABLE = True
except ImportError:
    TERMINOLOGY_AVAILABLE = False
    logging.warning("Custom terminology system not available")

def check(content):
    """Check for terminology consistency and correctness"""
    suggestions = []
    
    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)
    
    # Rule 1: Inconsistent term usage
    inconsistent_terms = find_inconsistent_terminology(text_content)
    for issue in inconsistent_terms:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="inconsistent_terminology",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Inconsistent terminology: Use '{issue['preferred']}' consistently instead of '{issue['variant']}'"
            suggestions.append(suggestion)
    
    # Rule 2: Incorrect product name capitalization
    capitalization_issues = find_capitalization_issues(text_content)
    for issue in capitalization_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="product_capitalization",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Capitalization: '{issue['incorrect']}' should be '{issue['correct']}'"
            suggestions.append(suggestion)
    
    # Rule 3: Undefined technical terms
    undefined_terms = find_undefined_technical_terms(text_content)
    for issue in undefined_terms:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="undefined_technical_term",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Undefined term: '{issue['term']}' should be defined on first use"
            suggestions.append(suggestion)
    
    # Rule 4: Incorrect acronym usage
    acronym_issues = find_acronym_issues(text_content)
    for issue in acronym_issues:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="acronym_usage",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Acronym: {issue['message']}"
            suggestions.append(suggestion)
    
    # Rule 5: Industry-specific terminology errors
    industry_errors = find_industry_terminology_errors(text_content)
    for issue in industry_errors:
        if AI_AVAILABLE:
            ai_suggestion = get_ai_suggestion(
                issue_type="industry_terminology",
                text=issue['context'],
                details=issue
            )
            suggestions.append(ai_suggestion)
        else:
            suggestion = f"Industry terminology: {issue['message']}"
            suggestions.append(suggestion)
    
    return suggestions

def find_inconsistent_terminology(text):
    """Find inconsistent usage of the same terms"""
    issues = []
    
    # Common terminology variants that should be consistent
    terminology_variants = {
        # Software terms
        'website': ['web site', 'web-site', 'Website'],
        'email': ['e-mail', 'E-mail', 'Email'],
        'internet': ['Internet', 'internet'],
        'web browser': ['webbrowser', 'Web Browser', 'browser'],
        'username': ['user name', 'user-name', 'Username'],
        'password': ['pass word', 'Password'],
        'database': ['data base', 'data-base', 'Database'],
        'software': ['soft ware', 'Software'],
        'hardware': ['hard ware', 'Hardware'],
        'network': ['net work', 'Network'],
        
        # Technical terms
        'API': ['api', 'Api'],
        'URL': ['url', 'Url'],
        'HTTP': ['http', 'Http'],
        'HTML': ['html', 'Html'],
        'CSS': ['css', 'Css'],
        'JavaScript': ['javascript', 'Javascript', 'Java Script'],
        'JSON': ['json', 'Json'],
        'XML': ['xml', 'Xml'],
        
        # Industrial terms (if applicable)
        'runtime': ['run time', 'run-time', 'Runtime'],
        'setup': ['set up', 'set-up', 'Setup'],
        'backup': ['back up', 'back-up', 'Backup'],
        'login': ['log in', 'log-in', 'Login'],
        'logout': ['log out', 'log-out', 'Logout']
    }
    
    for preferred, variants in terminology_variants.items():
        # Count occurrences of each variant
        preferred_count = len(re.findall(re.escape(preferred), text, re.IGNORECASE))
        variant_counts = {}
        
        for variant in variants:
            count = len(re.findall(re.escape(variant), text, re.IGNORECASE))
            if count > 0:
                variant_counts[variant] = count
        
        # If both preferred and variants are used, flag inconsistency
        if preferred_count > 0 and variant_counts:
            for variant, count in variant_counts.items():
                # Find first occurrence for context
                match = re.search(re.escape(variant), text, re.IGNORECASE)
                if match:
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end]
                    
                    issues.append({
                        "preferred": preferred,
                        "variant": variant,
                        "preferred_count": preferred_count,
                        "variant_count": count,
                        "context": context.strip()
                    })
    
    return issues

def find_capitalization_issues(text):
    """Find incorrect capitalization of product names and proper nouns"""
    # Known product names and their correct capitalization
    product_names = {
        # Software products
        'microsoft': 'Microsoft',
        'windows': 'Windows',
        'office': 'Office',
        'excel': 'Excel',
        'word': 'Word',
        'powerpoint': 'PowerPoint',
        'outlook': 'Outlook',
        'google': 'Google',
        'chrome': 'Chrome',
        'firefox': 'Firefox',
        'safari': 'Safari',
        'adobe': 'Adobe',
        'photoshop': 'Photoshop',
        'github': 'GitHub',
        'docker': 'Docker',
        'kubernetes': 'Kubernetes',
        
        # Programming languages
        'javascript': 'JavaScript',
        'typescript': 'TypeScript',
        'python': 'Python',
        'java': 'Java',
        'csharp': 'C#',
        'php': 'PHP',
        
        # Industrial (if applicable)
        'siemens': 'Siemens',
        'wincc': 'WinCC',
        'tia': 'TIA',
        'profinet': 'PROFINET',
        'profibus': 'PROFIBUS',
        'modbus': 'Modbus',
        'opcua': 'OPC UA',
        'scada': 'SCADA',
        'plc': 'PLC',
        'hmi': 'HMI'
    }
    
    issues = []
    
    for incorrect, correct in product_names.items():
        # Look for the incorrect version (case-insensitive, but not the correct version)
        pattern = re.compile(r'\b' + re.escape(incorrect) + r'\b', re.IGNORECASE)
        
        for match in pattern.finditer(text):
            # Skip if it's already correctly capitalized
            if match.group() == correct:
                continue
            
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "incorrect": match.group(),
                "correct": correct,
                "context": context.strip()
            })
    
    return issues

def find_undefined_technical_terms(text):
    """Find technical terms that should be defined on first use"""
    # Technical terms that often need definition
    technical_terms = [
        'API', 'SDK', 'REST', 'SOAP', 'JSON', 'XML', 'HTTP', 'HTTPS',
        'SSL', 'TLS', 'VPN', 'DNS', 'TCP', 'UDP', 'IP',
        'GUI', 'CLI', 'IDE', 'CI/CD', 'DevOps',
        'SCADA', 'PLC', 'HMI', 'OPC UA', 'PROFINET', 'Modbus',
        'IoT', 'IIoT', 'Edge Computing', 'Cloud Computing'
    ]
    
    issues = []
    
    for term in technical_terms:
        # Find first occurrence
        pattern = re.compile(r'\b' + re.escape(term) + r'\b')
        first_match = pattern.search(text)
        
        if first_match:
            # Check if it's defined (look for parentheses or explanation nearby)
            start_check = max(0, first_match.start() - 100)
            end_check = min(len(text), first_match.end() + 100)
            context_check = text[start_check:end_check]
            
            # Look for definition patterns
            definition_patterns = [
                r'\([^)]*' + re.escape(term) + r'[^)]*\)',  # (acronym definition)
                r'\b' + re.escape(term) + r'\s*\([^)]+\)',   # TERM (definition)
                r'\b' + re.escape(term) + r'\s*[-–—]\s*\w+', # TERM - definition
                r'\b' + re.escape(term) + r'\s+is\s+\w+',    # TERM is definition
                r'\b' + re.escape(term) + r'\s+stands for'   # TERM stands for
            ]
            
            is_defined = any(re.search(pattern, context_check, re.IGNORECASE) 
                           for pattern in definition_patterns)
            
            if not is_defined:
                start = max(0, first_match.start() - 30)
                end = min(len(text), first_match.end() + 30)
                context = text[start:end]
                
                issues.append({
                    "term": term,
                    "context": context.strip(),
                    "first_occurrence": True
                })
    
    return issues

def find_acronym_issues(text):
    """Find acronym usage issues"""
    issues = []
    
    # Find potential acronyms (2+ capital letters)
    acronym_pattern = r'\b[A-Z]{2,}\b'
    acronyms = re.findall(acronym_pattern, text)
    
    for acronym in set(acronyms):  # Remove duplicates
        # Count occurrences
        count = text.count(acronym)
        
        # Find first occurrence
        first_match = text.find(acronym)
        
        if first_match != -1:
            # Check if acronym is expanded on first use
            start_check = max(0, first_match - 50)
            end_check = min(len(text), first_match + len(acronym) + 50)
            context_check = text[start_check:end_check]
            
            # Look for expansion patterns before or after the acronym
            expansion_patterns = [
                r'\([^)]*' + re.escape(acronym) + r'[^)]*\)',
                r'\b\w+(?:\s+\w+)*\s*\(' + re.escape(acronym) + r'\)',
                r'\b' + re.escape(acronym) + r'\s*\([^)]+\)'
            ]
            
            has_expansion = any(re.search(pattern, context_check) 
                              for pattern in expansion_patterns)
            
            if count > 1 and not has_expansion:
                start = max(0, first_match - 30)
                end = min(len(text), first_match + len(acronym) + 30)
                context = text[start:end]
                
                issues.append({
                    "message": f"Acronym '{acronym}' used {count} times but not expanded on first use",
                    "acronym": acronym,
                    "count": count,
                    "context": context.strip()
                })
    
    return issues

def find_industry_terminology_errors(text):
    """Find industry-specific terminology errors"""
    issues = []
    
    # Common industry terminology corrections
    corrections = {
        # Software development
        'web page': 'webpage',
        'open source': 'open-source',  # When used as adjective
        'real time': 'real-time',      # When used as adjective
        'plug in': 'plugin',           # As noun
        'log in': 'login',             # As noun
        'set up': 'setup',             # As noun
        'back up': 'backup',           # As noun
        
        # Industrial automation
        'human machine interface': 'human-machine interface',
        'supervisory control and data acquisition': 'SCADA',
        'programmable logic controller': 'PLC',
        
        # Common errors
        'data base': 'database',
        'fire wall': 'firewall',
        'pass word': 'password',
        'user name': 'username'
    }
    
    for incorrect, correct in corrections.items():
        pattern = re.compile(re.escape(incorrect), re.IGNORECASE)
        
        for match in pattern.finditer(text):
            # Check context to see if it's used as noun vs verb
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            issues.append({
                "message": f"Use '{correct}' instead of '{match.group()}'",
                "incorrect": match.group(),
                "correct": correct,
                "context": context.strip()
            })
    
    return issues

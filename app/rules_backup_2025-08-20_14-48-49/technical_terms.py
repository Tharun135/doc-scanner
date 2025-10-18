import re
import spacy
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

# Load spaCy English model (make sure to run: python -m spacy download en_core_web_sm)
nlp = spacy.load("en_core_web_sm")

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

    # Define doc using nlp
    doc = nlp(text_content)
    
    # Rule: Capitalize 'Bluetooth'
    bluetooth_pattern = r'\bbluetooth\b'
    matches = re.finditer(bluetooth_pattern, content)
    for match in matches:
        suggestions.append("Capitalize 'Bluetooth' as it's a proper noun.")

    # Rule: Use 'bounding box' instead of 'bounding outline'
    bounding_outline_pattern = r'\bbounding outline\b'
    matches = re.finditer(bounding_outline_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        suggestions.append(f"Use 'bounding box' instead of '{match.group()}'.")

    # Rule: Use 'Blu-ray Disc' with correct capitalization
    bluray_pattern = r'\bblu[-\s]?ray\s+disc\b'
    matches = re.finditer(bluray_pattern, content, flags=re.IGNORECASE)
    for match in matches:
        if match.group() != 'Blu-ray Disc':
            suggestions.append("Use 'Blu-ray Disc' with 'Disc' capitalized.")

    # Rule: Consistent API/URL formatting
    api_terms = {
        r'\bapi\b': 'API',
        r'\burl\b': 'URL',
        r'\buri\b': 'URI',
        r'\bhtml\b': 'HTML',
        r'\bcss\b': 'CSS',
        r'\bxml\b': 'XML',
        r'\bjson\b': 'JSON',
        r'\bhttp\b': 'HTTP',
        r'\bhttps\b': 'HTTPS',
        r'\bsql\b': 'SQL',
        r'\bui\b': 'UI',
        r'\bux\b': 'UX',
    }
    
    for pattern, correct_form in api_terms.items():
        # Only match when not already capitalized
        matches = re.finditer(pattern, content)
        for match in matches:
            if match.group() != correct_form:
                suggestions.append(f"Capitalize '{match.group()}' as '{correct_form}'.")

    # Rule: Consistent file extension formatting
    file_extensions = [
        r'\.txt\b', r'\.pdf\b', r'\.doc\b', r'\.docx\b', r'\.xls\b', r'\.xlsx\b',
        r'\.ppt\b', r'\.pptx\b', r'\.jpg\b', r'\.jpeg\b', r'\.png\b', r'\.gif\b',
        r'\.zip\b', r'\.exe\b', r'\.dll\b', r'\.sys\b'
    ]
    
    for pattern in file_extensions:
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            ext = match.group()
            if ext != ext.lower():
                suggestions.append(f"Use lowercase for file extension: '{ext}' → '{ext.lower()}'")

    # Rule: Proper product name capitalization
    product_names = {
        r'\bmicrosoft\b': 'Microsoft',
        r'\bwindows\b': 'Windows',
        r'\bmac\s+os\b': 'macOS',
        r'\bmacos\b': 'macOS',
        r'\bios\b': 'iOS',
        r'\bandroid\b': 'Android',
        r'\blinux\b': 'Linux',
        r'\bubuntu\b': 'Ubuntu',
        r'\bgoogle\b': 'Google',
        r'\bchrome\b': 'Chrome',
        r'\bfirefox\b': 'Firefox',
        r'\bsafari\b': 'Safari',
        r'\bedge\b': 'Edge',
        r'\boffice\s+365\b': 'Office 365',
        r'\bazure\b': 'Azure',
        r'\baws\b': 'AWS',
    }
    
    for pattern, correct_name in product_names.items():
        matches = re.finditer(pattern, content)
        for match in matches:
            if match.group() != correct_name:
                # Check if it's in a proper context (not just any occurrence)
                context = get_word_context(content, match)
                if is_product_context(context):
                    suggestions.append(f"Capitalize product name: '{match.group()}' → '{correct_name}'")

    # Rule: Consistent unit abbreviations
    unit_abbreviations = {
        r'\bkilobyte\b': 'KB',
        r'\bmegabyte\b': 'MB', 
        r'\bgigabyte\b': 'GB',
        r'\bterabyte\b': 'TB',
        r'\bkilohertz\b': 'kHz',
        r'\bmegahertz\b': 'MHz',
        r'\bgigahertz\b': 'GHz',
        r'\bmillisecond\b': 'ms',
        r'\bmicrosecond\b': 'μs',
    }
    
    for pattern, abbreviation in unit_abbreviations.items():
        matches = re.finditer(pattern, content, flags=re.IGNORECASE)
        for match in matches:
            suggestions.append(f"Consider using standard abbreviation: '{match.group()}' → '{abbreviation}'")

    return suggestions if suggestions else []

def get_word_context(content, match, context_size=20):
    """Get context around a match for better analysis."""
    start = max(0, match.start() - context_size)
    end = min(len(content), match.end() + context_size)
    return content[start:end]

def is_product_context(context):
    """Check if the context suggests this is referring to a product/technology."""
    context_lower = context.lower()
    product_indicators = [
        'operating system', 'browser', 'application', 'software', 'platform',
        'version', 'release', 'install', 'download', 'support', 'compatible',
        'runs on', 'works with', 'available for', 'designed for'
    ]
    return any(indicator in context_lower for indicator in product_indicators)

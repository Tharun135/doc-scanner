import re
from bs4 import BeautifulSoup
import html

# COMPLETELY CLEAN VERSION - NO AI DEPENDENCIES FOR FAST LOADING

def check(content):
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()

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
        r'(?<!\.)\bhtml\b': 'HTML',  # Don't match .html file extensions
        r'(?<!\.)\bcss\b': 'CSS',   # Don't match .css file extensions
        r'(?<!\.)\bxml\b': 'XML',   # Don't match .xml file extensions
        r'(?<!\.)\bjson\b': 'JSON', # Don't match .json file extensions
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

    return suggestions if suggestions else []

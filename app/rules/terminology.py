"""
Term# Import the RAG helper for rule-based suggestions
try:
    from .rag_main import get_rag_suggestion, is_rag_available
except ImportError:
    def get_rag_suggestion(issue_text, sentence_context, category="terminology"):
        return {"suggestion": f"Terminology issue: {issue_text}", "confidence": 0.5}
    def is_rag_available():
        return FalseRules
Ensures consistent use of terminology, product names, and technical terms.
"""

import re
import logging
from typing import List, Dict, Any

# Import the AI helper
try:
    from .llamaindex_helper import get_rag_suggestion, is_ai_available
except ImportError:
    def get_rag_suggestion(issue_text, sentence_context, category="terminology"):
        return {"suggestion": f"Terminology issue: {issue_text}", "confidence": 0.5}
    def is_ai_available():
        return False

logger = logging.getLogger(__name__)

def check(content: str) -> List[str]:
    """
    Check for terminology issues.
    Returns AI-powered suggestions for all detected issues.
    """
    suggestions = []
    
    # Split content into sentences for analysis
    sentences = _split_into_sentences(content)
    
    for sentence in sentences:
        # 1. Product name capitalization
        product_issues = _check_product_names(sentence)
        for issue in product_issues:
            rag_response = get_rag_suggestion(
                issue_text="Product name capitalization",
                sentence_context=sentence,
                category="terminology"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 2. Technical term consistency
        tech_term_issues = _check_technical_terms(sentence)
        for issue in tech_term_issues:
            rag_response = get_rag_suggestion(
                issue_text="Technical term consistency",
                sentence_context=sentence,
                category="terminology"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 3. Acronym usage
        acronym_issues = _check_acronym_usage(sentence)
        for issue in acronym_issues:
            rag_response = get_rag_suggestion(
                issue_text="Acronym usage issue",
                sentence_context=sentence,
                category="terminology"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 4. Inconsistent terminology
        consistency_issues = _check_terminology_consistency(sentence, content)
        for issue in consistency_issues:
            rag_response = get_rag_suggestion(
                issue_text="Terminology inconsistency",
                sentence_context=sentence,
                category="terminology"
            )
            suggestions.append(rag_response.get("suggestion", issue))
    
    return suggestions

def _split_into_sentences(content: str) -> List[str]:
    """Split content into sentences while preserving formatting within sentences."""
    import re
    
    # Clean up extra whitespace but preserve sentence structure
    content = re.sub(r'\s+', ' ', content.strip())
    
    # Split only on sentence-ending punctuation followed by whitespace and capital letter
    sentences = re.split(r'([.!?]+)\s+(?=[A-Z])', content)
    
    # Reconstruct sentences with their punctuation
    result = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            sentence = sentences[i] + sentences[i + 1]
            if sentence.strip():
                result.append(sentence.strip())
        else:
            if sentences[i].strip():
                result.append(sentences[i].strip())
    
    # Handle case where content doesn't end with proper punctuation
    if sentences and not result and content.strip():
        result = [content.strip()]
    
    return result

def _check_product_names(sentence: str) -> List[str]:
    """Check for proper product name capitalization."""
    issues = []
    
    # Common product names that should be capitalized correctly
    product_names = {
        r'\bmicrosoft\b': 'Microsoft',
        r'\bwindows\b': 'Windows',
        r'\boffice\b': 'Office',
        r'\bexcel\b': 'Excel',
        r'\bword\b': 'Word',
        r'\bpowerpoint\b': 'PowerPoint',
        r'\boutlook\b': 'Outlook',
        r'\bgoogle\b': 'Google',
        r'\bchrome\b': 'Chrome',
        r'\bfirefox\b': 'Firefox',
        r'\bsafari\b': 'Safari',
        r'\bapple\b': 'Apple',
        r'\bmac\b': 'Mac',
        r'\biphone\b': 'iPhone',
        r'\bipad\b': 'iPad',
        r'\blinux\b': 'Linux',
        r'\bubuntu\b': 'Ubuntu',
        r'\bcentos\b': 'CentOS',
        r'\bredhat\b': 'Red Hat',
        r'\bordacle\b': 'Oracle',
        r'\bmysql\b': 'MySQL',
        r'\bpostgresql\b': 'PostgreSQL',
        r'\bmongodb\b': 'MongoDB'
    }
    
    for pattern, correct_name in product_names.items():
        matches = re.finditer(pattern, sentence, re.IGNORECASE)
        for match in matches:
            if match.group() != correct_name:
                issues.append(f"Product name should be '{correct_name}': {match.group()}")
    
    return issues

def _check_technical_terms(sentence: str) -> List[str]:
    """Check for technical term consistency."""
    issues = []
    
    # Technical terms with preferred forms
    technical_terms = {
        r'\be-mail\b': 'email',
        r'\bweb site\b': 'website',
        r'\bweb page\b': 'webpage',
        r'\bdata base\b': 'database',
        r'\bfile name\b': 'filename',
        r'\buser name\b': 'username',
        r'\bpass word\b': 'password',
        r'\bwifi\b': 'Wi-Fi',
        r'\binternet\b': 'Internet',
        r'\bworldwide web\b': 'World Wide Web',
        r'\bworld wide web\b': 'World Wide Web'
    }
    
    for pattern, preferred in technical_terms.items():
        matches = re.finditer(pattern, sentence, re.IGNORECASE)
        for match in matches:
            if match.group().lower() != preferred.lower():
                issues.append(f"Use '{preferred}' instead of '{match.group()}'")
    
    return issues

def _check_acronym_usage(sentence: str) -> List[str]:
    """Check for proper acronym usage."""
    issues = []
    
    # Check for undefined acronyms (basic check)
    acronym_pattern = r'\b[A-Z]{2,}\b'
    acronyms = re.findall(acronym_pattern, sentence)
    
    # Common acronyms that don't need definition
    common_acronyms = {
        'URL', 'HTML', 'CSS', 'JS', 'API', 'HTTP', 'HTTPS', 'FTP', 'SSH',
        'PDF', 'CSV', 'XML', 'JSON', 'SQL', 'CPU', 'GPU', 'RAM', 'ROM',
        'USB', 'HDMI', 'WiFi', 'GPS', 'DVD', 'CD', 'HD', 'SD', 'GB', 'MB',
        'KB', 'TB', 'AI', 'ML', 'IoT', 'VPN', 'DNS', 'IP', 'TCP', 'UDP'
    }
    
    for acronym in acronyms:
        if acronym not in common_acronyms and len(acronym) > 2:
            # This is a simplified check - in practice, you'd track defined acronyms
            if not re.search(rf'\b{re.escape(acronym)}\s*\([^)]+\)', sentence):
                issues.append(f"Consider defining acronym '{acronym}' on first use")
    
    return issues

def _check_terminology_consistency(sentence: str, full_content: str) -> List[str]:
    """Check for terminology consistency across the document."""
    issues = []
    
    # Look for variant spellings of the same concept
    variant_groups = [
        ['email', 'e-mail', 'Email', 'E-mail'],
        ['website', 'web site', 'Website', 'Web site'],
        ['login', 'log in', 'log-in', 'Login'],
        ['setup', 'set up', 'set-up', 'Setup'],
        ['backup', 'back up', 'back-up', 'Backup'],
        ['online', 'on-line', 'on line', 'Online'],
        ['offline', 'off-line', 'off line', 'Offline']
    ]
    
    for variants in variant_groups:
        found_variants = []
        for variant in variants:
            if re.search(rf'\b{re.escape(variant)}\b', full_content, re.IGNORECASE):
                found_variants.append(variant)
        
        if len(found_variants) > 1:
            # Check if current sentence contains any variant
            for variant in variants:
                if re.search(rf'\b{re.escape(variant)}\b', sentence, re.IGNORECASE):
                    issues.append(f"Inconsistent terminology: multiple forms used - {', '.join(found_variants)}")
                    break
    
    return issues

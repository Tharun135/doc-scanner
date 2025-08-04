"""
Rule for checking cross-references, links, and citation consistency.
Ensures proper formatting and consistency of internal references, external links, and citations.
"""

import re
from bs4 import BeautifulSoup
import html
from urllib.parse import urlparse

# Import RAG system with fallback
try:
    from .rag_rule_helper import check_with_rag
    RAG_HELPER_AVAILABLE = True
except ImportError:
    RAG_HELPER_AVAILABLE = False
    import logging
    logging.debug(f"RAG helper not available for {__name__} - using basic rules")

def check(content):
    """Check for cross-reference and link consistency issues."""
    suggestions = []

    # Parse HTML to handle links properly
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Use RAG system if available
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(
            content,
            "cross_references_links",
            "Check for cross-reference consistency, broken link patterns, and citation formatting issues."
        )
        if rag_suggestions:
            return rag_suggestions

    # Fallback to rule-based detection
    suggestions.extend(check_internal_references(text_content))
    suggestions.extend(check_link_formatting(content, soup))
    suggestions.extend(check_citation_consistency(text_content))
    suggestions.extend(check_section_references(text_content))
    suggestions.extend(check_figure_table_references(text_content))

    return suggestions if suggestions else []

def check_internal_references(text_content):
    """Check for consistent internal reference formatting."""
    suggestions = []
    
    # Find different patterns of section references
    section_ref_patterns = [
        r'\bsee\s+section\s+\d+',
        r'\bsee\s+chapter\s+\d+',
        r'\brefer\s+to\s+section\s+\d+',
        r'\bin\s+section\s+\d+',
        r'\bsection\s+\d+\.\d+',
        r'\bchapter\s+\d+\.\d+',
    ]
    
    found_patterns = []
    for pattern in section_ref_patterns:
        matches = list(re.finditer(pattern, text_content, flags=re.IGNORECASE))
        if matches:
            found_patterns.append((pattern, len(matches)))
    
    if len(found_patterns) > 1:
        suggestions.append("Inconsistent section reference formatting. Consider using a consistent style throughout the document.")
    
    # Check for missing references
    orphaned_references = re.findall(r'\b(?:see|refer to|as mentioned in|as described in)\s+(?:the\s+)?\w*\s*$', text_content, flags=re.IGNORECASE)
    if orphaned_references:
        suggestions.append("Incomplete references found. Ensure all 'see' or 'refer to' statements include specific section or page numbers.")
    
    return suggestions

def check_link_formatting(content, soup):
    """Check for consistent link formatting and potential issues."""
    suggestions = []
    
    # Find all links
    links = soup.find_all('a', href=True)
    
    if not links:
        # Check for URLs in plain text that should be links
        url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+|[^\s<>"\']+\.[a-z]{2,}(?:/[^\s<>"\']*)?'
        urls_in_text = re.findall(url_pattern, soup.get_text(), flags=re.IGNORECASE)
        
        if urls_in_text:
            suggestions.append(f"Found {len(urls_in_text)} potential URLs in plain text. Consider making them clickable links.")
        
        return suggestions
    
    # Check link text quality
    poor_link_texts = ['click here', 'here', 'this link', 'read more', 'link', 'click this']
    
    for link in links:
        link_text = link.get_text().strip().lower()
        if link_text in poor_link_texts:
            suggestions.append(f"Non-descriptive link text: '{link_text}'. Use descriptive text that explains the destination.")
    
    # Check for external links without proper indicators
    external_links = []
    internal_links = []
    
    for link in links:
        href = link.get('href', '')
        if href.startswith(('http://', 'https://')):
            external_links.append(link)
        elif href.startswith(('#', '/', './')):
            internal_links.append(link)
    
    if external_links:
        # Check if external links are properly indicated
        for link in external_links:
            link_text = link.get_text()
            if not any(indicator in link_text.lower() for indicator in ['external', 'opens in new', 'new window', 'new tab']):
                # Check if there's a visual indicator nearby
                next_sibling = link.next_sibling
                if not (next_sibling and ('↗' in str(next_sibling) or 'external' in str(next_sibling).lower())):
                    suggestions.append(f"External link '{link_text}' may need an indicator (e.g., icon or '(external link)') for accessibility.")
    
    # Check for consistent URL formatting
    url_formats = set()
    for link in external_links:
        href = link.get('href')
        parsed = urlparse(href)
        if parsed.scheme:
            url_formats.add(parsed.scheme)
    
    if 'http' in url_formats and 'https' in url_formats:
        suggestions.append("Mixed HTTP and HTTPS links found. Consider using HTTPS consistently for security.")
    
    return suggestions

def check_citation_consistency(text_content):
    """Check for consistent citation formatting."""
    suggestions = []
    
    # Find different citation patterns
    citation_patterns = [
        r'\[\d+\]',           # [1]
        r'\(\d+\)',           # (1)
        r'\(\w+,?\s*\d{4}\)', # (Author, 2023)
        r'\(\w+\s+et\s+al\.,?\s*\d{4}\)', # (Author et al., 2023)
        r'\[\w+,?\s*\d{4}\]', # [Author, 2023]
    ]
    
    found_citation_styles = []
    for pattern in citation_patterns:
        matches = list(re.finditer(pattern, text_content))
        if matches:
            found_citation_styles.append((pattern, len(matches)))
    
    if len(found_citation_styles) > 1:
        suggestions.append("Inconsistent citation formatting. Use a consistent citation style throughout the document.")
    
    # Check for incomplete citations
    incomplete_citations = re.findall(r'\b(?:according to|as stated by|reference|cite)\s+\w*\s*$', text_content, flags=re.IGNORECASE)
    if incomplete_citations:
        suggestions.append("Incomplete citations found. Ensure all citation statements include proper references.")
    
    return suggestions

def check_section_references(text_content):
    """Check for consistent section numbering and references."""
    suggestions = []
    
    # Find section numbers
    section_numbers = re.findall(r'^\s*(\d+(?:\.\d+)*)\s+[A-Z]', text_content, flags=re.MULTILINE)
    
    if len(section_numbers) > 1:
        # Check for consistent numbering depth
        depths = [len(num.split('.')) for num in section_numbers]
        if len(set(depths)) > 3:  # More than 3 different depths
            suggestions.append("Inconsistent section numbering depth. Consider limiting to 2-3 levels for better readability.")
        
        # Check for sequential numbering
        main_sections = [num for num in section_numbers if '.' not in num]
        if len(main_sections) > 1:
            try:
                numbers = [int(num) for num in main_sections]
                expected = list(range(1, len(numbers) + 1))
                if numbers != expected:
                    suggestions.append("Non-sequential section numbering detected. Ensure sections are numbered consecutively.")
            except ValueError:
                pass  # Skip if numbers can't be parsed
    
    return suggestions

def check_figure_table_references(text_content):
    """Check for consistent figure and table references."""
    suggestions = []
    
    # Find figure references
    figure_refs = re.findall(r'\b(?:figure|fig\.?)\s*(\d+)', text_content, flags=re.IGNORECASE)
    table_refs = re.findall(r'\btable\s*(\d+)', text_content, flags=re.IGNORECASE)
    
    # Check figure reference consistency
    if figure_refs:
        figure_ref_styles = set()
        for match in re.finditer(r'\b(figure|fig\.?)\s*\d+', text_content, flags=re.IGNORECASE):
            style = match.group(1).lower()
            figure_ref_styles.add(style)
        
        if len(figure_ref_styles) > 1:
            suggestions.append("Inconsistent figure reference style. Use either 'Figure' or 'Fig.' consistently.")
    
    # Check for orphaned references
    all_figure_numbers = set(figure_refs)
    all_table_numbers = set(table_refs)
    
    # Look for actual figure/table captions
    figure_captions = re.findall(r'\b(?:figure|fig\.?)\s*(\d+):', text_content, flags=re.IGNORECASE)
    table_captions = re.findall(r'\btable\s*(\d+):', text_content, flags=re.IGNORECASE)
    
    caption_figures = set(figure_captions)
    caption_tables = set(table_captions)
    
    # Check for references without captions
    orphaned_figures = all_figure_numbers - caption_figures
    orphaned_tables = all_table_numbers - caption_tables
    
    if orphaned_figures:
        suggestions.append(f"Figure references without captions: {', '.join(sorted(orphaned_figures))}. Ensure all referenced figures have captions.")
    
    if orphaned_tables:
        suggestions.append(f"Table references without captions: {', '.join(sorted(orphaned_tables))}. Ensure all referenced tables have captions.")
    
    return suggestions

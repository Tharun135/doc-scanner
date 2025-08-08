"""
Smart Rule Filtering - Only run relevant rules per sentence
This dramatically reduces processing time by applying intelligent rule selection.
"""

import re
from typing import List, Dict, Set

# Rule categories and their triggers
RULE_TRIGGERS = {
    # Technical content rules
    "technical_terms": ["api", "json", "html", "css", "xml", "http", "url", "uri", "sql"],
    "technical_terms_clean": ["api", "json", "html", "css", "xml", "http", "url", "uri", "sql"],
    "computer_device_terms": ["computer", "device", "hardware", "software", "system"],
    "cloud_computing_terms": ["cloud", "server", "hosting", "deployment", "infrastructure"],
    "css_terms": ["css", "style", "stylesheet", "class", "selector"],
    "c_languages_terms": ["c++", "java", "python", "javascript", "programming"],
    
    # Grammar and style rules (always apply)
    "grammar_issues": ["always"],
    "grammar_word_choice": ["always"],
    "passive_voice": ["always"],
    "long_sentences": ["always"],
    "simple_present_tense": ["always"],
    "repeated_words": ["always"],
    
    # Content-specific rules
    "accessibility_terms": ["accessibility", "screen reader", "alt text", "aria"],
    "security_terms": ["security", "password", "encryption", "authentication"],
    "ai_bot_terms": ["ai", "artificial intelligence", "bot", "machine learning"],
    
    # UI/UX rules
    "mouse_interaction_terms": ["click", "mouse", "cursor", "hover"],
    "keys_keyboard_shortcuts": ["key", "keyboard", "shortcut", "ctrl", "alt"],
    "touch_pen_interaction_terms": ["touch", "tap", "swipe", "pen", "stylus"],
    
    # Document structure rules
    "document_structure": ["heading", "section", "paragraph", "list"],
    "cross_references": ["see", "refer", "chapter", "section"],
    "style_formatting": ["bold", "italic", "format", "style"],
    
    # Language rules
    "contractions_rule": ["don't", "won't", "can't", "isn't", "aren't"],
    "inclusive_language": ["always"],  # Important for all content
    "tone_voice": ["always"],  # Important for all content
    
    # Measurement and units
    "units_of_measure_terms": ["inch", "foot", "meter", "gram", "byte", "gb", "mb"],
    
    # Specific term rules (only when relevant)
    "cable_terms": ["cable", "wire", "connector", "ethernet"],
    "cache_terms": ["cache", "memory", "storage", "buffer"],
    "calendar_terms": ["calendar", "date", "time", "schedule"],
    "callback_terms": ["callback", "function", "method", "procedure"],
    "callout_terms": ["note", "warning", "tip", "important"],
    "cancel_terms": ["cancel", "stop", "abort", "exit"],
    "can_may_terms": ["can", "may", "might", "could"],
    "catalog_terms": ["catalog", "directory", "index", "list"],
    "run_vs_carryout_terms": ["run", "execute", "carry out", "perform"],
}

def get_sentence_keywords(sentence: str) -> Set[str]:
    """Extract keywords from a sentence for rule matching."""
    # Convert to lowercase and extract words
    words = re.findall(r'\b\w+\b', sentence.lower())
    
    # Add common technical patterns
    keywords = set(words)
    
    # Check for technical patterns
    if re.search(r'\b\w+\.(com|org|net|html|css|js)\b', sentence.lower()):
        keywords.update(["url", "web", "technical"])
    
    if re.search(r'\b[A-Z]{2,}\b', sentence):  # Acronyms
        keywords.add("technical")
    
    return keywords

def get_relevant_rules(sentence: str, all_rules: Dict) -> List:
    """Filter rules to only those relevant for the given sentence."""
    sentence_keywords = get_sentence_keywords(sentence)
    relevant_rules = []
    applied_rule_names = []
    
    for rule_name, rule_function in all_rules.items():
        # Get rule filename without extension
        rule_key = rule_name.replace('.py', '') if rule_name.endswith('.py') else rule_name
        
        # Check if this rule should be applied
        if rule_key in RULE_TRIGGERS:
            rule_triggers = RULE_TRIGGERS[rule_key]
            
            # Always apply rules marked as "always"
            if "always" in rule_triggers:
                relevant_rules.append(rule_function)
                applied_rule_names.append(rule_key)
                continue
            
            # Check if any trigger keywords match
            if any(trigger in sentence_keywords for trigger in rule_triggers):
                relevant_rules.append(rule_function)
                applied_rule_names.append(rule_key)
                continue
    
    # Always include core grammar rules for quality
    core_rules = ["grammar_issues", "passive_voice", "long_sentences", "repeated_words"]
    for rule_name, rule_function in all_rules.items():
        rule_key = rule_name.replace('.py', '') if rule_name.endswith('.py') else rule_name
        if rule_key in core_rules and rule_function not in relevant_rules:
            relevant_rules.append(rule_function)
            applied_rule_names.append(f"{rule_key}(core)")
    
    print(f"   → Applied rules: {applied_rule_names}")
    return relevant_rules

def analyze_sentence_smart(sentence: str, all_rules: Dict) -> tuple:
    """
    Smart sentence analysis - only applies relevant rules.
    This replaces the original analyze_sentence function.
    """
    relevant_rules = get_relevant_rules(sentence, all_rules)
    print(f"🔍 SMART FILTERING: Reduced from {len(all_rules)} to {len(relevant_rules)} rules for sentence")
    
    # Only run relevant rules instead of all 46 rules
    feedback = []
    for rule_function in relevant_rules:
        try:
            suggestions = rule_function(sentence)
            if suggestions:
                feedback.extend(suggestions)
        except Exception as e:
            import logging
            logging.warning(f"Rule failed for sentence: {e}")
    
    # Calculate readability scores (lightweight)
    try:
        import textstat
        readability_scores = {
            "flesch_reading_ease": textstat.flesch_reading_ease(sentence),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(sentence),
        }
    except:
        readability_scores = {"flesch_reading_ease": 0, "flesch_kincaid_grade": 0}
    
    # Simple quality score based on feedback count
    quality_score = max(0, 100 - (len(feedback) * 5))
    
    return feedback, readability_scores, quality_score

def get_smart_performance_stats(sentences: List[str], all_rules: Dict) -> Dict:
    """Get performance statistics for smart rule filtering."""
    total_rules = len(all_rules)
    total_sentences = len(sentences)
    total_possible_executions = total_rules * total_sentences
    
    actual_executions = 0
    for sentence in sentences:
        relevant_rules = get_relevant_rules(sentence, all_rules)
        actual_executions += len(relevant_rules)
    
    reduction_percentage = ((total_possible_executions - actual_executions) / total_possible_executions) * 100
    
    return {
        "total_rules": total_rules,
        "total_sentences": total_sentences,
        "total_possible_executions": total_possible_executions,
        "actual_executions": actual_executions,
        "reduction_percentage": reduction_percentage,
        "avg_rules_per_sentence": actual_executions / total_sentences if total_sentences > 0 else 0
    }

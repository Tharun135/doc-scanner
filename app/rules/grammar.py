"""
Grammar and Syntax Rules
Comprehensive grammar checking with AI-powered suggestions.
"""

import re
import logging
from typing import List, Dict, Any

# Import the RAG helper for rule-based suggestions
try:
    from .rag_main import get_rag_suggestion, is_rag_available
except ImportError:
    def get_rag_suggestion(issue_text, sentence_context, category="grammar"):
        return {"suggestion": f"Grammar issue: {issue_text}", "confidence": 0.5}
    def is_rag_available():
        return False

logger = logging.getLogger(__name__)

def check(content: str) -> List[str]:
    """
    Check for grammar and syntax issues.
    Returns AI-powered suggestions for all detected issues.
    """
    suggestions = []
    
    # Split content into sentences for analysis
    sentences = _split_into_sentences(content)
    
    for sentence in sentences:
        # 1. Subject-verb agreement
        agreement_issues = _check_subject_verb_agreement(sentence)
        for issue in agreement_issues:
            rag_response = get_rag_suggestion(
                issue_text="Subject-verb agreement error",
                sentence_context=sentence,
                category="grammar"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 2. Verb tense consistency
        tense_issues = _check_verb_tense_consistency(sentence, content)
        for issue in tense_issues:
            rag_response = get_rag_suggestion(
                issue_text="Verb tense consistency",
                sentence_context=sentence,
                category="grammar"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 3. Pronoun reference clarity
        pronoun_issues = _check_pronoun_reference(sentence)
        for issue in pronoun_issues:
            rag_response = get_rag_suggestion(
                issue_text="Unclear pronoun reference",
                sentence_context=sentence,
                category="grammar"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 4. Parallel structure
        parallel_issues = _check_parallel_structure(sentence)
        for issue in parallel_issues:
            rag_response = get_rag_suggestion(
                issue_text="Parallel structure",
                sentence_context=sentence,
                category="grammar"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 5. Modifier placement
        modifier_issues = _check_modifier_placement(sentence)
        for issue in modifier_issues:
            rag_response = get_rag_suggestion(
                issue_text="Modifier placement",
                sentence_context=sentence,
                category="grammar"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 6. Sentence fragments
        fragment_issues = _check_sentence_fragments(sentence)
        for issue in fragment_issues:
            rag_response = get_rag_suggestion(
                issue_text="Sentence fragment",
                sentence_context=sentence,
                category="grammar"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 7. Run-on sentences
        runon_issues = _check_run_on_sentences(sentence)
        for issue in runon_issues:
            rag_response = get_rag_suggestion(
                issue_text="Run-on sentence",
                sentence_context=sentence,
                category="grammar"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 8. Passive voice detection
        passive_issues = _check_passive_voice(sentence)
        for issue in passive_issues:
            rag_response = get_rag_suggestion(
                issue_text="Passive voice detected",
                sentence_context=sentence,
                category="grammar"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 9. Common grammar errors
        common_issues = _check_common_errors(sentence)
        for issue in common_issues:
            rag_response = get_rag_suggestion(
                issue_text="Common grammar error",
                sentence_context=sentence,
                category="grammar"
            )
            suggestions.append(rag_response.get("suggestion", issue))
        
        # 10. Article usage (a/an/the)
        article_issues = _check_article_usage(sentence)
        for issue in article_issues:
            rag_response = get_rag_suggestion(
                issue_text="Article usage",
                sentence_context=sentence,
                category="grammar"
            )
            suggestions.append(rag_response.get("suggestion", issue))
    
    return suggestions

def _split_into_sentences(content: str) -> List[str]:
    """Split content into sentences."""
    sentences = re.split(r'[.!?]+', content)
    return [s.strip() for s in sentences if s.strip()]

def _check_subject_verb_agreement(sentence: str) -> List[str]:
    """Check for subject-verb agreement issues."""
    issues = []
    
    # Common patterns that often have agreement issues
    patterns = [
        # Singular subjects with plural verbs
        (r'\b(each|every|either|neither|one|someone|everyone|anyone|nobody|somebody)\s+\w*\s+(are|were|have)', 
         'Singular subject needs singular verb'),
        
        # Plural subjects with singular verbs  
        (r'\b(data|criteria|phenomena|media)\s+(is|was|has)',
         'Plural subject needs plural verb'),
        
        # Subject separated by prepositional phrase
        (r'\b(\w+)\s+of\s+\w+\s+(is|are)',
         'Check if subject agrees with verb'),
        
        # Compound subjects
        (r'\b\w+\s+and\s+\w+\s+(is|was)',
         'Compound subjects usually need plural verbs'),
    ]
    
    for pattern, message in patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            issues.append(f"{message}: '{sentence[:50]}...'")
    
    return issues

def _check_verb_tense_consistency(sentence: str, full_content: str) -> List[str]:
    """Check for verb tense consistency."""
    issues = []
    
    # Find tenses in current sentence
    past_tense = re.findall(r'\b\w+ed\b|\bwas\b|\bwere\b|\bhad\b', sentence, re.IGNORECASE)
    present_tense = re.findall(r'\bis\b|\bare\b|\bam\b|\bhave\b|\bhas\b', sentence, re.IGNORECASE)
    future_tense = re.findall(r'\bwill\b|\bshall\b|\bgoing to\b', sentence, re.IGNORECASE)
    
    # Count tenses in full document to determine primary tense
    doc_past = len(re.findall(r'\b\w+ed\b|\bwas\b|\bwere\b|\bhad\b', full_content, re.IGNORECASE))
    doc_present = len(re.findall(r'\bis\b|\bare\b|\bam\b|\bhave\b|\bhas\b', full_content, re.IGNORECASE))
    doc_future = len(re.findall(r'\bwill\b|\bshall\b|\bgoing to\b', full_content, re.IGNORECASE))
    
    # If sentence has mixed tenses
    tense_count = sum([1 for x in [past_tense, present_tense, future_tense] if x])
    if tense_count > 1:
        issues.append("Mixed verb tenses in sentence - maintain consistency")
    
    # Check if sentence tense differs from document primary tense
    primary_tense = max(doc_past, doc_present, doc_future)
    if primary_tense > 5:  # Only check if there's enough content
        if primary_tense == doc_present and past_tense and not present_tense:
            issues.append("Inconsistent tense - document primarily uses present tense")
        elif primary_tense == doc_past and present_tense and not past_tense:
            issues.append("Inconsistent tense - document primarily uses past tense")
    
    return issues

def _check_pronoun_reference(sentence: str) -> List[str]:
    """Check for unclear pronoun references."""
    issues = []
    
    # Find pronouns that might be ambiguous
    ambiguous_pronouns = re.findall(r'\b(it|this|that|they|them|their|which)\b', sentence, re.IGNORECASE)
    
    for pronoun in ambiguous_pronouns:
        # Check if there are multiple possible antecedents
        words_before = sentence.split(pronoun.lower())[0].split()[-10:]  # Last 10 words before pronoun
        nouns = [word for word in words_before if re.match(r'^[A-Z][a-z]+$', word)]
        
        if len(nouns) > 2:  # Multiple possible antecedents
            issues.append(f"Unclear pronoun reference: '{pronoun}' - clarify what it refers to")
    
    return issues

def _check_parallel_structure(sentence: str) -> List[str]:
    """Check for parallel structure in lists and series."""
    issues = []
    
    # Look for lists with "and", "or", commas
    list_patterns = [
        r'(\w+ing),\s*(\w+ed),?\s*and\s*(\w+)',  # Mixed verb forms
        r'(\w+),\s*(\w+ing),?\s*and\s*(\w+ed)',  # Mixed structures
        r'(to\s+\w+),\s*(\w+ing),?\s*and\s*(\w+)',  # Mixed infinitive/gerund
    ]
    
    for pattern in list_patterns:
        matches = re.finditer(pattern, sentence, re.IGNORECASE)
        for match in matches:
            issues.append(f"Non-parallel structure in list: '{match.group()}'")
    
    return issues

def _check_modifier_placement(sentence: str) -> List[str]:
    """Check for misplaced or dangling modifiers."""
    issues = []
    
    # Dangling modifier patterns
    dangling_patterns = [
        r'^(After|Before|While|When|Since|Because)\s+\w+ing\s+\w+,\s+(the|a|an)\s+\w+',
        r'^(Having|Being|Running|Walking|Driving)\s+\w+,\s+(the|a|an)\s+\w+',
    ]
    
    for pattern in dangling_patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            issues.append("Possible dangling modifier - ensure modifier clearly relates to subject")
    
    # Misplaced "only" and similar modifiers
    misplaced_patterns = [
        r'\bonly\s+\w+\s+\w+\s+\w+',  # "only" too far from what it modifies
        r'\bjust\s+\w+\s+\w+\s+\w+',  # "just" misplaced
        r'\balmost\s+\w+\s+\w+\s+\w+',  # "almost" misplaced
    ]
    
    for pattern in misplaced_patterns:
        if re.search(pattern, sentence, re.IGNORECASE):
            match = re.search(pattern, sentence, re.IGNORECASE)
            issues.append(f"Check modifier placement: '{match.group()}'")
    
    return issues

def _check_sentence_fragments(sentence: str) -> List[str]:
    """Check for sentence fragments."""
    issues = []
    
    # Remove leading/trailing whitespace and check length
    clean_sentence = sentence.strip()
    if len(clean_sentence) < 5:
        return issues
    
    # Fragment indicators
    fragment_patterns = [
        r'^(Because|Since|Although|While|When|If|Unless|After|Before)\s+',  # Starts with subordinate
        r'^(And|But|Or|So)\s+',  # Starts with coordinating conjunction
        r'^\w+ing\s+',  # Starts with gerund
        r'^To\s+\w+',  # Starts with infinitive
    ]
    
    # Must have a main verb
    has_main_verb = bool(re.search(r'\b(is|are|was|were|have|has|had|will|would|can|could|should|must|do|does|did)\b', clean_sentence, re.IGNORECASE))
    
    for pattern in fragment_patterns:
        if re.search(pattern, clean_sentence, re.IGNORECASE) and not has_main_verb:
            issues.append(f"Possible sentence fragment: '{clean_sentence[:30]}...'")
            break
    
    return issues

def _check_run_on_sentences(sentence: str) -> List[str]:
    """Check for run-on sentences."""
    issues = []
    
    # Count independent clauses
    conjunctions = len(re.findall(r'\b(and|but|or|so|yet|for|nor)\b', sentence, re.IGNORECASE))
    comma_splices = len(re.findall(r',\s+\w+\s+(is|are|was|were|have|has|had|will|would)', sentence, re.IGNORECASE))
    
    # Very long sentences are likely run-ons
    word_count = len(sentence.split())
    
    if word_count > 30:
        issues.append(f"Very long sentence ({word_count} words) - consider breaking into shorter sentences")
    elif conjunctions > 2:
        issues.append("Multiple independent clauses - consider breaking into separate sentences")
    elif comma_splices > 0:
        issues.append("Possible comma splice - use semicolon or separate sentences")
    
    return issues

def _check_passive_voice(sentence: str) -> List[str]:
    """Check for passive voice constructions."""
    issues = []
    
    # Passive voice patterns
    passive_patterns = [
        r'\b(is|are|was|were|been|being)\s+\w+ed\b',  # be + past participle
        r'\b(is|are|was|were|been|being)\s+\w+en\b',  # be + past participle (irregular)
        r'\b(get|gets|got|getting)\s+\w+ed\b',       # get passive
        r'\b(become|becomes|became)\s+\w+ed\b',      # become passive
    ]
    
    for pattern in passive_patterns:
        matches = re.finditer(pattern, sentence, re.IGNORECASE)
        for match in matches:
            # Skip legitimate passive constructions (past participles as adjectives)
            context = sentence[max(0, match.start()-20):match.end()+20]
            if not re.search(r'\b(by|from|with)\s+\w+', context, re.IGNORECASE):
                issues.append(f"Consider active voice instead of: '{match.group()}'")
    
    return issues

def _check_common_errors(sentence: str) -> List[str]:
    """Check for common grammar errors."""
    issues = []
    
    # Common errors with corrections
    common_errors = {
        r'\bits\s+is\b': "it's (it is) vs its (possessive)",
        r'\byour\s+(going|coming|running)\b': "you're (you are)",
        r'\btheir\s+(going|coming|running)\b': "they're (they are)",
        r'\bwho\'s\s+\w+\b': "whose (possessive) vs who's (who is)",
        r'\beffect\s+(on|change)\b': "affect (verb) vs effect (noun)",
        r'\baccept\s+(for|that)\b': "except vs accept",
        r'\bthen\s+(it|this|that)\b': "than (comparison) vs then (time)",
        r'\blose\s+(my|your|the)\b': "loose (not tight) vs lose (misplace)",
        r'\badvice\s+(you|me)\b': "advise (verb) vs advice (noun)",
        r'\bbreath\s+(deeply|in)\b': "breathe (verb) vs breath (noun)",
        r'\bcould\s+of\b': "could have (not could of)",
        r'\bwould\s+of\b': "would have (not would of)",
        r'\bshould\s+of\b': "should have (not should of)",
    }
    
    for pattern, correction in common_errors.items():
        if re.search(pattern, sentence, re.IGNORECASE):
            match = re.search(pattern, sentence, re.IGNORECASE)
            issues.append(f"Common error: '{match.group()}' - {correction}")
    
    return issues

def _check_article_usage(sentence: str) -> List[str]:
    """Check for proper article usage (a/an/the)."""
    issues = []
    
    # "A" before vowel sounds (should be "an")
    a_before_vowel = re.findall(r'\ba\s+[aeiou]\w*', sentence, re.IGNORECASE)
    for match in a_before_vowel:
        # Exceptions: words that start with vowel but have consonant sound
        exceptions = ['user', 'university', 'unique', 'unit', 'uniform', 'union', 'universal']
        word = match.split()[1].lower()
        if word not in exceptions:
            issues.append(f"Use 'an' before vowel sound: '{match}'")
    
    # "An" before consonant sounds (should be "a")
    an_before_consonant = re.findall(r'\ban\s+[bcdfgjklmnpqrstvwxyz]\w*', sentence, re.IGNORECASE)
    for match in an_before_consonant:
        # Exceptions: words that start with consonant but have vowel sound
        exceptions = ['hour', 'honest', 'honor', 'heir']
        word = match.split()[1].lower()
        if word not in exceptions:
            issues.append(f"Use 'a' before consonant sound: '{match}'")
    
    return issues

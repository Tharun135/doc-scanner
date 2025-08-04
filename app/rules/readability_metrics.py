"""
Rule for checking readability metrics and suggesting improvements.
Analyzes text complexity using various readability measures and suggests specific improvements.
"""

import re
import math
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

def check(content):
    """Check readability metrics and suggest improvements."""
    suggestions = []

    # Strip HTML tags from content
    soup = BeautifulSoup(content, "html.parser")
    text_content = soup.get_text()
    text_content = html.unescape(text_content)

    # Use RAG system if available
    if RAG_HELPER_AVAILABLE:
        rag_suggestions = check_with_rag(
            content,
            "readability_metrics",
            "Analyze text readability and complexity, suggest specific improvements for clarity and comprehension."
        )
        if rag_suggestions:
            return rag_suggestions

    # Skip very short texts
    if len(text_content.split()) < 50:
        return suggestions

    # Calculate various readability metrics
    metrics = calculate_readability_metrics(text_content)
    
    # Analyze and suggest improvements based on metrics
    suggestions.extend(analyze_sentence_complexity(text_content, metrics))
    suggestions.extend(analyze_vocabulary_complexity(text_content, metrics))
    suggestions.extend(analyze_paragraph_structure(text_content))
    suggestions.extend(analyze_transition_usage(text_content))

    return suggestions if suggestions else []

def calculate_readability_metrics(text):
    """Calculate various readability metrics."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    words = text.split()
    syllables = sum(count_syllables(word) for word in words)
    
    # Basic metrics
    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = syllables
    
    if total_sentences == 0 or total_words == 0:
        return {}
    
    avg_sentence_length = total_words / total_sentences
    avg_syllables_per_word = total_syllables / total_words
    
    # Flesch Reading Ease (higher = easier)
    flesch_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
    
    # Flesch-Kincaid Grade Level
    flesch_grade = (0.39 * avg_sentence_length) + (11.8 * avg_syllables_per_word) - 15.59
    
    # Complex words (3+ syllables)
    complex_words = sum(1 for word in words if count_syllables(word) >= 3)
    complex_word_ratio = complex_words / total_words if total_words > 0 else 0
    
    # Gunning Fog Index
    fog_index = 0.4 * (avg_sentence_length + 100 * complex_word_ratio)
    
    return {
        'total_words': total_words,
        'total_sentences': total_sentences,
        'avg_sentence_length': avg_sentence_length,
        'avg_syllables_per_word': avg_syllables_per_word,
        'flesch_ease': flesch_ease,
        'flesch_grade': flesch_grade,
        'complex_word_ratio': complex_word_ratio,
        'fog_index': fog_index,
        'complex_words': complex_words
    }

def count_syllables(word):
    """Estimate syllable count for a word."""
    word = word.lower().strip('.,!?;:"')
    if not word:
        return 0
    
    # Remove common endings that don't add syllables
    word = re.sub(r'(es|ed|e)$', '', word)
    
    # Count vowel groups
    vowel_groups = re.findall(r'[aeiouy]+', word)
    syllable_count = len(vowel_groups)
    
    # Minimum of 1 syllable per word
    return max(1, syllable_count)

def analyze_sentence_complexity(text, metrics):
    """Analyze sentence complexity and suggest improvements."""
    suggestions = []
    
    avg_length = metrics.get('avg_sentence_length', 0)
    flesch_ease = metrics.get('flesch_ease', 0)
    flesch_grade = metrics.get('flesch_grade', 0)
    
    # Sentence length analysis
    if avg_length > 25:
        suggestions.append(f"Average sentence length is {avg_length:.1f} words. Consider breaking long sentences into shorter ones (aim for 15-20 words).")
    elif avg_length > 20:
        suggestions.append(f"Average sentence length is {avg_length:.1f} words. Some sentences might benefit from being shorter for better readability.")
    
    # Flesch Reading Ease analysis
    if flesch_ease < 30:
        suggestions.append("Text is very difficult to read (college graduate level). Consider simplifying sentence structure and vocabulary.")
    elif flesch_ease < 50:
        suggestions.append("Text is difficult to read (college level). Consider using shorter sentences and simpler words where possible.")
    elif flesch_ease < 60:
        suggestions.append("Text is fairly difficult to read (10th-12th grade level). Minor simplifications could improve accessibility.")
    
    # Grade level analysis
    if flesch_grade > 16:
        suggestions.append(f"Text requires graduate-level reading skills (grade {flesch_grade:.1f}). Consider simplifying for broader accessibility.")
    elif flesch_grade > 12:
        suggestions.append(f"Text requires college-level reading skills (grade {flesch_grade:.1f}). Consider whether this is appropriate for your audience.")
    
    return suggestions

def analyze_vocabulary_complexity(text, metrics):
    """Analyze vocabulary complexity."""
    suggestions = []
    
    complex_ratio = metrics.get('complex_word_ratio', 0)
    fog_index = metrics.get('fog_index', 0)
    
    # Complex word analysis
    if complex_ratio > 0.15:
        suggestions.append(f"{complex_ratio*100:.1f}% of words are complex (3+ syllables). Consider using simpler alternatives where possible.")
    
    # Fog Index analysis
    if fog_index > 17:
        suggestions.append("Text has very high complexity (Fog Index > 17). Break down complex concepts and use shorter words.")
    elif fog_index > 13:
        suggestions.append("Text has high complexity (Fog Index > 13). Consider simplifying some vocabulary and sentence structures.")
    
    # Find specific complex words that could be simplified
    words = text.split()
    complex_words_found = []
    
    common_complex_alternatives = {
        'utilize': 'use',
        'facilitate': 'help',
        'demonstrate': 'show',
        'initialize': 'start',
        'terminate': 'end',
        'approximately': 'about',
        'sufficient': 'enough',
        'additional': 'more',
        'implement': 'carry out',
        'methodology': 'method',
        'functionality': 'function',
        'subsequently': 'then',
        'nevertheless': 'however',
        'approximately': 'about',
        'ということ': 'thing'  # Just in case there are any Unicode issues
    }
    
    for word in words:
        clean_word = word.lower().strip('.,!?;:"')
        if clean_word in common_complex_alternatives:
            complex_words_found.append((word, common_complex_alternatives[clean_word]))
    
    if complex_words_found:
        word_pairs = [f"'{original}' → '{simple}'" for original, simple in complex_words_found[:3]]  # Limit to first 3
        suggestions.append(f"Consider simpler alternatives: {', '.join(word_pairs)}")
    
    return suggestions

def analyze_paragraph_structure(text):
    """Analyze paragraph structure and length."""
    suggestions = []
    
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if len(paragraphs) < 2:
        return suggestions
    
    # Analyze paragraph lengths
    paragraph_lengths = [len(p.split()) for p in paragraphs]
    avg_paragraph_length = sum(paragraph_lengths) / len(paragraph_lengths)
    
    if avg_paragraph_length > 150:
        suggestions.append(f"Average paragraph length is {avg_paragraph_length:.0f} words. Consider breaking long paragraphs for better readability (aim for 50-100 words).")
    
    # Check for very long paragraphs
    long_paragraphs = [i+1 for i, length in enumerate(paragraph_lengths) if length > 200]
    if long_paragraphs:
        if len(long_paragraphs) == 1:
            suggestions.append(f"Paragraph {long_paragraphs[0]} is very long ({paragraph_lengths[long_paragraphs[0]-1]} words). Consider breaking it into smaller chunks.")
        else:
            suggestions.append(f"Multiple paragraphs are very long (paragraphs {', '.join(map(str, long_paragraphs))}). Consider breaking them for better readability.")
    
    # Check for very short paragraphs (might indicate poor organization)
    short_paragraphs = [i+1 for i, length in enumerate(paragraph_lengths) if length < 20 and length > 5]
    if len(short_paragraphs) > len(paragraphs) * 0.3:
        suggestions.append("Many short paragraphs detected. Consider combining related ideas for better flow.")
    
    return suggestions

def analyze_transition_usage(text):
    """Analyze use of transitions and connecting words."""
    suggestions = []
    
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) < 5:
        return suggestions
    
    # Common transition words and phrases
    transitions = [
        'however', 'therefore', 'furthermore', 'moreover', 'nevertheless',
        'consequently', 'additionally', 'meanwhile', 'subsequently', 'finally',
        'first', 'second', 'third', 'next', 'then', 'also', 'furthermore',
        'in addition', 'on the other hand', 'for example', 'for instance',
        'in contrast', 'similarly', 'likewise', 'in conclusion'
    ]
    
    sentences_with_transitions = 0
    
    for sentence in sentences:
        sentence_lower = sentence.lower()
        if any(transition in sentence_lower for transition in transitions):
            sentences_with_transitions += 1
    
    transition_ratio = sentences_with_transitions / len(sentences)
    
    if transition_ratio < 0.1:
        suggestions.append("Few transition words detected. Adding transitions between ideas can improve flow and readability.")
    elif transition_ratio > 0.4:
        suggestions.append("High use of transition words. Ensure they add value and don't make text feel over-connected.")
    
    return suggestions

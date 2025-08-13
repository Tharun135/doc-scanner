"""
Lightning-fast AI system for document improvement suggestions.
No network calls, no complex processing - just instant pattern-based responses.
"""

import re
import time
from typing import Dict, Any


class LightningAISuggestionEngine:
    """Ultra-fast AI engine using only pattern-based suggestions."""
    
    def __init__(self):
        self.is_initialized = True
        print("⚡ Lightning AI initialized - instant responses enabled")
    
    def generate_contextual_suggestion(self, feedback_text: str, sentence_context: str) -> Dict[str, Any]:
        """Generate instant suggestions using pattern-based rules."""
        start_time = time.time()
        
        suggestion = self._get_instant_suggestion(feedback_text, sentence_context)
        response_time = time.time() - start_time
        
        return {
            'suggestion': suggestion,
            'method': 'lightning_fast',
            'response_time': response_time,
            'confidence': 0.9
        }
    
    def _get_instant_suggestion(self, feedback_text: str, sentence_context: str) -> str:
        """Get instant suggestion based on feedback type."""
        
        if "passive voice" in feedback_text.lower():
            return self._fix_passive_voice(sentence_context)
        
        elif "long sentence" in feedback_text.lower() or "sentence too long" in feedback_text.lower():
            return self._split_long_sentence(sentence_context)
        
        elif "modal verb" in feedback_text.lower():
            return self._remove_modal_verbs(sentence_context)
        
        elif "weak word" in feedback_text.lower():
            return self._strengthen_words(sentence_context)
        
        else:
            return self._general_improvement(sentence_context)
    
    def _fix_passive_voice(self, sentence: str) -> str:
        """Convert passive voice to active voice instantly."""
        original = sentence.strip()
        
        # Simple pattern matching for common passive voice constructions
        if 'was written by' in original.lower():
            # "The document was written by the team" -> "The team wrote the document"
            match = re.search(r'(.+?)\s+was\s+written\s+by\s+(.+)', original, re.IGNORECASE)
            if match:
                what = match.group(1).strip().rstrip('.')
                who = match.group(2).strip().rstrip('.')
                active = who + " wrote " + what.lower()
                # Capitalize first letter and add period
                active = active[0].upper() + active[1:] + "."
            else:
                active = original.replace(' was written by ', ' - written by ')
        
        elif 'was created by' in original.lower():
            match = re.search(r'(.+?)\s+was\s+created\s+by\s+(.+)', original, re.IGNORECASE)
            if match:
                what = match.group(1).strip().rstrip('.')
                who = match.group(2).strip().rstrip('.')
                active = who + " created " + what.lower()
                active = active[0].upper() + active[1:] + "."
            else:
                active = original.replace(' was created by ', ' - created by ')
        
        elif 'was reviewed by' in original.lower():
            match = re.search(r'(.+?)\s+was\s+reviewed\s+by\s+(.+)', original, re.IGNORECASE)
            if match:
                what = match.group(1).strip().rstrip('.')
                who = match.group(2).strip().rstrip('.')
                active = who + " reviewed " + what.lower()
                active = active[0].upper() + active[1:] + "."
            else:
                active = original.replace(' was reviewed by ', ' - reviewed by ')
        
        else:
            # Generic approach: just suggest removing passive construction
            active = original.replace(' was ', ' is ').replace(' were ', ' are ')
        
        # Create alternative options
        option2 = original.replace(' was ', ' is ').replace(' were ', ' are ')
        option3 = original.replace(' by the ', ' by a ').replace(' by ', ' via ')
        
        result = "OPTION 1: " + active + "\n"
        result += "OPTION 2: " + option2 + "\n"
        result += "OPTION 3: " + option3 + "\n"
        result += "WHY: Converts passive voice to active voice for clarity."
        
        return result
    
    def _split_long_sentence(self, sentence: str) -> str:
        """Split long sentences into shorter ones."""
        # Find natural break points
        break_points = [', and ', ', but ', ', however ', ', therefore ', ', because ']
        
        for break_point in break_points:
            if break_point in sentence.lower():
                parts = sentence.split(break_point, 1)
                if len(parts) == 2:
                    first = parts[0].strip() + '.'
                    second = parts[1].strip()
                    if not second[0].isupper():
                        second = second[0].upper() + second[1:]
                    
                    return ("OPTION 1: " + first + " " + second + "\n" +
                            "OPTION 2: " + parts[0].strip() + ". Then, " + parts[1].strip().lower() + "\n" +
                            "OPTION 3: " + parts[0].strip() + ". Also, " + parts[1].strip().lower() + "\n" +
                            "WHY: Breaks long sentence into clearer segments.")
        
        # Fallback: split at comma
        if ', ' in sentence:
            parts = sentence.split(', ', 1)
            first = parts[0].strip() + '.'
            second = parts[1].strip()
            if not second[0].isupper():
                second = second[0].upper() + second[1:]
            
            return ("OPTION 1: " + first + " " + second + "\n" +
                    "OPTION 2: " + first + " Additionally, " + second.lower() + "\n" +
                    "OPTION 3: " + first + " Furthermore, " + second.lower() + "\n" +
                    "WHY: Breaks long sentence for better readability.")
        
        # Last resort: split in middle
        mid = len(sentence) // 2
        space_pos = sentence.find(' ', mid)
        if space_pos > 0:
            first = sentence[:space_pos].strip() + '.'
            second = sentence[space_pos:].strip()
            if not second[0].isupper():
                second = second[0].upper() + second[1:]
            
            return ("OPTION 1: " + first + " " + second + "\n" +
                    "OPTION 2: " + first + " Then " + second.lower() + "\n" +
                    "OPTION 3: " + first + " Next, " + second.lower() + "\n" +
                    "WHY: Splits sentence for improved clarity.")
        
        return ("OPTION 1: " + sentence + " (Consider rephrasing)\n" +
                "OPTION 2: " + sentence.replace('.', ' - this needs revision.') + "\n" +
                "OPTION 3: Break this sentence into smaller parts.\n" +
                "WHY: Long sentences can be difficult to follow.")
    
    def _remove_modal_verbs(self, sentence: str) -> str:
        """Remove modal verbs for more direct communication."""
        modal_replacements = {
            'should be': 'is',
            'could be': 'is',
            'would be': 'is',
            'might be': 'is',
            'may be': 'is',
            'should have': 'has',
            'could have': 'has',
            'would have': 'has',
            'should': '',
            'could': 'can',
            'would': 'will',
            'might': 'may',
        }
        
        direct_version = sentence
        for modal, replacement in modal_replacements.items():
            direct_version = re.sub(r'\b' + modal + r'\b', replacement, direct_version, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        direct_version = re.sub(r'\s+', ' ', direct_version).strip()
        
        return ("OPTION 1: " + direct_version + "\n" +
                "OPTION 2: " + sentence.replace('should', 'must').replace('could', 'can') + "\n" +
                "OPTION 3: " + sentence.replace('would', 'will').replace('might', 'will') + "\n" +
                "WHY: Removes unnecessary modal verbs for direct communication.")
    
    def _strengthen_words(self, sentence: str) -> str:
        """Replace weak words with stronger alternatives."""
        weak_to_strong = {
            'very good': 'excellent',
            'pretty good': 'good',
            'quite nice': 'nice',
            'rather interesting': 'interesting',
            'somewhat important': 'important',
            'fairly simple': 'simple',
            'really great': 'outstanding',
            'very bad': 'terrible',
            'pretty bad': 'poor',
            'quite difficult': 'challenging',
        }
        
        stronger = sentence
        for weak, strong in weak_to_strong.items():
            stronger = re.sub(r'\b' + weak + r'\b', strong, stronger, flags=re.IGNORECASE)
        
        return ("OPTION 1: " + stronger + "\n" +
                "OPTION 2: " + sentence.replace('very ', '').replace('quite ', '').replace('rather ', '') + "\n" +
                "OPTION 3: " + sentence.replace('pretty ', '').replace('fairly ', '') + "\n" +
                "WHY: Replaces weak modifiers with stronger language.")
    
    def _general_improvement(self, sentence: str) -> str:
        """General improvements for any sentence."""
        # Remove filler words
        improved = sentence
        fillers = ['actually', 'basically', 'literally', 'obviously', 'clearly', 'essentially']
        for filler in fillers:
            improved = re.sub(r'\b' + filler + r'\s+', '', improved, flags=re.IGNORECASE)
        
        # Clean up
        improved = re.sub(r'\s+', ' ', improved).strip()
        
        return ("OPTION 1: " + improved + "\n" +
                "OPTION 2: " + sentence.replace(', ', ' - ').replace(' and ', ' plus ') + "\n" +
                "OPTION 3: " + sentence.replace(' that ', ' which ').replace(' who ', ' that ') + "\n" +
                "WHY: Improves clarity and directness.")

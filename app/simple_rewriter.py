#!/usr/bin/env python3
"""
Simple sentence rewriter that provides actual rewrites for common writing issues.
This is a fallback system when the full RAG/LLM system isn't working properly.
"""

import re
import logging

logger = logging.getLogger(__name__)

class SimpleSentenceRewriter:
    """Provides actual sentence rewrites for common writing issues."""
    
    def __init__(self):
        self.passive_patterns = [
            # Pattern, replacement, description
            (r'(.+) was (\w+ed) by (.+)', r'\3 \2 \1', 'Convert passive to active voice'),
            (r'(.+) were (\w+ed) by (.+)', r'\3 \2 \1', 'Convert passive to active voice'),
            (r'(.+) is (\w+ed) by (.+)', r'\3 \2s \1', 'Convert passive to active voice'),
            (r'(.+) are (\w+ed) by (.+)', r'\3 \2 \1', 'Convert passive to active voice'),
            (r'(.+) will be (\w+ed) by (.+)', r'\3 will \2 \1', 'Convert passive to active voice'),
            (r'(.+) has been (\w+ed) by (.+)', r'\3 has \2 \1', 'Convert passive to active voice'),
            (r'(.+) have been (\w+ed) by (.+)', r'\3 have \2 \1', 'Convert passive to active voice'),
        ]
        
        self.modal_replacements = [
            (r'\bcan be used to\b', 'enables', 'Replace modal verb with direct action'),
            (r'\bwill be able to\b', 'will', 'Simplify modal construction'),
            (r'\bmay be\b', 'might be', 'Use simpler modal'),
            (r'\bshould be able to\b', 'should', 'Simplify modal construction'),
            (r'\bmight be able to\b', 'might', 'Simplify modal construction'),
        ]
        
        self.weak_word_patterns = [
            (r'\bvery (\w+)', r'\1', 'Remove weak intensifier'),
            (r'\bquite (\w+)', r'\1', 'Remove weak intensifier'), 
            (r'\brather (\w+)', r'\1', 'Remove weak intensifier'),
            (r'\breally (\w+)', r'\1', 'Remove weak intensifier'),
            (r'\bactually (\w+)', r'\1', 'Remove weak qualifier'),
            (r'\bjust (\w+)', r'\1', 'Remove weak qualifier'),
        ]
    
    def rewrite_sentence(self, sentence: str, issue_type: str = "general") -> str:
        """
        Generate an actual rewritten sentence based on the issue type.
        
        Args:
            sentence: The original sentence
            issue_type: Type of issue (passive_voice, long_sentence, modal_verb, etc.)
            
        Returns:
            Rewritten sentence
        """
        original = sentence.strip()
        rewritten = original
        
        try:
            if issue_type == "passive_voice":
                rewritten = self._fix_passive_voice(rewritten)
            elif issue_type == "long_sentence": 
                rewritten = self._shorten_sentence(rewritten)
            elif issue_type == "modal_verb":
                rewritten = self._fix_modal_verbs(rewritten)
            elif issue_type == "clarity" or issue_type == "word_choice":
                rewritten = self._improve_clarity(rewritten)
            else:
                # General improvements
                rewritten = self._apply_general_improvements(rewritten)
            
            # If no changes were made, force an improvement
            if rewritten.strip() == original.strip():
                rewritten = self._force_improvement(original, issue_type)
                
            logger.info(f"Rewrote sentence: {issue_type} -> {len(rewritten)} chars")
            return rewritten
            
        except Exception as e:
            logger.error(f"Error rewriting sentence: {e}")
            return self._force_improvement(original, issue_type)
    
    def _fix_passive_voice(self, sentence: str) -> str:
        """Convert passive voice to active voice."""
        for pattern, replacement, desc in self.passive_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                new_sentence = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
                # Clean up the result
                new_sentence = re.sub(r'\s+', ' ', new_sentence).strip()
                new_sentence = new_sentence[0].upper() + new_sentence[1:] if new_sentence else sentence
                if new_sentence != sentence:
                    return new_sentence
        
        # Fallback: look for common passive constructions
        if ' was ' in sentence or ' were ' in sentence:
            # Simple fallback: try to restructure
            if sentence.startswith('The '):
                return sentence.replace('The ', 'This ', 1)
            elif sentence.startswith('It was '):
                return sentence.replace('It was ', 'This is ')
        
        return sentence
    
    def _shorten_sentence(self, sentence: str) -> str:
        """Break long sentences into shorter ones."""
        words = sentence.split()
        
        if len(words) <= 20:
            return sentence
            
        # Look for natural break points
        conjunctions = [' and ', ' but ', ' however ', ' therefore ', ' meanwhile ', ' furthermore ', ' moreover ']
        
        for conj in conjunctions:
            if conj in sentence:
                parts = sentence.split(conj, 1)
                if len(parts) == 2 and len(parts[0].strip()) > 5 and len(parts[1].strip()) > 5:
                    first_part = parts[0].strip()
                    second_part = parts[1].strip()
                    
                    # Ensure both parts are complete sentences
                    if not first_part.endswith('.'):
                        first_part += '.'
                    if not second_part[0].isupper():
                        second_part = second_part[0].upper() + second_part[1:]
                    if not second_part.endswith('.'):
                        second_part += '.'
                        
                    return f"{first_part} {second_part}"
        
        # Fallback: split at comma if sentence is very long
        if len(words) > 25 and ', ' in sentence:
            comma_pos = sentence.find(', ')
            if comma_pos > 20:  # Ensure reasonable first part
                first_part = sentence[:comma_pos].strip()
                second_part = sentence[comma_pos+2:].strip()
                
                if not first_part.endswith('.'):
                    first_part += '.'
                if not second_part[0].isupper():
                    second_part = second_part[0].upper() + second_part[1:]
                    
                return f"{first_part} {second_part}"
        
        return sentence
    
    def _fix_modal_verbs(self, sentence: str) -> str:
        """Replace modal verb constructions with more direct language."""
        result = sentence
        
        for pattern, replacement, desc in self.modal_replacements:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def _improve_clarity(self, sentence: str) -> str:
        """Remove weak words and improve clarity."""
        result = sentence
        
        for pattern, replacement, desc in self.weak_word_patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        # Clean up multiple spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    def _apply_general_improvements(self, sentence: str) -> str:
        """Apply general improvements to any sentence."""
        result = sentence
        
        # Remove weak words
        result = self._improve_clarity(result)
        
        # Fix modal verbs
        result = self._fix_modal_verbs(result)
        
        # Try passive voice fixes
        passive_result = self._fix_passive_voice(result)
        if passive_result != result:
            result = passive_result
        
        return result
    
    def _force_improvement(self, sentence: str, issue_type: str) -> str:
        """Force an improvement when automatic fixes don't work."""
        
        # Make specific improvements based on issue type
        if issue_type == "passive_voice":
            if sentence.startswith("It is "):
                return sentence.replace("It is ", "This is ")
            elif sentence.startswith("There are "):
                return sentence.replace("There are ", "Multiple ")
            elif sentence.startswith("There is "):
                return sentence.replace("There is ", "A ")
            elif " is " in sentence and " by " in sentence:
                return sentence.replace(" is ", " remains ")
        
        elif issue_type == "long_sentence":
            words = sentence.split()
            if len(words) > 15:
                # Take first meaningful chunk
                mid_point = len(words) // 2
                return " ".join(words[:mid_point]) + "."
        
        elif issue_type == "modal_verb":
            if "can be" in sentence:
                return sentence.replace("can be", "is")
            elif "will be" in sentence:
                return sentence.replace("will be", "becomes")
        
        # Generic improvements
        if sentence.startswith("The "):
            return sentence.replace("The ", "This ", 1)
        elif sentence.startswith("There "):
            return sentence.replace("There ", "Here ", 1)
        elif " very " in sentence:
            return sentence.replace(" very ", " ")
        
        # Last resort: add improvement note
        return f"Consider revising: {sentence}"

# Global instance for easy import
sentence_rewriter = SimpleSentenceRewriter()

def get_simple_rewrite(sentence: str, issue_type: str = "general") -> str:
    """
    Get a rewritten version of the sentence.
    
    Args:
        sentence: Original sentence
        issue_type: Type of writing issue
        
    Returns:
        Rewritten sentence
    """
    return sentence_rewriter.rewrite_sentence(sentence, issue_type)

def get_issue_solution(sentence: str, issue_type: str = "general") -> str:
    """
    Get a solution that specifically addresses the identified writing issue.
    
    Args:
        sentence: Original sentence with the issue
        issue_type: Specific type of writing issue identified
        
    Returns:
        Corrected sentence that solves the specific issue
    """
    original = sentence.strip()
    
    # Issue-specific solutions
    if issue_type == "passive voice":
        solution = sentence_rewriter._fix_passive_voice(original)
        if solution != original:
            return solution
        # Force active voice conversion
        if " was " in original and " by " in original:
            # Try basic pattern: "X was done by Y" -> "Y did X"
            parts = original.split(" was ")
            if len(parts) == 2 and " by " in parts[1]:
                after_by = parts[1].split(" by ", 1)
                if len(after_by) == 2:
                    action = after_by[0].strip()
                    doer = after_by[1].strip().rstrip('.')
                    subject = parts[0].replace("The ", "the ").replace("This ", "this ")
                    return f"{doer.capitalize()} {action} {subject}."
        
    elif issue_type == "overly long sentence":
        solution = sentence_rewriter._shorten_sentence(original)
        if solution != original:
            return solution
        # Force sentence splitting
        words = original.split()
        if len(words) > 20:
            mid = len(words) // 2
            # Find a good break point near the middle
            for i in range(mid-3, mid+4):
                if i < len(words) and words[i] in ["and", "but", "however", "therefore"]:
                    first_part = " ".join(words[:i]).strip()
                    second_part = " ".join(words[i+1:]).strip()
                    if first_part and second_part:
                        return f"{first_part}. {second_part.capitalize()}"
            # Simple split in half
            first_half = " ".join(words[:mid]).rstrip(',').strip() + "."
            second_half = " ".join(words[mid:]).capitalize()
            return f"{first_half} {second_half}"
    
    elif issue_type == "weak modal verb construction":
        solution = sentence_rewriter._fix_modal_verbs(original)
        if solution != original:
            return solution
        # Force modal verb fixes
        if "can be used to" in original:
            return original.replace("can be used to", "enables")
        elif "will be able to" in original:
            return original.replace("will be able to", "will")
        elif "can be" in original:
            return original.replace("can be", "is")
    
    elif issue_type == "weak word usage":
        solution = sentence_rewriter._improve_clarity(original)
        if solution != original:
            return solution
        # Force weak word removal
        weak_words = ["very ", "quite ", "rather ", "really ", "actually ", "just "]
        for weak in weak_words:
            if weak in original:
                return original.replace(weak, "")
    
    elif issue_type == "wordy construction":
        if original.startswith("There are "):
            noun_phrase = original[10:].strip()
            return noun_phrase.capitalize()
        elif original.startswith("There is "):
            noun_phrase = original[9:].strip()
            return noun_phrase.capitalize()
        elif original.startswith("It is "):
            return original.replace("It is ", "This is ")
        elif " in order to " in original:
            return original.replace(" in order to ", " to ")
    
    elif issue_type == "unclear pronoun reference":
        # Simple pronoun clarification
        if " it " in original.lower():
            return original.replace(" it ", " the system ")
        elif " they " in original.lower():
            return original.replace(" they ", " the users ")
        elif " this " in original.lower() and not original.lower().startswith("this "):
            return original.replace(" this ", " this approach ")
    
    # If no specific solution worked, fall back to general improvement
    return sentence_rewriter.rewrite_sentence(original, issue_type)

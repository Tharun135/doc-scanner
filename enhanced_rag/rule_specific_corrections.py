# enhanced_rag/rule_specific_corrections.py
"""
Rule-specific correction patterns for accurate AI suggestions.
Implements targeted correction logic for different writing issues.
"""
import re
from typing import Dict, List, Tuple, Optional

class RuleSpecificCorrector:
    """
    Provides rule-specific correction logic for different writing issues.
    Each method handles a specific type of writing problem with targeted solutions.
    """
    
    @staticmethod
    def fix_capitalization(sentence: str) -> str:
        """
        Fix capitalization issues - starts sentence with capital letter.
        
        Args:
            sentence: Input sentence that may need capitalization
            
        Returns:
            Sentence with proper capitalization
        """
        sentence = sentence.strip()
        if not sentence:
            return sentence
            
        # Capitalize the first letter
        if len(sentence) > 0:
            return sentence[0].upper() + sentence[1:]
        
        return sentence
    
    @staticmethod
    def fix_passive_voice(sentence: str) -> str:
        """
        Convert passive voice to active voice with improved logic.
        
        Args:
            sentence: Sentence containing passive voice
            
        Returns:
            Sentence converted to active voice
        """
        sentence = sentence.strip()
        
        # Pattern 1: "When X is enabled, Y is done" -> "When you enable X, the system does Y"
        when_pattern = r'When\s+(.+?)\s+(?:is|are)\s+([a-zA-Z]+ed),\s*(.+?)(?:is|are)\s+([a-zA-Z]+ed)'
        when_match = re.search(when_pattern, sentence, re.IGNORECASE)
        if when_match:
            feature = when_match.group(1)
            action = when_match.group(2)
            subject = when_match.group(3)
            second_action = when_match.group(4)
            
            active_verb1 = RuleSpecificCorrector._active_verb(action)
            active_verb2 = RuleSpecificCorrector._active_verb(second_action)
            
            return f"When you {active_verb1.replace('s', '')} {feature}, the system {active_verb2} {subject}"
        
        # Pattern 2: "X is published by Y" -> "Y publishes X"
        by_pattern = r'(.+?)\s+(?:is|was|are|were)\s+([a-zA-Z]+ed)\s+by\s+(.+)'
        by_match = re.search(by_pattern, sentence, re.IGNORECASE)
        if by_match:
            object_part = by_match.group(1).strip()
            passive_verb = by_match.group(2)
            subject = by_match.group(3).strip()
            
            # Remove period from subject if it exists
            subject = subject.rstrip('.')
            
            active_verb = RuleSpecificCorrector._active_verb(passive_verb)
            
            # Proper capitalization: capitalize first word, lowercase object
            result = f"{subject.capitalize()} {active_verb} {object_part.lower()}"
            
            # Add period at the end if original had one
            if sentence.rstrip().endswith('.'):
                result += '.'
                
            return result
        
        # Pattern 3a: Handle complex sentences like "With X, qx is published which..."
        complex_pattern = r'(With\s+.+?),\s*(.+?)\s+(?:is|are)\s+([a-zA-Z]+ed)(\s+.+)?'
        complex_match = re.search(complex_pattern, sentence, re.IGNORECASE)
        if complex_match:
            with_part = complex_match.group(1)
            subject = complex_match.group(2)
            passive_verb = complex_match.group(3)
            rest = complex_match.group(4) or ""
            
            active_verb = RuleSpecificCorrector._active_verb(passive_verb)
            return f"{with_part}, the system {active_verb} {subject}{rest}"
        
        # Pattern 4: "When [something], X is [also] published" -> "When [something], the system publishes X"
        when_simple_pattern = r'(When\s+.+?),\s*(.+?)\s+(?:is|are)\s+(?:also\s+)?([a-zA-Z]+ed)(\s+.+)?'
        when_simple_match = re.search(when_simple_pattern, sentence, re.IGNORECASE)
        if when_simple_match:
            when_clause = when_simple_match.group(1)
            subject = when_simple_match.group(2)
            passive_verb = when_simple_match.group(3)
            rest = when_simple_match.group(4) or ""
            
            active_verb = RuleSpecificCorrector._active_verb(passive_verb)
            return f"{when_clause}, the system {active_verb} {subject}{rest}"
        
        # Pattern 5: "When X is enabled, [rest]" -> "When you enable X, [rest]"
        when_passive_pattern = r'When\s+(.+?)\s+(?:is|are)\s+([a-zA-Z]+ed)(,\s*.+)?'
        when_passive_match = re.search(when_passive_pattern, sentence, re.IGNORECASE)
        if when_passive_match:
            subject = when_passive_match.group(1)
            passive_verb = when_passive_match.group(2)
            rest = when_passive_match.group(3) or ""
            
            active_verb = RuleSpecificCorrector._active_verb(passive_verb)
            # Convert to active voice with "you" as the actor
            active_verb_base = active_verb.replace('s', '') if active_verb.endswith('s') else active_verb
            return f"When you {active_verb_base} {subject}{rest}"
        
        # Pattern 6: General passive with adverbs like "also" -> "X is also published"
        adverb_pattern = r'(.+?)\s+(?:is|was|are|were)\s+(also\s+|automatically\s+|then\s+)?([a-zA-Z]+ed)(\s+.+)?'
        adverb_match = re.search(adverb_pattern, sentence, re.IGNORECASE)
        if adverb_match:
            subject = adverb_match.group(1).strip()
            adverb = adverb_match.group(2) or ""
            passive_verb = adverb_match.group(3)
            rest = adverb_match.group(4) or ""
            
            # Only apply if the subject part is reasonably clean (not too complex)
            if len(subject.split()) <= 6 and not subject.lower().startswith(('when ', 'if ', 'while ')):
                active_verb = RuleSpecificCorrector._active_verb(passive_verb)
                return f"The system {adverb}{active_verb} {subject}{rest}"
        
        # Pattern 6: Simple "X is published" -> "The system publishes X" (only for clean cases)
        simple_pattern = r'^(.+?)\s+(?:is|was|are|were)\s+([a-zA-Z]+ed)(\s+.+)?$'
        simple_match = re.search(simple_pattern, sentence, re.IGNORECASE)
        if simple_match:
            object_part = simple_match.group(1).strip()
            passive_verb = simple_match.group(2)
            rest = simple_match.group(3) or ""
            
            # Only apply if the object part is reasonably clean (not too complex)
            if len(object_part.split()) <= 4 and not object_part.startswith('With '):
                active_verb = RuleSpecificCorrector._active_verb(passive_verb)
                return f"The system {active_verb} {object_part}{rest}"
        
        return sentence
    
    @staticmethod
    def _active_verb(passive_verb: str) -> str:
        """Convert passive verb to active form"""
        # Simple verb conversion rules
        verb_map = {
            'published': 'publishes',
            'demonstrated': 'demonstrates',
            'enabled': 'enables',
            'disabled': 'disables',
            'created': 'creates',
            'updated': 'updates',
            'configured': 'configures',
            'processed': 'processes',
            'generated': 'generates',
            'managed': 'manages',
            'stored': 'stores',
            'saved': 'saves',
            'loaded': 'loads',
            'shown': 'shows',
            'displayed': 'displays',
            'installed': 'installs'
        }
        
        return verb_map.get(passive_verb.lower(), passive_verb.replace('ed', 's'))
    
    @staticmethod
    def break_long_sentence(sentence: str) -> str:
        """
        Break long sentences into shorter, clearer ones.
        
        Args:
            sentence: Long sentence to break up
            
        Returns:
            Multiple shorter sentences
        """
        sentence = sentence.strip()
        
        # Pattern 1: Break at colon that introduces a list
        colon_pattern = r'(.+?):\s*(.+)'
        colon_match = re.search(colon_pattern, sentence)
        if colon_match and len(sentence) > 80:
            main_part = colon_match.group(1).strip()
            list_part = colon_match.group(2).strip()
            return f"{main_part}. This includes: {list_part}"
        
        # Pattern 2: Break at "which" clauses
        which_pattern = r'(.+?),\s*which\s+(.+)'
        which_match = re.search(which_pattern, sentence)
        if which_match and len(sentence) > 60:
            main_part = which_match.group(1).strip()
            which_part = which_match.group(2).strip()
            return f"{main_part}. This {which_part}"
        
        # Pattern 3: Break at coordinating conjunctions in long sentences
        coord_pattern = r'(.+?),\s+(and|or|but)\s+(.+)'
        coord_match = re.search(coord_pattern, sentence)
        if coord_match and len(sentence) > 70:
            first_part = coord_match.group(1).strip()
            conjunction = coord_match.group(2)
            second_part = coord_match.group(3).strip()
            
            if conjunction.lower() == "and":
                return f"{first_part}. Additionally, {second_part}"
            elif conjunction.lower() == "or":
                return f"{first_part}. Alternatively, {second_part}"
            else:  # but
                return f"{first_part}. However, {second_part}"
        
        # Pattern 4: Break at natural pauses (commas) if very long
        if len(sentence) > 100 and ',' in sentence:
            comma_parts = sentence.split(',', 1)
            if len(comma_parts) == 2 and len(comma_parts[0]) > 30:
                first = comma_parts[0].strip()
                rest = comma_parts[1].strip()
                return f"{first}. {rest.capitalize()}"
        
        return sentence
    
    @staticmethod
    def remove_adverbs(sentence: str) -> str:
        """
        Remove unnecessary adverbs from sentences.
        
        Args:
            sentence: Sentence containing adverbs
            
        Returns:
            Sentence with adverbs removed
        """
        # Common unnecessary adverbs
        adverbs_to_remove = [
            r'\breally\b', r'\bvery\b', r'\bquite\b', r'\breadily\b',
            r'\beasily\b', r'\bsimply\b', r'\bbasically\b', r'\bactually\b',
            r'\bobviously\b', r'\bclearly\b', r'\bjust\b', r'\bpretty\b'
        ]
        
        result = sentence
        for adverb_pattern in adverbs_to_remove:
            result = re.sub(adverb_pattern, '', result, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result
    
    @staticmethod
    def fix_click_on(sentence: str) -> str:
        """
        Replace 'click on' with more direct language.
        
        Args:
            sentence: Sentence containing 'click on'
            
        Returns:
            Sentence with improved button instruction language
        """
        # Replace "click on" with "click" or "select"
        patterns = [
            (r'\bclick on\b', 'click'),
            (r'\bClick on\b', 'Click'),
            (r'\bCLICK ON\b', 'CLICK')
        ]
        
        result = sentence
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        
        return result
    
    @staticmethod
    def fix_modal_verbs(sentence: str) -> str:
        """
        Replace modal verbs with direct imperative language.
        
        Args:
            sentence: Sentence containing modal verbs
            
        Returns:
            Sentence with direct imperative language
        """
        # Replace modal constructions with direct imperatives
        patterns = [
            (r'\bYou should\b', 'You must'),
            (r'\byou should\b', 'you must'),
            (r'\bYou can\b', ''),
            (r'\byou can\b', ''),
            (r'\bYou may\b', 'You can'),
            (r'\byou may\b', 'you can'),
        ]
        
        result = sentence
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result).strip()
        
        # Clean up extra spaces
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result


def get_rule_specific_correction(sentence: str, rule_id: str, feedback_text: str = "") -> str:
    """
    Apply rule-specific correction based on the detected issue type.
    
    Args:
        sentence: Original sentence with the issue
        rule_id: Type of rule violation detected
        feedback_text: The feedback text describing the issue
        
    Returns:
        Corrected sentence using rule-specific logic
    """
    corrector = RuleSpecificCorrector()
    
    # First check feedback text for specific issues
    if feedback_text:
        feedback_lower = feedback_text.lower()
        
        if "capital letter" in feedback_lower or "sentence case" in feedback_lower:
            return corrector.fix_capitalization(sentence)
        
        elif "passive voice" in feedback_lower:
            return corrector.fix_passive_voice(sentence)
        
        elif "long sentence" in feedback_lower or "shorter sentences" in feedback_lower:
            return corrector.break_long_sentence(sentence)
        
        elif "adverb" in feedback_lower:
            return corrector.remove_adverbs(sentence)
        
        elif "click on" in feedback_lower:
            return corrector.fix_click_on(sentence)
        
        elif "modal" in feedback_lower:
            return corrector.fix_modal_verbs(sentence)
    
    # Fallback to rule_id checking
    if rule_id == "capitalization" or "capital letter" in rule_id.lower():
        return corrector.fix_capitalization(sentence)
    
    elif rule_id == "passive-voice" or "passive voice" in rule_id.lower():
        return corrector.fix_passive_voice(sentence)
    
    elif rule_id == "long-sentence" or "long sentence" in rule_id.lower():
        return corrector.break_long_sentence(sentence)
    
    elif rule_id == "adverb-usage" or "adverb" in rule_id.lower():
        return corrector.remove_adverbs(sentence)
    
    elif rule_id == "click-on" or "click on" in rule_id.lower():
        return corrector.fix_click_on(sentence)
    
    elif rule_id == "modal-verbs" or "modal" in rule_id.lower():
        return corrector.fix_modal_verbs(sentence)
    
    else:
        # Generic improvement
        return sentence.strip()


# Enhanced prompt templates for rule-specific issues
class EnhancedRulePrompts:
    """Enhanced prompts that are specific to each rule type"""
    
    @staticmethod
    def get_rule_specific_prompt(sentence: str, rule_id: str, context_chunks: List[str] = None) -> str:
        """
        Get a rule-specific prompt for more accurate AI responses.
        
        Args:
            sentence: The problematic sentence
            rule_id: The specific rule that was violated
            context_chunks: Retrieved context from RAG system
            
        Returns:
            Tailored prompt for the specific rule type
        """
        context_text = ""
        if context_chunks:
            context_text = f"\n\nRelevant guidance:\n{context_chunks[0][:200]}..."
        
        prompts = {
            "capitalization": f"""Fix the capitalization in this sentence:
"{sentence}"

Rule: Sentences must start with a capital letter.
Task: Capitalize the first letter of the sentence.{context_text}

Corrected sentence:""",

            "passive-voice": f"""Convert this passive voice sentence to active voice:
"{sentence}"

Rule: Use active voice instead of passive voice.
Task: Identify who/what performs the action and make them the subject.{context_text}

Active voice correction:""",

            "long-sentence": f"""Break this long sentence into shorter, clearer sentences:
"{sentence}"

Rule: Use shorter sentences for better readability.
Task: Split into 2-3 shorter sentences while preserving meaning.{context_text}

Shorter sentences:""",

            "adverb-usage": f"""Remove unnecessary adverbs from this sentence:
"{sentence}"

Rule: Avoid unnecessary adverbs that don't add meaning.
Task: Remove words like "easily", "simply", "really", "very".{context_text}

Sentence without adverbs:""",

            "click-on": f"""Improve this user interface instruction:
"{sentence}"

Rule: Use direct language for button instructions.
Task: Replace "click on" with "click" or "select".{context_text}

Improved instruction:""",
        }
        
        # Get specific prompt or generic fallback
        return prompts.get(rule_id, f"""Improve this sentence according to the {rule_id} rule:
"{sentence}"{context_text}

Improved sentence:""")


if __name__ == "__main__":
    # Test the rule-specific corrections with your examples
    print("Testing Rule-Specific Corrections")
    print("=" * 50)
    
    test_cases = [
        {
            "sentence": "When the \"Bulk Publish\" is enabled, all tags data is published under single group with topic name as:",
            "rule": "passive-voice",
            "description": "Passive voice issue"
        },
        {
            "sentence": "it is in ISO 8601 Zulu format.",
            "rule": "capitalization", 
            "description": "Capitalization issue"
        },
        {
            "sentence": "With \"SLMP Connector V2.0\", with qc, qx is published which holds all the bits data: quality code, sub status, extended sub status, flags, and limit.",
            "rule": "long-sentence",
            "description": "Long sentence issue"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Original: \"{test['sentence']}\"")
        
        # Apply rule-specific correction
        corrected = get_rule_specific_correction(test['sentence'], test['rule'])
        print(f"Corrected: \"{corrected}\"")
        
        # Show the specialized prompt that would be used
        prompt = EnhancedRulePrompts.get_rule_specific_prompt(test['sentence'], test['rule'])
        print(f"Prompt used: {prompt[:100]}...")

"""
Enhanced Passive Voice Detection and Transformation
================================================

This module provides improved passive voice detection and transformation
that correctly handles various passive voice patterns including:
- Simple passive: "The issue was resolved"
- Passive with agent: "The issue was resolved by the developer"
- Complex passive constructions: "The languages that are not needed"
"""

import re
import spacy
from typing import Tuple, Optional

class EnhancedPassiveVoiceProcessor:
    """Advanced passive voice detection and transformation"""
    
    def __init__(self):
        """Initialize the processor"""
        try:
            # Try to load spaCy model for better analysis
            self.nlp = spacy.load("en_core_web_sm")
            self.use_nlp = True
        except OSError:
            print("spaCy model not available, using regex patterns")
            self.nlp = None
            self.use_nlp = False
        
        # Enhanced passive voice patterns
        self.passive_patterns = [
            # Classic passive with 'by' agent
            {
                "pattern": r"(.+?)\s+(was|were|is|are|been|be)\s+(\w+ed|chosen|taken|given|made|done|seen|found)\s+by\s+(.+)",
                "transform": self.transform_classic_passive_with_agent,
                "description": "Classic passive with agent"
            },
            # Passive without explicit agent
            {
                "pattern": r"(.+?)\s+(was|were|is|are|been|be)\s+(\w+ed|chosen|taken|given|made|done|seen|found)(?!\s+by)",
                "transform": self.transform_passive_without_agent,
                "description": "Passive without agent"
            },
            # Relative clause passive (like "languages that are not needed")
            {
                "pattern": r"(.+?)\s+that\s+(are|were|is|was)\s+(not\s+)?(\w+ed|needed|required|used|selected)",
                "transform": self.transform_relative_clause_passive,
                "description": "Relative clause passive"
            },
            # Get + past participle
            {
                "pattern": r"(.+?)\s+get[s]?\s+(\w+ed|done|made|taken)",
                "transform": self.transform_get_passive,
                "description": "Get passive"
            }
        ]
    
    def is_passive_voice(self, sentence: str) -> Tuple[bool, str]:
        """
        Detect if sentence contains passive voice
        
        Returns:
            (is_passive, pattern_description)
        """
        
        if self.use_nlp:
            return self.detect_with_spacy(sentence)
        else:
            return self.detect_with_regex(sentence)
    
    def detect_with_spacy(self, sentence: str) -> Tuple[bool, str]:
        """Use spaCy for more accurate passive voice detection"""
        doc = self.nlp(sentence)
        
        for token in doc:
            # Look for passive voice indicators
            if (token.dep_ == "nsubjpass" or  # passive nominal subject
                (token.pos_ == "VERB" and "Pass" in token.morph.get("Voice", []))):
                return True, "SpaCy detected passive voice"
        
        return False, "No passive voice detected"
    
    def detect_with_regex(self, sentence: str) -> Tuple[bool, str]:
        """Use regex patterns for passive voice detection"""
        for pattern_info in self.passive_patterns:
            if re.search(pattern_info["pattern"], sentence, re.IGNORECASE):
                return True, pattern_info["description"]
        
        return False, "No passive voice pattern found"
    
    def transform_classic_passive_with_agent(self, match) -> str:
        """Transform: 'The issue was resolved by the developer' → 'The developer resolved the issue'"""
        subject = match.group(1).strip()
        auxiliary = match.group(2).strip()
        past_participle = match.group(3).strip()
        agent = match.group(4).strip()
        
        # Convert past participle to active verb
        active_verb = self.convert_to_active_verb(past_participle, auxiliary)
        
        return f"{agent.capitalize()} {active_verb} {subject.lower()}"
    
    def transform_passive_without_agent(self, match) -> str:
        """Transform: 'The issue was resolved' → 'Someone resolved the issue' or suggest active alternative"""
        subject = match.group(1).strip()
        auxiliary = match.group(2).strip()
        past_participle = match.group(3).strip()
        
        active_verb = self.convert_to_active_verb(past_participle, auxiliary)
        
        # For imperatives, suggest removing passive construction
        if subject.lower().startswith(('the', 'this', 'that')):
            return f"The system {active_verb} {subject.lower()}"
        else:
            return f"Someone {active_verb} {subject.lower()}"
    
    def transform_relative_clause_passive(self, match) -> str:
        """Transform: 'Delete the languages that are not needed' → 'Delete the unneeded languages'"""
        main_part = match.group(1).strip()
        auxiliary = match.group(2).strip()
        negation = match.group(3).strip() if match.group(3) else ""
        past_participle = match.group(4).strip()
        
        # Convert to adjective form
        if "not" in negation:
            if past_participle == "needed":
                adjective = "unneeded"
            elif past_participle == "required":
                adjective = "unnecessary"
            elif past_participle == "used":
                adjective = "unused"
            else:
                adjective = f"un{past_participle}"
        else:
            adjective = past_participle
        
        # Restructure the sentence
        return f"{main_part.replace('the', f'the {adjective}')}"
    
    def transform_get_passive(self, match) -> str:
        """Transform: 'The data gets processed' → 'The system processes the data'"""
        subject = match.group(1).strip()
        past_participle = match.group(2).strip()
        
        active_verb = self.convert_to_active_verb(past_participle, "get")
        return f"The system {active_verb} {subject.lower()}"
    
    def convert_to_active_verb(self, past_participle: str, auxiliary: str) -> str:
        """Convert past participle to active verb form"""
        
        # Common irregular verbs
        irregular_verbs = {
            "chosen": "chooses" if auxiliary in ["is", "are"] else "chose",
            "taken": "takes" if auxiliary in ["is", "are"] else "took", 
            "given": "gives" if auxiliary in ["is", "are"] else "gave",
            "made": "makes" if auxiliary in ["is", "are"] else "made",
            "done": "does" if auxiliary in ["is", "are"] else "did",
            "seen": "sees" if auxiliary in ["is", "are"] else "saw",
            "found": "finds" if auxiliary in ["is", "are"] else "found",
            "resolved": "resolves" if auxiliary in ["is", "are"] else "resolved",
            "processed": "processes" if auxiliary in ["is", "are"] else "processed",
            "needed": "needs" if auxiliary in ["is", "are"] else "needed",
            "required": "requires" if auxiliary in ["is", "are"] else "required"
        }
        
        if past_participle in irregular_verbs:
            return irregular_verbs[past_participle]
        
        # Regular verbs ending in -ed
        if past_participle.endswith("ed"):
            base_verb = past_participle[:-2]  # Remove -ed
            if auxiliary in ["is", "are"]:
                return f"{base_verb}s" if base_verb.endswith(('s', 'sh', 'ch', 'x', 'z')) else f"{base_verb}s"
            else:
                return past_participle
        
        return past_participle
    
    def transform_passive_to_active(self, sentence: str) -> Tuple[str, str]:
        """
        Transform passive voice sentence to active voice
        
        Returns:
            (transformed_sentence, explanation)
        """
        
        is_passive, pattern_type = self.is_passive_voice(sentence)
        
        if not is_passive:
            return sentence, "No passive voice detected in this sentence."
        
        # Try each transformation pattern
        for pattern_info in self.passive_patterns:
            match = re.search(pattern_info["pattern"], sentence, re.IGNORECASE)
            if match:
                try:
                    transformed = pattern_info["transform"](match)
                    explanation = f"Converted {pattern_info['description']} to active voice."
                    return transformed, explanation
                except Exception as e:
                    continue
        
        # Fallback transformation
        return self.fallback_transformation(sentence), "Applied general active voice transformation."
    
    def fallback_transformation(self, sentence: str) -> str:
        """Fallback transformation for cases not caught by specific patterns"""
        
        # Simple replacements for common passive constructions
        transformations = {
            r"is being (.+)": r"someone is \1ing",
            r"was being (.+)": r"someone was \1ing", 
            r"are being (.+)": r"someone is \1ing",
            r"were being (.+)": r"someone was \1ing",
        }
        
        result = sentence
        for pattern, replacement in transformations.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result

def test_enhanced_passive_processor():
    """Test the enhanced passive voice processor"""
    
    processor = EnhancedPassiveVoiceProcessor()
    
    test_sentences = [
        "Delete the languages that are not needed.",
        "The issue was resolved by the developer.",
        "The data is processed automatically.",
        "Files that are unused should be removed.",
        "The application gets updated weekly.",
        "Errors are logged by the system.",
        "The server was restarted.",
        "Click the button that is highlighted.",
        "Remove items that are not required."
    ]
    
    print("🔍 Enhanced Passive Voice Processor Test")
    print("=" * 50)
    
    for sentence in test_sentences:
        is_passive, pattern_type = processor.is_passive_voice(sentence)
        
        print(f"\nOriginal: '{sentence}'")
        print(f"Passive? {is_passive} ({pattern_type})")
        
        if is_passive:
            transformed, explanation = processor.transform_passive_to_active(sentence)
            print(f"Active:   '{transformed}'")
            print(f"Why:      {explanation}")
        else:
            print("No transformation needed - already in active voice.")

if __name__ == "__main__":
    test_enhanced_passive_processor()
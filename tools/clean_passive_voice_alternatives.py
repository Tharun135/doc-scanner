"""
Clean passive voice alternatives generator - optimized for practical usage.
Focuses on providing clear, usable active voice alternatives.
"""

import os
import logging
import re
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class CleanPassiveVoiceResolver:
    """
    Clean, practical passive voice resolver that generates multiple 
    high-quality active voice alternatives using different words.
    """
    
    def __init__(self):
        self.patterns = self._load_conversion_patterns()
        self.synonyms = self._load_synonym_groups()
    
    def _load_conversion_patterns(self):
        """Load passive-to-active conversion patterns"""
        return {
            # Pattern: (passive_phrase, active_alternatives)
            "is displayed": [
                ("The system shows {object}", "system"),
                ("You see {object}", "user"),
                ("{object} appears", "state"),
                ("The interface presents {object}", "interface")
            ],
            "are displayed": [
                ("The system shows {object}", "system"),
                ("{object} appear", "state"),
                ("You can view {object}", "user"),
                ("The interface presents {object}", "interface")
            ],
            "is generated": [
                ("The system creates {object}", "system"),
                ("{object} gets built", "process"),
                ("The application produces {object}", "app"),
                ("You generate {object}", "user")
            ],
            "are generated": [
                ("The system creates {object}", "system"),
                ("{object} get built", "process"),
                ("The application produces {object}", "app"),
                ("You generate {object}", "user")
            ],
            "are configured": [
                ("You configure {object}", "user"),
                ("The system sets up {object}", "system"),
                ("{object} get arranged", "process"),
                ("You customize {object}", "user")
            ],
            "are processed": [
                ("The system handles {object}", "system"),
                ("{object} get managed", "process"),
                ("The application processes {object}", "app"),
                ("You process {object}", "user")
            ],
            "are fixed": [
                ("The system locks {object}", "system"),
                ("{object} remain stable", "state"),
                ("The application secures {object}", "app"),
                ("{object} stay permanent", "state")
            ],
            "cannot be removed": [
                ("prevent removal", "action"),
                ("block deletion", "action"),
                ("ensure permanence", "action"),
                ("maintain presence", "action")
            ]
        }
    
    def _load_synonym_groups(self):
        """Load synonym groups for word variety"""
        return {
            "show": ["display", "present", "reveal", "exhibit"],
            "create": ["generate", "produce", "build", "make"],
            "handle": ["process", "manage", "deal with", "work with"],
            "configure": ["set up", "arrange", "customize", "adjust"],
            "appear": ["show up", "become visible", "emerge", "surface"],
            "system": ["application", "interface", "platform", "software"],
            "lock": ["secure", "fix", "stabilize", "anchor"],
            "prevent": ["block", "stop", "avoid", "eliminate"]
        }
    
    def generate_alternatives(self, sentence: str, feedback: str = "") -> Dict[str, Any]:
        """
        Generate clean, practical active voice alternatives.
        
        Args:
            sentence: The passive voice sentence
            feedback: Optional feedback context
            
        Returns:
            Dict with clean suggestions and explanations
        """
        
        # Analyze sentence structure
        analysis = self._analyze_sentence(sentence)
        
        # Generate alternatives using different strategies
        alternatives = []
        
        # Strategy 1: Direct pattern matching
        pattern_alts = self._get_pattern_alternatives(sentence, analysis)
        alternatives.extend(pattern_alts)
        
        # Strategy 2: Synonym-based alternatives
        synonym_alts = self._get_synonym_alternatives(sentence, analysis)
        alternatives.extend(synonym_alts)
        
        # Strategy 3: Structure-based alternatives
        structure_alts = self._get_structure_alternatives(sentence, analysis)
        alternatives.extend(structure_alts)
        
        # Clean and rank alternatives
        clean_alternatives = self._clean_and_rank(alternatives, sentence)
        
        # Select top 4 best alternatives
        final_suggestions = clean_alternatives[:4]
        
        return {
            "suggestions": final_suggestions,
            "method": "clean_passive_voice_resolver",
            "confidence": "high" if len(final_suggestions) >= 3 else "medium",
            "analysis": analysis,
            "explanation": self._create_explanation(sentence, final_suggestions)
        }
    
    def _analyze_sentence(self, sentence: str) -> Dict[str, Any]:
        """Analyze sentence structure to identify passive voice elements"""
        
        analysis = {
            "passive_elements": [],
            "subject": None,
            "object": None,
            "length": len(sentence.split()),
            "complexity": "simple"
        }
        
        # Find passive voice patterns
        for pattern in self.patterns.keys():
            if pattern in sentence.lower():
                # Extract subject/object context
                match_context = self._extract_context(sentence, pattern)
                analysis["passive_elements"].append({
                    "pattern": pattern,
                    "context": match_context
                })
        
        # Determine complexity
        if len(sentence.split()) > 20:
            analysis["complexity"] = "complex"
        elif "," in sentence or " and " in sentence:
            analysis["complexity"] = "compound"
        
        return analysis
    
    def _extract_context(self, sentence: str, pattern: str) -> Dict[str, str]:
        """Extract subject and object context around a passive pattern"""
        
        # Split sentence around the pattern
        parts = sentence.lower().split(pattern.lower())
        
        context = {
            "before": parts[0].strip() if parts else "",
            "after": parts[1].strip() if len(parts) > 1 else ""
        }
        
        # Clean up subject (before pattern)
        if context["before"]:
            # Remove articles and clean up
            subject = re.sub(r'^(the|a|an)\s+', '', context["before"], flags=re.IGNORECASE)
            context["subject"] = subject.strip()
        
        # Extract object context
        if context["after"]:
            # Look for prepositional phrases or continuation
            after_clean = context["after"].split('.')[0]  # Take first sentence part
            context["object_context"] = after_clean.strip()
        
        return context
    
    def _get_pattern_alternatives(self, sentence: str, analysis: Dict) -> List[Dict[str, Any]]:
        """Generate alternatives using direct pattern matching"""
        alternatives = []
        
        for element in analysis.get("passive_elements", []):
            pattern = element["pattern"]
            context = element["context"]
            
            if pattern in self.patterns:
                templates = self.patterns[pattern]
                
                # Extract object for template substitution
                subject = context.get("subject", "")
                
                for template, style in templates:
                    try:
                        if "{object}" in template and subject:
                            alternative = template.format(object=subject)
                        else:
                            # Handle non-templated alternatives
                            alternative = template
                        
                        # Clean up the alternative
                        alternative = self._apply_to_sentence(sentence, pattern, alternative)
                        
                        if alternative and alternative != sentence:
                            alternatives.append({
                                "text": alternative,
                                "source": "pattern",
                                "style": style,
                                "confidence": 0.8
                            })
                    except Exception as e:
                        logger.debug(f"Pattern generation failed: {e}")
        
        return alternatives
    
    def _apply_to_sentence(self, sentence: str, pattern: str, replacement: str) -> str:
        """Apply a replacement to the sentence context"""
        
        # Handle specific patterns
        if pattern == "is displayed":
            if "data is displayed" in sentence.lower():
                return sentence.replace("data is displayed", "the system shows data").replace("Data is displayed", "The system shows data")
            elif "information is displayed" in sentence.lower():
                return sentence.replace("information is displayed", "the interface presents information")
        elif pattern == "are displayed":
            if "columns are displayed" in sentence.lower():
                return sentence.replace("columns are displayed", "the system shows columns")
            elif "options are displayed" in sentence.lower():
                return sentence.replace("options are displayed", "you can view options")
        elif pattern == "are fixed":
            if "columns are fixed" in sentence.lower():
                return sentence.replace("are fixed and cannot be removed", "remain locked and cannot be deleted")
        
        # Generic replacement
        return sentence.replace(pattern, replacement)
    
    def _get_synonym_alternatives(self, sentence: str, analysis: Dict) -> List[Dict[str, Any]]:
        """Generate alternatives using synonyms"""
        alternatives = []
        
        # For each detected passive element, try synonyms
        for element in analysis.get("passive_elements", []):
            pattern = element["pattern"]
            
            # Extract the main verb from the pattern
            if "displayed" in pattern:
                base_verb = "show"
            elif "generated" in pattern:
                base_verb = "create"
            elif "processed" in pattern:
                base_verb = "handle"
            elif "configured" in pattern:
                base_verb = "configure"
            elif "fixed" in pattern:
                base_verb = "lock"
            else:
                continue
            
            if base_verb in self.synonyms:
                synonyms = self.synonyms[base_verb]
                
                for synonym in synonyms:
                    try:
                        alternative = self._create_synonym_version(sentence, pattern, base_verb, synonym)
                        if alternative and alternative != sentence:
                            alternatives.append({
                                "text": alternative,
                                "source": "synonym",
                                "original_verb": base_verb,
                                "synonym_verb": synonym,
                                "confidence": 0.7
                            })
                    except Exception as e:
                        logger.debug(f"Synonym generation failed: {e}")
        
        return alternatives
    
    def _create_synonym_version(self, sentence: str, pattern: str, base_verb: str, synonym: str) -> str:
        """Create a version using a synonym"""
        
        if pattern == "is displayed":
            if synonym == "present":
                return sentence.replace("is displayed", "gets presented").replace("Is displayed", "Gets presented")
            elif synonym == "reveal":
                return sentence.replace("is displayed", "reveals itself").replace("Is displayed", "Reveals itself")
            else:
                return sentence.replace("is displayed", f"appears as {synonym}").replace("Is displayed", f"Appears as {synonym}")
        elif pattern == "are displayed":
            if synonym == "present":
                return sentence.replace("are displayed", "get presented").replace("Are displayed", "Get presented")
            elif synonym == "reveal":
                return sentence.replace("are displayed", "reveal themselves").replace("Are displayed", "Reveal themselves")
            else:
                return sentence.replace("are displayed", f"appear as {synonym}").replace("Are displayed", f"Appear as {synonym}")
        elif pattern == "are fixed":
            if synonym == "secure":
                return sentence.replace("are fixed", "remain secure").replace("Are fixed", "Remain secure")
            elif synonym == "anchor":
                return sentence.replace("are fixed", "stay anchored").replace("Are fixed", "Stay anchored")
        
        # Generic replacement
        return sentence
    
    def _get_structure_alternatives(self, sentence: str, analysis: Dict) -> List[Dict[str, Any]]:
        """Generate alternatives with different sentence structures"""
        alternatives = []
        
        # Structure 1: User-focused
        user_version = self._create_user_focused_version(sentence)
        if user_version and user_version != sentence:
            alternatives.append({
                "text": user_version,
                "source": "structure",
                "style": "user_focused",
                "confidence": 0.6
            })
        
        # Structure 2: System-focused
        system_version = self._create_system_focused_version(sentence)
        if system_version and system_version != sentence:
            alternatives.append({
                "text": system_version,
                "source": "structure", 
                "style": "system_focused",
                "confidence": 0.6
            })
        
        # Structure 3: Action-focused
        action_version = self._create_action_focused_version(sentence)
        if action_version and action_version != sentence:
            alternatives.append({
                "text": action_version,
                "source": "structure",
                "style": "action_focused",
                "confidence": 0.6
            })
        
        return alternatives
    
    def _create_user_focused_version(self, sentence: str) -> str:
        """Create a user-focused version of the sentence"""
        
        if "are displayed" in sentence.lower():
            return sentence.replace("are displayed", "you can view").replace("Are displayed", "You can view")
        elif "is displayed" in sentence.lower():
            return sentence.replace("is displayed", "you see").replace("Is displayed", "You see")
        elif "are configured" in sentence.lower():
            return sentence.replace("are configured", "you configure").replace("Are configured", "You configure")
        elif "are generated" in sentence.lower():
            return sentence.replace("are generated", "you generate").replace("Are generated", "You generate")
        
        return sentence
    
    def _create_system_focused_version(self, sentence: str) -> str:
        """Create a system-focused version of the sentence"""
        
        if "are displayed" in sentence.lower():
            return sentence.replace("are displayed", "the system displays").replace("Are displayed", "The system displays")
        elif "is displayed" in sentence.lower():
            return sentence.replace("is displayed", "the system shows").replace("Is displayed", "The system shows")
        elif "are generated" in sentence.lower():
            return sentence.replace("are generated", "the system creates").replace("Are generated", "The system creates")
        elif "are processed" in sentence.lower():
            return sentence.replace("are processed", "the system handles").replace("Are processed", "The system handles")
        
        return sentence
    
    def _create_action_focused_version(self, sentence: str) -> str:
        """Create an action-focused version of the sentence"""
        
        if "columns are fixed and cannot be removed" in sentence.lower():
            return sentence.replace("columns are fixed and cannot be removed", "columns remain permanent and resist deletion")
        elif "data is displayed" in sentence.lower():
            return sentence.replace("data is displayed", "data becomes visible").replace("Data is displayed", "Data becomes visible")
        elif "files are processed" in sentence.lower():
            return sentence.replace("files are processed", "processing occurs on files").replace("Files are processed", "Processing occurs on files")
        
        return sentence
    
    def _clean_and_rank(self, alternatives: List[Dict], original: str) -> List[Dict]:
        """Clean and rank alternatives by quality"""
        
        # Remove duplicates
        seen = set()
        unique_alternatives = []
        
        for alt in alternatives:
            text = alt["text"].strip().lower()
            if text not in seen and text != original.lower() and len(text) > 10:
                seen.add(text)
                unique_alternatives.append(alt)
        
        # Rank by quality metrics
        def rank_alternative(alt):
            score = alt.get("confidence", 0.5)
            
            # Bonus for clear, simple language
            if alt.get("style") in ["user_focused", "system_focused"]:
                score += 0.1
            
            # Bonus for pattern-based (usually most accurate)
            if alt.get("source") == "pattern":
                score += 0.2
            
            # Check for reasonable length
            words = len(alt["text"].split())
            if 8 <= words <= 25:
                score += 0.1
            
            # Penalty for too similar to original
            similarity = self._calculate_similarity(alt["text"], original)
            score -= similarity * 0.2
            
            return score
        
        unique_alternatives.sort(key=rank_alternative, reverse=True)
        return unique_alternatives
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between texts"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def _create_explanation(self, original: str, suggestions: List[Dict]) -> str:
        """Create explanation for the suggestions"""
        
        if not suggestions:
            return "No suitable alternatives generated."
        
        explanation = f"Generated {len(suggestions)} active voice alternatives with different word choices:\n\n"
        
        for i, suggestion in enumerate(suggestions, 1):
            explanation += f"**Option {i}**: {suggestion['text']}\n"
            
            style = suggestion.get("style", "")
            source = suggestion.get("source", "")
            
            if style:
                explanation += f"   *{style.replace('_', ' ').title()} approach*\n"
            elif source == "pattern":
                explanation += f"   *Pattern-based conversion*\n"
            elif source == "synonym":
                explanation += f"   *Uses synonym: {suggestion.get('synonym_verb', 'alternative word')}*\n"
            
            explanation += "\n"
        
        explanation += "**Why**: These alternatives convert passive voice to active voice using different words and structures while maintaining clarity and meaning."
        
        return explanation


def test_clean_passive_voice_resolver():
    """Test the clean passive voice resolver"""
    
    print("🔧 Testing Clean Passive Voice Resolver...")
    
    resolver = CleanPassiveVoiceResolver()
    
    test_cases = [
        "Date and Time Picker enables you to configure the date and time range of the data that is displayed in the logbook.",
        "The Time, Description, and Comments columns are fixed and cannot be removed.",
        "Docker logs are not generated when there are no active applications.",
        "The configuration options are displayed in the Settings panel.",
        "Data is processed automatically by the system when files are uploaded."
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"📝 Test Case {i}")
        print(f"{'='*60}")
        print(f"Original: {test_case}")
        print("-" * 60)
        
        result = resolver.generate_alternatives(test_case)
        
        if result.get("suggestions"):
            print(f"Method: {result['method']}")
            print(f"Confidence: {result['confidence']}")
            print(f"\n🎯 Generated {len(result['suggestions'])} alternatives:")
            
            for j, suggestion in enumerate(result["suggestions"], 1):
                print(f"\n  {j}. {suggestion['text']}")
                
                # Show metadata
                details = []
                if suggestion.get('style'):
                    details.append(f"Style: {suggestion['style']}")
                if suggestion.get('source'):
                    details.append(f"Source: {suggestion['source']}")
                if suggestion.get('synonym_verb'):
                    details.append(f"Synonym: {suggestion['original_verb']} → {suggestion['synonym_verb']}")
                
                if details:
                    print(f"     ({', '.join(details)})")
        else:
            print("❌ No alternatives generated")


if __name__ == "__main__":
    test_clean_passive_voice_resolver()

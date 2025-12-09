"""
Enhanced Passive Voice Resolution with AI-Generated Alternatives
Generates multiple active voice suggestions using different words while preserving meaning through RAG.
"""

import os
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
import json

# Import the existing RAG system
from scripts.docscanner_ollama_rag import DocScannerOllamaRAG

logger = logging.getLogger(__name__)

class EnhancedPassiveVoiceResolver(DocScannerOllamaRAG):
    """
    Enhanced passive voice resolver that generates multiple active voice alternatives
    using different words while preserving meaning through RAG.
    """
    
    def __init__(self):
        super().__init__()
        self._load_synonym_knowledge()
        self._load_alternative_patterns()
    
    def _load_synonym_knowledge(self):
        """Load synonym patterns for generating alternative active voice suggestions"""
        self.synonym_patterns = {
            # Verb synonyms for passive voice conversion
            "display": ["show", "present", "render", "exhibit"],
            "generate": ["create", "produce", "make", "build"],
            "configure": ["set up", "arrange", "customize", "adjust"],
            "process": ["handle", "manage", "execute", "run"],
            "create": ["build", "generate", "develop", "establish"],
            "enable": ["activate", "turn on", "allow", "permit"],
            "remove": ["delete", "eliminate", "clear", "erase"],
            "fix": ["lock", "secure", "stabilize", "set"],
            
            # Subject alternatives for technical writing
            "system": ["application", "platform", "interface", "software"],
            "user": ["operator", "person", "individual", "administrator"],
            "team": ["group", "developers", "staff", "organization"],
            "daemon": ["service", "process", "application", "program"],
            
            # Action phrases
            "is displayed": ["appears", "shows up", "becomes visible", "gets presented"],
            "are configured": ["get set up", "become arranged", "get customized"],
            "is generated": ["gets created", "becomes produced", "gets built"],
            "are processed": ["get handled", "become managed", "get executed"],
        }
        
        # Load enhanced rules from JSON file if available
        self._load_enhanced_rules_from_file()
    
    def _load_alternative_patterns(self):
        """Load alternative phrasing patterns for active voice conversion"""
        self.alternative_patterns = {
            # Pattern: passive_phrase -> [(active_template, subject_type), ...]
            "are displayed": [
                ("The {subject} shows {object}", "system"),
                ("You can see {object} in the {subject}", "user"),
                ("{object} appears on the {subject}", "interface"),
                ("The {subject} presents {object}", "application")
            ],
            "is generated": [
                ("The {subject} creates {object}", "system"),
                ("{object} gets built by the {subject}", "process"),
                ("The {subject} produces {object}", "application"),
                ("{object} emerges from the {subject}", "system")
            ],
            "are configured": [
                ("You configure {object}", "user"),
                ("The {subject} sets up {object}", "system"),
                ("{object} gets arranged by {subject}", "process"),
                ("You can customize {object}", "user")
            ],
            "are fixed": [
                ("The {subject} locks {object}", "system"),
                ("{object} remains stable", "state"),
                ("The {subject} secures {object}", "application"),
                ("{object} stays in place", "interface")
            ],
            "cannot be removed": [
                ("prevent removal", "action"),
                ("block deletion", "action"),
                ("ensure permanence", "action"),
                ("maintain presence", "action")
            ]
        }
    
    def generate_passive_voice_alternatives(self, sentence: str, feedback_text: str = "") -> Dict[str, Any]:
        """
        Generate multiple active voice alternatives using different words while preserving meaning.
        
        Args:
            sentence: The passive voice sentence to convert
            feedback_text: Optional feedback context
            
        Returns:
            Dict with multiple suggestions, explanations, and metadata
        """
        
        if not self.is_initialized:
            return self._fallback_alternatives(sentence)
        
        try:
            # Analyze the sentence structure
            analysis = self._analyze_passive_sentence(sentence)
            
            # Generate RAG-enhanced alternatives
            rag_alternatives = self._get_rag_alternatives(sentence, analysis)
            
            # Generate pattern-based alternatives
            pattern_alternatives = self._get_pattern_alternatives(sentence, analysis)
            
            # Generate synonym-based alternatives  
            synonym_alternatives = self._get_synonym_alternatives(sentence, analysis)
            
            # Combine and rank alternatives
            all_alternatives = []
            all_alternatives.extend(rag_alternatives)
            all_alternatives.extend(pattern_alternatives)
            all_alternatives.extend(synonym_alternatives)
            
            # Remove duplicates and rank by quality
            unique_alternatives = self._deduplicate_and_rank(all_alternatives, sentence)
            
            # Select top 3-4 best alternatives
            final_suggestions = unique_alternatives[:4]
            
            return {
                "suggestions": final_suggestions,
                "method": "enhanced_passive_voice_rag",
                "confidence": "high",
                "analysis": analysis,
                "total_generated": len(all_alternatives),
                "explanation": self._generate_explanation(sentence, final_suggestions)
            }
            
        except Exception as e:
            logger.error(f"Enhanced passive voice generation failed: {e}")
            return self._fallback_alternatives(sentence)
    
    def _analyze_passive_sentence(self, sentence: str) -> Dict[str, Any]:
        """Analyze the structure of a passive voice sentence"""
        analysis = {
            "passive_patterns": [],
            "subject": None,
            "object": None,
            "action": None,
            "auxiliary_verbs": [],
            "length": len(sentence.split()),
            "complexity": "simple"
        }
        
        # Detect passive voice patterns
        passive_patterns = [
            (r'(.*?)\s+(is|are|was|were)\s+(\w+ed|displayed|generated|configured|fixed|created|processed)', 'be_verb_past_participle'),
            (r'(.*?)\s+(cannot|can\'t)\s+be\s+(\w+ed|removed|deleted|changed)', 'modal_be_past_participle'),
            (r'(.*?)\s+(is|are|was|were)\s+being\s+(\w+ed|processed|handled)', 'progressive_passive'),
        ]
        
        for pattern, pattern_type in passive_patterns:
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                analysis["passive_patterns"].append({
                    "type": pattern_type,
                    "subject": match.group(1).strip(),
                    "auxiliary": match.group(2),
                    "action": match.group(3),
                    "full_match": match.group(0)
                })
        
        # Extract key components
        if analysis["passive_patterns"]:
            first_pattern = analysis["passive_patterns"][0]
            analysis["subject"] = first_pattern["subject"]
            analysis["action"] = first_pattern["action"]
        
        # Determine complexity
        if len(sentence.split()) > 20:
            analysis["complexity"] = "complex"
        elif "," in sentence or "and" in sentence:
            analysis["complexity"] = "compound"
        
        return analysis
    
    def _get_rag_alternatives(self, sentence: str, analysis: Dict) -> List[Dict[str, Any]]:
        """Generate alternatives using RAG system with different prompting strategies"""
        alternatives = []
        
        if not self.query_engine:
            return alternatives
        
        try:
            # Strategy 1: Focus on word variety
            query1 = f"""Rewrite this passive sentence in active voice using different action words.

Original: {sentence}

Provide 3 different active voice versions using synonyms:
1. Version with 'shows/displays'
2. Version with 'presents/reveals' 
3. Version with 'provides/offers'

Each version:"""
            
            response1 = self.query_engine.query(query1)
            alternatives.extend(self._extract_alternatives_from_rag(str(response1), "word_variety"))
            
            # Strategy 2: Focus on subject variety
            query2 = f"""Rewrite this passive sentence in active voice using different subjects.

Original: {sentence}

Provide 3 versions with different actors:
1. Version with 'The system...'
2. Version with 'You can...'
3. Version with 'The interface...'

Each version:"""
            
            response2 = self.query_engine.query(query2)
            alternatives.extend(self._extract_alternatives_from_rag(str(response2), "subject_variety"))
            
            # Strategy 3: Focus on structure variety
            query3 = f"""Rewrite this passive sentence using completely different sentence structures while keeping the same meaning.

Original: {sentence}

Provide 3 structurally different versions:
1. Simple subject-verb-object
2. Compound sentence with 'and'
3. Sentence starting with action word

Each version:"""
            
            response3 = self.query_engine.query(query3)
            alternatives.extend(self._extract_alternatives_from_rag(str(response3), "structure_variety"))
            
        except Exception as e:
            logger.warning(f"RAG alternative generation failed: {e}")
        
        return alternatives
    
    def _extract_alternatives_from_rag(self, rag_response: str, strategy: str) -> List[Dict[str, Any]]:
        """Extract individual alternatives from RAG response"""
        alternatives = []
        
        # Split response into lines and look for numbered alternatives
        lines = rag_response.split('\n')
        current_alternative = ""
        
        for line in lines:
            line = line.strip()
            
            # Look for numbered items or bullet points
            if re.match(r'^\d+\.', line) or line.startswith('-') or line.startswith('•'):
                if current_alternative:
                    # Process previous alternative
                    clean_alt = self._clean_rag_alternative(current_alternative)
                    if clean_alt and len(clean_alt) > 10:
                        alternatives.append({
                            "text": clean_alt,
                            "source": "rag",
                            "strategy": strategy,
                            "confidence": 0.8
                        })
                
                # Start new alternative
                current_alternative = re.sub(r'^\d+\.\s*|^[-•]\s*', '', line)
            else:
                # Continue current alternative
                if current_alternative and line:
                    current_alternative += " " + line
        
        # Process last alternative
        if current_alternative:
            clean_alt = self._clean_rag_alternative(current_alternative)
            if clean_alt and len(clean_alt) > 10:
                alternatives.append({
                    "text": clean_alt,
                    "source": "rag",
                    "strategy": strategy,
                    "confidence": 0.8
                })
        
        return alternatives
    
    def _clean_rag_alternative(self, text: str) -> str:
        """Clean up a RAG-generated alternative"""
        # Remove common prefixes
        prefixes = [
            "Version with", "Version:", "Alternative:", "Rewrite:", 
            "Active voice:", "Better:", "Improved:"
        ]
        
        for prefix in prefixes:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
        
        # Remove quotes
        text = text.strip('"\'')
        
        # Clean up common artifacts
        text = re.sub(r'^\w+\s*version:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Each version:\s*', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _get_pattern_alternatives(self, sentence: str, analysis: Dict) -> List[Dict[str, Any]]:
        """Generate alternatives using predefined patterns"""
        alternatives = []
        
        for pattern_info in analysis.get("passive_patterns", []):
            subject = pattern_info.get("subject", "")
            action = pattern_info.get("action", "")
            
            # Look for matching patterns in our knowledge base
            for passive_phrase, templates in self.alternative_patterns.items():
                if passive_phrase in sentence.lower():
                    for template, subject_type in templates:
                        try:
                            # Extract object from sentence context
                            object_match = self._extract_object_from_sentence(sentence, passive_phrase)
                            
                            if object_match:
                                # Generate alternative using template
                                alternative = template.format(
                                    subject=self._get_appropriate_subject(subject_type, subject),
                                    object=object_match
                                )
                                
                                alternatives.append({
                                    "text": alternative,
                                    "source": "pattern",
                                    "pattern": passive_phrase,
                                    "confidence": 0.7
                                })
                        except Exception as e:
                            logger.debug(f"Pattern generation failed: {e}")
        
        return alternatives
    
    def _get_synonym_alternatives(self, sentence: str, analysis: Dict) -> List[Dict[str, Any]]:
        """Generate alternatives using synonym substitution"""
        alternatives = []
        
        # For each detected action, try synonyms
        for pattern_info in analysis.get("passive_patterns", []):
            action = pattern_info.get("action", "")
            
            # Find base verb for this action
            base_verb = self._get_base_verb(action)
            
            if base_verb in self.synonym_patterns:
                synonyms = self.synonym_patterns[base_verb]
                
                for synonym in synonyms:
                    try:
                        # Create alternative using synonym
                        alternative = self._create_synonym_alternative(sentence, action, synonym, analysis)
                        
                        if alternative and alternative != sentence:
                            alternatives.append({
                                "text": alternative,
                                "source": "synonym",
                                "original_verb": base_verb,
                                "synonym_verb": synonym,
                                "confidence": 0.6
                            })
                    except Exception as e:
                        logger.debug(f"Synonym generation failed: {e}")
        
        return alternatives
    
    def _get_base_verb(self, action: str) -> str:
        """Extract base verb from action (e.g., 'displayed' -> 'display')"""
        # Handle common past participles
        verb_mappings = {
            "displayed": "display",
            "generated": "generate", 
            "configured": "configure",
            "processed": "process",
            "created": "create",
            "enabled": "enable",
            "removed": "remove",
            "fixed": "fix"
        }
        
        return verb_mappings.get(action.lower(), action)
    
    def _create_synonym_alternative(self, sentence: str, original_action: str, synonym: str, analysis: Dict) -> str:
        """Create an alternative sentence using a synonym for the action"""
        
        # Simple substitution approach first
        if "is displayed" in sentence.lower():
            alternatives = [
                sentence.replace("is displayed", f"appears").replace("Is displayed", "Appears"),
                sentence.replace("is displayed", f"shows up").replace("Is displayed", "Shows up"),
                sentence.replace("data is displayed", f"the system shows data").replace("Data is displayed", "The system shows data")
            ]
        elif "are displayed" in sentence.lower():
            alternatives = [
                sentence.replace("are displayed", f"appear").replace("Are displayed", "Appear"),
                sentence.replace("are displayed", f"show up").replace("Are displayed", "Show up"),
                sentence.replace("columns are displayed", f"the system displays columns").replace("Columns are displayed", "The system displays columns")
            ]
        elif "are fixed" in sentence.lower():
            alternatives = [
                sentence.replace("are fixed and cannot be removed", f"remain locked and cannot be deleted"),
                sentence.replace("are fixed and cannot be removed", f"stay permanent and cannot be erased"),
                sentence.replace("are fixed", f"remain stable").replace("Are fixed", "Remain stable")
            ]
        else:
            # Generic pattern replacement
            alternatives = [sentence.replace(original_action, synonym)]
        
        # Return the best alternative
        for alt in alternatives:
            if alt != sentence and len(alt) > 10:
                return alt
        
        return sentence
    
    def _load_enhanced_rules_from_file(self):
        """Load enhanced passive voice rules from JSON configuration file"""
        rules_file = "enhanced_passive_voice_rules.json"
        
        if os.path.exists(rules_file):
            try:
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                
                # Load synonym categories
                if "synonym_categories" in rules_data:
                    for category, synonyms in rules_data["synonym_categories"].items():
                        base_verb = category.replace("_verbs", "")
                        if base_verb not in self.synonym_patterns:
                            self.synonym_patterns[base_verb] = synonyms
                        else:
                            # Extend existing synonyms
                            self.synonym_patterns[base_verb].extend(synonyms)
                
                # Load sentence patterns
                if "sentence_patterns" in rules_data:
                    patterns = rules_data["sentence_patterns"]
                    if "passive_to_active_templates" in patterns:
                        # Store templates for later use
                        self.active_templates = patterns["passive_to_active_templates"]
                    if "technical_subjects" in patterns:
                        self.technical_subjects = patterns["technical_subjects"]
                    if "user_subjects" in patterns:
                        self.user_subjects = patterns["user_subjects"]
                
                logger.info(f"Loaded enhanced passive voice rules from {rules_file}")
                
            except Exception as e:
                logger.warning(f"Could not load enhanced rules from {rules_file}: {e}")
        else:
            logger.info(f"Enhanced rules file {rules_file} not found, using defaults")
    
    def _extract_object_from_sentence(self, sentence: str, passive_phrase: str) -> Optional[str]:
        """Extract the object being acted upon in a passive sentence"""
        
        # Look before the passive phrase for the subject/object
        parts = sentence.lower().split(passive_phrase)
        if len(parts) >= 2:
            before = parts[0].strip()
            # Clean up common articles and determiners
            before = re.sub(r'^(the|a|an)\s+', '', before, flags=re.IGNORECASE)
            return before
        
        return None
    
    def _get_appropriate_subject(self, subject_type: str, original_subject: str) -> str:
        """Get an appropriate subject based on type and context"""
        
        subject_mappings = {
            "system": "system",
            "user": "you",
            "interface": "interface", 
            "application": "application",
            "process": "system"
        }
        
        return subject_mappings.get(subject_type, "system")
    
    def _deduplicate_and_rank(self, alternatives: List[Dict], original: str) -> List[Dict]:
        """Remove duplicates and rank alternatives by quality"""
        
        # Remove exact duplicates
        seen_texts = set()
        unique_alternatives = []
        
        for alt in alternatives:
            text = alt["text"].strip().lower()
            if text not in seen_texts and text != original.lower():
                seen_texts.add(text)
                unique_alternatives.append(alt)
        
        # Rank by confidence and other quality metrics
        def rank_alternative(alt):
            confidence = alt.get("confidence", 0.5)
            
            # Bonus for RAG-generated
            if alt.get("source") == "rag":
                confidence += 0.1
            
            # Bonus for variety in word choice
            if alt.get("strategy") == "word_variety":
                confidence += 0.1
            
            # Penalty for very similar to original
            similarity = self._calculate_similarity(alt["text"].lower(), original.lower())
            confidence -= similarity * 0.3
            
            # Bonus for reasonable length
            words = len(alt["text"].split())
            if 8 <= words <= 25:
                confidence += 0.1
            
            return confidence
        
        # Sort by ranking score
        unique_alternatives.sort(key=rank_alternative, reverse=True)
        
        return unique_alternatives
    
    def _generate_explanation(self, original: str, suggestions: List[Dict]) -> str:
        """Generate an explanation of the alternatives provided"""
        
        if not suggestions:
            return "No suitable active voice alternatives could be generated."
        
        explanation = f"Generated {len(suggestions)} active voice alternatives:\n\n"
        
        for i, suggestion in enumerate(suggestions, 1):
            source = suggestion.get("source", "unknown")
            strategy = suggestion.get("strategy", "")
            
            explanation += f"**Option {i}**: {suggestion['text']}\n"
            
            if source == "rag":
                explanation += f"   *AI-generated using {strategy} strategy*\n"
            elif source == "pattern":
                explanation += f"   *Pattern-based conversion*\n"
            elif source == "synonym":
                explanation += f"   *Synonym-based alternative*\n"
            
            explanation += "\n"
        
        explanation += f"**Why**: These alternatives convert the passive voice to active voice while using different words and structures to provide variety and maintain clarity."
        
        return explanation
    
    def _fallback_alternatives(self, sentence: str) -> Dict[str, Any]:
        """Provide fallback alternatives when RAG system is unavailable"""
        
        alternatives = []
        
        # Basic pattern-based alternatives
        if "are displayed" in sentence.lower():
            alternatives = [
                {"text": sentence.replace("are displayed", "appear"), "source": "fallback"},
                {"text": sentence.replace("are displayed", "show up"), "source": "fallback"},
                {"text": sentence.replace("data is displayed", "the system shows data"), "source": "fallback"}
            ]
        elif "is generated" in sentence.lower():
            alternatives = [
                {"text": sentence.replace("is generated", "gets created"), "source": "fallback"},
                {"text": sentence.replace("is generated", "emerges"), "source": "fallback"}
            ]
        else:
            alternatives = [
                {"text": f"Rewrite in active voice: {sentence}", "source": "fallback"}
            ]
        
        return {
            "suggestions": alternatives[:3],
            "method": "fallback_pattern_matching",
            "confidence": "low",
            "explanation": "Basic active voice alternatives (RAG system unavailable)"
        }


def test_enhanced_passive_voice_resolver():
    """Test the enhanced passive voice resolver"""
    
    print("🔧 Testing Enhanced Passive Voice Resolver...")
    
    resolver = EnhancedPassiveVoiceResolver()
    
    # Test cases
    test_cases = [
        "Date and Time Picker enables you to configure the date and time range of the data that is displayed in the logbook.",
        "The Time, Description, and Comments columns are fixed and cannot be removed.",
        "Docker logs are not generated when there are no active applications.",
        "The configuration options are displayed in the Settings panel.",
        "Data is processed automatically by the system."
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}:")
        print(f"Original: {test_case}")
        print("-" * 60)
        
        result = resolver.generate_passive_voice_alternatives(test_case)
        
        if result.get("suggestions"):
            print(f"Method: {result['method']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Generated {len(result['suggestions'])} alternatives:")
            
            for j, suggestion in enumerate(result["suggestions"], 1):
                print(f"\n  {j}. {suggestion['text']}")
                print(f"     Source: {suggestion.get('source', 'unknown')}")
                if suggestion.get('strategy'):
                    print(f"     Strategy: {suggestion['strategy']}")
        else:
            print("❌ No alternatives generated")


if __name__ == "__main__":
    test_enhanced_passive_voice_resolver()

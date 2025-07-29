"""
Enhanced AI suggestion system for better writing recommendations.
This module provides improved prompt engineering and context-aware suggestions using OpenAI's ChatGPT.
"""

import json
import re
import openai
import logging
import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from .prompt_templates import (
    AdvancedPromptTemplates, 
    classify_feedback_type, 
    get_document_type_from_string,
    DocumentType,
    FeedbackType
)

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class EnhancedAISuggestionEngine:
    """
    Enhanced AI suggestion engine with better prompt engineering,
    context awareness, and domain-specific knowledge using OpenAI ChatGPT.
    """
    
    def __init__(self, model_name: str = None):
        self.client = self._initialize_openai_client()
        self.model_name = model_name or "gpt-3.5-turbo"
        self.style_guide_context = self._load_style_guide_context()
        
    def _initialize_openai_client(self):
        """Initialize OpenAI client with API key."""
        try:
            # Get API key from environment variable (should be loaded by dotenv)
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                logger.warning("No OpenAI API key found in environment variable OPENAI_API_KEY")
                logger.info("To set up OpenAI: 1) Get API key from https://platform.openai.com/api-keys 2) Set OPENAI_API_KEY environment variable")
                return None
                
            # Create client
            client = openai.OpenAI(api_key=api_key)
            logger.info(f"OpenAI client initialized successfully with key: {api_key[:8]}...")
            return client
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return None
        
    def _get_available_model(self, preferred_model: str = None) -> str:
        """Get the preferred OpenAI model."""
        try:
            if not self.client:
                logger.warning("No OpenAI client available")
                return None
                
            # If a specific model is requested, use it
            if preferred_model:
                logger.info(f"Using requested model: {preferred_model}")
                return preferred_model
            
            # Default to GPT-3.5-turbo for cost effectiveness
            # Can be upgraded to GPT-4 for better quality
            available_models = [
                "gpt-4o-mini",      # Most cost-effective GPT-4 class model
                "gpt-3.5-turbo",    # Reliable and fast
                "gpt-4o",           # Best quality but more expensive
            ]
            
            # Use the first available model
            model_name = available_models[0]
            logger.info(f"Using OpenAI model: {model_name}")
            return model_name
            
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            return None
        
    def _load_style_guide_context(self) -> str:
        """Load relevant style guide information for context."""
        return """
Style Guide Context:
- Use active voice instead of passive voice
- Keep sentences under 25 words for better readability
- Use specific, concrete terms instead of vague language
- Avoid jargon unless necessary for technical audiences
- Use parallel structure in lists and series
- Prefer shorter, simpler words when possible
- Use inclusive language and avoid bias
- Be consistent with terminology throughout documents
        """
    
    def create_enhanced_prompt(self, feedback_text: str, sentence_context: str = "", 
                             document_type: str = "general", writing_goals: List[str] = None) -> str:
        """
        Create a comprehensive, context-aware prompt for better AI suggestions.
        
        Args:
            feedback_text: The specific feedback or issue identified
            sentence_context: The actual sentence or text context
            document_type: Type of document (technical, marketing, academic, etc.)
            writing_goals: Specific writing goals or requirements
        """
        
        writing_goals = writing_goals or ["clarity", "conciseness", "professionalism"]
        goals_text = ", ".join(writing_goals)
        
        prompt = f"""You are an expert writing coach and editor specializing in {document_type} writing. Your goal is to provide specific, actionable suggestions that improve {goals_text}.

{self.style_guide_context}

CONTEXT:
Document Type: {document_type}
Writing Goals: {goals_text}
Sentence/Text: "{sentence_context}"
Issue Identified: {feedback_text}

TASK:
Provide a specific, actionable suggestion to improve this text. Your response should include:

1. SPECIFIC PROBLEM: What exactly is wrong (be precise)
2. SUGGESTED IMPROVEMENT: Exact text changes or rewriting
3. EXPLANATION: Why this change improves the writing
4. ALTERNATIVE OPTIONS: 1-2 alternative approaches if applicable

EXAMPLES OF GOOD SUGGESTIONS:

Issue: "Passive voice detected"
Text: "The report was completed by the team."
Response:
- PROBLEM: Uses passive voice, making the sentence less direct and engaging
- IMPROVEMENT: "The team completed the report."
- EXPLANATION: Active voice is more direct, clearer, and engaging for readers
- ALTERNATIVE: "The team finished the report" (for variety)

Issue: "Sentence too long and complex"
Text: "The system, which was developed by our engineering team over the course of several months, provides users with the ability to manage their data more effectively."
Response:
- PROBLEM: 25+ words with embedded clauses make it hard to follow
- IMPROVEMENT: "Our engineering team developed the system over several months. It helps users manage their data more effectively."
- EXPLANATION: Breaking into two sentences improves readability and flow
- ALTERNATIVE: "The new system helps users manage data more effectively. Our engineering team spent several months developing it."

Now provide your suggestion for the current issue:"""

        return prompt
    
    def generate_contextual_suggestion(self, feedback_text: str, sentence_context: str = "",
                                     document_type: str = "general", 
                                     writing_goals: List[str] = None) -> Dict[str, Any]:
        """
        Generate an enhanced AI suggestion with advanced prompt engineering.
        
        Returns:
            Dict containing suggestion, confidence, and metadata
        """
        try:
            # Check for modal verb cases that need special handling
            feedback_lower = feedback_text.lower()
            if ("may" in feedback_lower and "possibility" in feedback_lower) or \
               ("may" in feedback_lower and "permission" in feedback_lower):
                logger.info("Using custom modal verb logic instead of Ollama AI")
                return self.generate_smart_fallback_suggestion(feedback_text, sentence_context)
            
            # Check for backup/back up cases that need special context analysis
            if ("back up" in feedback_lower or "backup" in feedback_lower) and sentence_context:
                logger.info("Using custom backup/back up logic instead of Ollama AI")
                return self.generate_smart_fallback_suggestion(feedback_text, sentence_context)
            
            # Check if we have a valid model
            if not self.model_name:
                logger.warning("No Ollama model available, falling back to rule-based suggestions")
                return self.generate_smart_fallback_suggestion(feedback_text, sentence_context)
            
            # Convert string to enum
            doc_type_enum = get_document_type_from_string(document_type)
            feedback_type_enum = classify_feedback_type(feedback_text)
            
            # Build advanced prompt
            prompt_data = AdvancedPromptTemplates.build_complete_prompt(
                feedback_type=feedback_type_enum,
                issue_description=feedback_text,
                sentence_context=sentence_context,
                document_type=doc_type_enum,
                writing_goals=writing_goals
            )

            # Check if we have a valid OpenAI client
            if not self.client:
                logger.warning("No OpenAI client available, falling back to rule-based suggestions")
                return self.generate_smart_fallback_suggestion(feedback_text, sentence_context)

            logger.info(f"Using OpenAI model: {self.model_name}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': prompt_data["system"]
                    },
                    {
                        'role': 'user',
                        'content': prompt_data["user"]
                    }
                ],
                temperature=0.1,        # Low for consistency
                max_tokens=150,         # Shorter limit for concise responses
                top_p=0.3,             # Focus on most likely tokens
                frequency_penalty=0.3,  # Reduce repetition
                presence_penalty=0.1,   # Encourage diverse vocabulary
                stop=['\n\n', 'ADDITIONAL', 'ALSO', 'FURTHERMORE', 'MOREOVER', 'EXPLANATION:', 'ANALYSIS:', 'NOTE:', 'REMEMBER:', 'CONSIDER:', 'However,', 'Additionally,', 'In conclusion']
            )
            
            # Validate response structure
            if not response or not response.choices or len(response.choices) == 0:
                raise ValueError("Invalid OpenAI response structure - no choices")
                
            if not response.choices[0].message or not response.choices[0].message.content:
                raise ValueError("Invalid OpenAI response structure - no content")
            
            suggestion = response.choices[0].message.content.strip()
            
            if not suggestion:
                raise ValueError("Empty suggestion from OpenAI")
            
            # Post-process to ensure exact format
            suggestion = self._post_process_ai_response(suggestion, sentence_context, feedback_text)
            
            return {
                "suggestion": suggestion,
                "confidence": "high",
                "method": "openai_chatgpt",
                "feedback_type": feedback_type_enum.value,
                "context_used": {
                    "document_type": document_type,
                    "writing_goals": writing_goals,
                    "feedback_classification": feedback_type_enum.value,
                    "has_sentence_context": bool(sentence_context),
                    "prompt_template": "advanced",
                    "model_used": self.model_name,
                    "api_provider": "openai"
                }
            }
            
        except Exception as e:
            logger.error(f"OpenAI ChatGPT suggestion failed: {str(e)}")
            # Fall back to improved rule-based suggestions
            return self.generate_smart_fallback_suggestion(feedback_text, sentence_context)
    
    def generate_smart_fallback_suggestion(self, feedback_text: str, 
                                         sentence_context: str = "") -> Dict[str, Any]:
        """
        Generate intelligent rule-based suggestions when AI is unavailable.
        Much more sophisticated than the original fallback.
        """
        feedback_lower = feedback_text.lower()
        context_lower = sentence_context.lower()
        
        # Check if feedback already contains a specific rewrite suggestion
        if "→ suggested:" in feedback_text.lower() or "suggested:" in feedback_text.lower():
            # Extract the suggested rewrite from the feedback
            suggested_pattern = r'suggested:\s*["\']([^"\']+)["\']'
            match = re.search(suggested_pattern, feedback_text, re.IGNORECASE)
            if match:
                suggested_text = match.group(1)
                return {
                    "suggestion": f'CORRECTED TEXT: "{suggested_text}"\nCHANGE MADE: {feedback_text.split(".")[0]}',
                    "confidence": "high",
                    "method": "rule_based_rewrite",
                    "pattern_matched": "specific_rewrite_provided"
                }
        
        # Check for "Original: ... → Suggested: ..." pattern (with or without quotes)
        rewrite_patterns = [
            r'original:\s*["\']([^"\']+)["\']\s*→\s*suggested:\s*["\']([^"\']+)["\']',  # With quotes
            r'original:\s*"([^"]+)"\s*→\s*suggested:\s*"([^"]+)"',  # Double quotes specifically
            r'original:\s*([^→]+)\s*→\s*suggested:\s*"([^"]+)"'     # Original without quotes, suggested with quotes
        ]
        
        for pattern in rewrite_patterns:
            match = re.search(pattern, feedback_text, re.IGNORECASE)
            if match:
                original_text = match.group(1).strip()
                suggested_text = match.group(2).strip()
                change_description = feedback_text.split(".")[0] if "." in feedback_text else "Applied suggested rewrite"
                return {
                    "suggestion": f'CORRECTED TEXT: "{suggested_text}"\nCHANGE MADE: {change_description}',
                    "confidence": "high", 
                    "method": "rule_based_rewrite",
                    "pattern_matched": "original_to_suggested"
                }
        
        # Advanced pattern matching with context awareness
        suggestions = {
            # Passive voice patterns
            ("passive", "voice"): {
                "suggestion": self._generate_active_voice_suggestion(sentence_context),
                "confidence": "medium"
            },
            
            # Sentence length and complexity
            ("long", "sentence"): {
                "suggestion": self._generate_sentence_shortening_suggestion(sentence_context),
                "confidence": "medium"
            },
            
            # Word choice improvements
            ("vague", "unclear"): {
                "suggestion": "Replace vague terms with specific, concrete language. Add precise details, numbers, or examples to clarify your meaning.",
                "confidence": "medium"
            },
            
            # Readability improvements
            ("complex", "difficult"): {
                "suggestion": "Simplify complex language: use shorter words, break up long phrases, and explain technical terms. Consider your audience's expertise level.",
                "confidence": "medium"
            },
            
            # Structure and flow
            ("transition", "flow", "choppy"): {
                "suggestion": "Improve flow with transition words: 'However' (contrast), 'Therefore' (conclusion), 'Furthermore' (addition), 'Meanwhile' (time), 'In contrast' (comparison).",
                "confidence": "high"
            }
        }
        
        # Find best matching suggestion
        for patterns, suggestion_data in suggestions.items():
            if any(pattern in feedback_lower for pattern in patterns):
                return {
                    "suggestion": suggestion_data["suggestion"],
                    "confidence": suggestion_data["confidence"],
                    "method": "smart_fallback",
                    "pattern_matched": patterns
                }
        
        # Default enhanced suggestion
        return {
            "suggestion": self._generate_general_improvement_suggestion(feedback_text, sentence_context),
            "confidence": "low",
            "method": "general_fallback"
        }
    
    def _generate_active_voice_suggestion(self, sentence: str) -> str:
        """Generate specific active voice suggestions with actual rewrite."""
        if not sentence:
            return "Convert passive voice to active voice: identify who performs the action and make them the subject."
        
        # Try to actually convert the sentence to active voice
        active_version = self._convert_passive_to_active(sentence)
        if active_version and active_version != sentence:
            return f'CORRECTED TEXT: "{active_version}"\nCHANGE MADE: Converted passive voice to active voice'
        
        # If automatic conversion fails, provide specific guidance
        return "Rewrite in active voice: move the action performer to the beginning and make them the subject."
    
    def _convert_passive_to_active(self, sentence: str) -> str:
        """Attempt to convert passive voice to active voice."""
        if not sentence:
            return sentence
            
        original = sentence.strip()
        
        # Pattern 1: "X is/was/are/were [verb]ed by Y" -> "Y [verb]s X"
        pattern1 = r'(.+?)\s+(is|was|are|were)\s+(\w+ed|en)\s+by\s+(.+?)(\.|$|,|\s+to\s+|\s+for\s+)'
        match1 = re.search(pattern1, original, re.IGNORECASE)
        if match1:
            subject = match1.group(1).strip()
            be_verb = match1.group(2)
            past_participle = match1.group(3)
            actor = match1.group(4).strip()
            remainder = match1.group(5)
            
            # Convert past participle to active verb
            active_verb = self._past_participle_to_active(past_participle, be_verb)
            if active_verb:
                # Handle the actor - remove articles if needed
                clean_actor = re.sub(r'^(the|a|an)\s+', '', actor, flags=re.IGNORECASE)
                return f"{clean_actor.capitalize()} {active_verb} {subject}{remainder}"
        
        # Pattern 2: "X is/was/are/were [verb]ed to [do something]" -> "[Someone] [verb]s X to [do something]"
        pattern2 = r'(.+?)\s+(is|was|are|were)\s+(\w+ed|en)\s+(to\s+.+?)(\.|$)'
        match2 = re.search(pattern2, original, re.IGNORECASE)
        if match2:
            subject = match2.group(1).strip()
            be_verb = match2.group(2)
            past_participle = match2.group(3)
            purpose = match2.group(4)
            remainder = match2.group(5)
            
            active_verb = self._past_participle_to_active(past_participle, be_verb)
            if active_verb:
                # For technical documents, often "the system" or "users" perform the action
                if 'app' in subject.lower() or 'system' in subject.lower():
                    actor = "The system"
                elif 'command' in subject.lower() or 'message' in subject.lower():
                    actor = "The system"
                elif 'data' in subject.lower():
                    actor = "The application"
                else:
                    actor = "The system"
                return f"{actor} {active_verb} {subject} {purpose}{remainder}"
        
        # Pattern 3: Handle complex sentences with multiple clauses
        # "A further Industrial Edge app called Flow Creator is used to send downlink commands"
        pattern3 = r'(.+?)\s+(is|are|was|were)\s+used\s+to\s+(.+?)(\.|$)'
        match3 = re.search(pattern3, original, re.IGNORECASE)
        if match3:
            subject = match3.group(1).strip()
            be_verb = match3.group(2)
            action = match3.group(3).strip()
            remainder = match3.group(4)
            
            # Extract the actual tool/app name if present
            if "called" in subject:
                parts = subject.split("called")
                if len(parts) >= 2:
                    actor_name = parts[1].strip()
                else:
                    actor_name = subject
            else:
                actor_name = subject
            
            return f"{actor_name} {action}{remainder}"
        
        return original
    
    def _past_participle_to_active(self, past_participle: str, be_verb: str) -> str:
        """Convert past participle to active verb form."""
        pp = past_participle.lower()
        
        # Common irregular verb conversions
        irregular_verbs = {
            'used': 'uses',
            'created': 'creates', 
            'generated': 'generates',
            'processed': 'processes',
            'handled': 'handles',
            'managed': 'manages',
            'executed': 'executes',
            'completed': 'completes',
            'performed': 'performs',
            'detected': 'detects',
            'sent': 'sends',
            'received': 'receives',
            'transmitted': 'transmits',
            'configured': 'configures',
            'established': 'establishes',
            'maintained': 'maintains'
        }
        
        if pp in irregular_verbs:
            return irregular_verbs[pp]
        
        # Regular verbs - remove 'ed' and add 's' for third person
        if pp.endswith('ed'):
            base = pp[:-2]
            # Handle doubled consonants (e.g., 'planned' -> 'plan')
            if len(base) >= 2 and base[-1] == base[-2] and base[-1] in 'bdfglmnprt':
                base = base[:-1]
            return f"{base}s"
        
        # For past participles ending in 'en'
        if pp.endswith('en'):
            base = pp[:-2]
            return f"{base}es"
        
        return f"{pp}s"
    
    def _generate_sentence_shortening_suggestion(self, sentence: str) -> str:
        """Generate specific suggestions for shortening sentences."""
        if not sentence:
            return "Break long sentences into shorter ones. Aim for 15-20 words per sentence."
        
        word_count = len(sentence.split())
        suggestions = []
        
        if word_count > 30:
            suggestions.append("This sentence is very long (30+ words). Break it into 2-3 shorter sentences.")
        elif word_count > 20:
            suggestions.append("Consider breaking this into two sentences for better readability.")
        
        # Look for specific patterns that can be simplified
        if ' which ' in sentence.lower() or ' that ' in sentence.lower():
            suggestions.append("Consider removing relative clauses ('which'/'that') and making separate sentences.")
        
        if sentence.count(',') > 2:
            suggestions.append("This sentence has multiple clauses. Consider breaking at commas to create separate sentences.")
        
        if ' and ' in sentence.lower() and sentence.count(' and ') > 1:
            suggestions.append("Multiple 'and' conjunctions suggest this could be broken into separate sentences.")
        
        return " ".join(suggestions) if suggestions else "Break this long sentence into shorter, more digestible parts."
    
    def _generate_general_improvement_suggestion(self, feedback: str, context: str) -> str:
        """Generate specific, actionable solutions based on the feedback and context."""
        feedback_lower = feedback.lower()
        
        # Check for specific issues and provide targeted solutions
        if "may" in feedback_lower and "possibility" in feedback_lower and context:
            # Handle "may" for possibility - remove "may" without replacement
            rewritten = re.sub(r'\bmay\s+', '', context, flags=re.IGNORECASE)
            # Clean up any double spaces
            rewritten = re.sub(r'\s+', ' ', rewritten).strip()
            # Capitalize first letter if needed
            if rewritten and rewritten[0].islower():
                rewritten = rewritten[0].upper() + rewritten[1:]
            return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Removed "may" to make statement more direct'
        
        elif "may" in feedback_lower and "permission" in feedback_lower and context:
            # Handle "may" for permission - change to "can"
            rewritten = re.sub(r'\bmay\b', 'can', context, flags=re.IGNORECASE)
            return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Replaced "may" with "can" for permission context'
        
        elif ("back up" in feedback_lower or "backup" in feedback_lower) and context:
            # Handle backup/back up terminology with proper context analysis
            context_lower = context.lower()
            
            # Check if "backup" is used correctly as a noun/adjective
            noun_patterns = [
                r'\bbackup\s+(files?|data|documents?|system|solution|strategy|process|operation)\b',
                r'\b(create|make|have|support|provide|include)\s+backup\b',
                r'\b(the|a|an|this|that|these|those)\s+backup\b',
                r'\bbackup\s+(and|or)\b'
            ]
            
            # Check if "backup" is correctly used as noun/adjective
            is_correct_noun_usage = any(re.search(pattern, context_lower) for pattern in noun_patterns)
            
            if is_correct_noun_usage:
                # This is correct usage - backup as noun/adjective
                return f'CORRECTED TEXT: "{context}"\nCHANGE MADE: No change needed - "backup" is correctly used as a noun/adjective here'
            
            # Check if it should be converted to verb form
            verb_patterns = [
                r'\b(to|should|must|can|will|need to)\s+backup\b',
                r'\bbackup\s+(your|the|all|these|those)\s+(files?|data|documents?)\b',
                r'\b(please|remember to|don\'t forget to)\s+backup\b'
            ]
            
            should_be_verb = any(re.search(pattern, context_lower) for pattern in verb_patterns)
            
            if should_be_verb:
                # Convert to verb form
                rewritten = re.sub(r'\bbackup\b', 'back up', context, flags=re.IGNORECASE)
                return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Changed "backup" to "back up" when used as a verb'
            
            # If unclear, provide guidance
            return f'CORRECTED TEXT: "{context}"\nCHANGE MADE: Context unclear - use "backup" as noun/adjective ("backup files") or "back up" as verb ("back up your files")'
        
        elif "can" in feedback_lower and context:
            # Handle modal verb "can" specifically with improved logic
            context_lower = context.lower()
            
            # Handle "you can" instructions - convert to imperative
            if "you can" in context_lower:
                # Pattern: "You can [verb] [rest of sentence]" -> "[Verb] [rest of sentence]"
                rewritten = re.sub(r'\byou can\s+(\w+)', r'\1', context, flags=re.IGNORECASE)
                if rewritten and rewritten[0].islower():
                    rewritten = rewritten[0].upper() + rewritten[1:]
                return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Converted "you can" instruction to direct imperative form'
            
            # Handle other subjects with "can"
            elif " can " in context_lower:
                # Look for various patterns and handle them appropriately
                
                # Pattern: "Users can access..." -> "Users access..."
                users_pattern = r'\b(users?|administrators?|developers?|operators?)\s+can\s+(\w+)'
                users_match = re.search(users_pattern, context, re.IGNORECASE)
                if users_match:
                    subject = users_match.group(1)
                    verb = users_match.group(2)
                    rewritten = re.sub(users_pattern, f'{subject} {verb}', context, flags=re.IGNORECASE)
                    return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Converted modal verb "can" to simple present tense'
                
                # Pattern: "The system can process..." -> "The system processes..."
                system_pattern = r'\b(the\s+(?:system|application|software|platform|tool|connector))\s+can\s+(\w+)'
                system_match = re.search(system_pattern, context, re.IGNORECASE)
                if system_match:
                    subject = system_match.group(1)
                    verb = system_match.group(2)
                    # Add 's' for third person singular with proper verb conjugation
                    verb_form = self._conjugate_third_person_singular(verb)
                    rewritten = re.sub(system_pattern, f'{subject} {verb_form}', context, flags=re.IGNORECASE)
                    return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Converted modal verb "can" to simple present tense'
                
                # Pattern for instructional contexts: "You can migrate..." -> "Migrate..." OR "You have two ways to migrate..."
                migration_pattern = r'\byou can\s+(\w+)\s+(.+?)\s+in\s+(two|multiple|several)\s+ways?:'
                migration_match = re.search(migration_pattern, context, re.IGNORECASE)
                if migration_match:
                    verb = migration_match.group(1)
                    object_part = migration_match.group(2)
                    count = migration_match.group(3)
                    rewritten = f"You have {count} ways to {verb} {object_part}:"
                    return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Rephrased to avoid modal verb "can" while maintaining clarity'
                
                # General fallback pattern
                general_pattern = r'(\w+)\s+can\s+(\w+)'
                general_match = re.search(general_pattern, context, re.IGNORECASE)
                if general_match:
                    subject = general_match.group(1)
                    verb = general_match.group(2)
                    
                    # Check if subject needs verb conjugation
                    if subject.lower() in ['i', 'you', 'we', 'they']:
                        verb_form = verb
                    else:
                        # Third person singular
                        verb_form = self._conjugate_third_person_singular(verb)
                    
                    rewritten = re.sub(general_pattern, f'{subject} {verb_form}', context, flags=re.IGNORECASE)
                    return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Converted modal verb "can" to appropriate verb form'
        
        # Handle passive voice
        if "passive" in feedback_lower and context:
            # Use the improved passive voice conversion
            active_version = self._convert_passive_to_active(context)
            if active_version and active_version != context:
                return f'CORRECTED TEXT: "{active_version}"\nCHANGE MADE: Converted passive voice to active voice'
        
        # Handle long sentences
        if "long" in feedback_lower or "complex" in feedback_lower and context:
            if len(context.split()) > 25:
                # Try to break at logical points
                if ' and ' in context and context.count(' and ') == 1:
                    parts = context.split(' and ', 1)
                    if len(parts) == 2:
                        rewritten = f"{parts[0].strip()}. {parts[1].strip()}"
                        return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Broke long sentence into two shorter sentences'
                elif ', which ' in context.lower():
                    rewritten = re.sub(r',\s*which\s+', '. This ', context, flags=re.IGNORECASE)
                    return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Converted relative clause to separate sentence'
        
        # Handle word choice issues
        if "vague" in feedback_lower or "unclear" in feedback_lower:
            vague_replacements = {
                "thing": "item/component/element",
                "stuff": "materials/items/content", 
                "good": "effective/reliable/high-quality",
                "bad": "ineffective/unreliable/poor-quality",
                "big": "large/significant/substantial",
                "small": "minor/compact/limited"
            }
            
            for vague, specific in vague_replacements.items():
                if vague in context.lower():
                    return f'SUGGESTION: Replace "{vague}" with more specific terms like: {specific}\nCONTEXT: "{context}"'
        
        # Handle key capitalization issues
        if "capitalize key names" in feedback_lower and context:
            # Extract the key name that needs to be capitalized
            key_pattern = r"capitalize key names:\s*['\"](\w+)['\"]"
            key_match = re.search(key_pattern, feedback, re.IGNORECASE)
            if key_match:
                key_to_capitalize = key_match.group(1)
                # Create corrected version with proper capitalization
                corrected_text = re.sub(rf'\b{key_to_capitalize.lower()}\b', key_to_capitalize, context, flags=re.IGNORECASE)
                return f'CORRECTED TEXT: "{corrected_text}"\nCHANGE MADE: Capitalized "{key_to_capitalize}" when referring to the key name'
        
        # Handle tense issues
        if "tense" in feedback_lower and context:
            # Try to convert to simple present
            if "will " in context.lower():
                rewritten = re.sub(r'\bwill\s+(\w+)', r'\1', context, flags=re.IGNORECASE)
                return f'CORRECTED TEXT: "{rewritten}"\nCHANGE MADE: Converted future tense to simple present'
        
        # Default: provide specific guidance based on what we can detect
        if context:
            word_count = len(context.split())
            if word_count > 25:
                return f'SUGGESTION: Break this {word_count}-word sentence into 2-3 shorter sentences for better readability.\nORIGINAL: "{context}"'
            elif any(word in context.lower() for word in ['can', 'could', 'would', 'should']):
                return f'SUGGESTION: Replace modal verbs with direct action language for clearer instructions.\nORIGINAL: "{context}"'
            else:
                return f'SUGGESTION: Rewrite for clarity and directness.\nORIGINAL: "{context}"'
        
        # Final fallback if no context available
        return f'SUGGESTION: {feedback.replace("Consider ", "").replace("consider ", "")} - Please provide the specific text for a detailed rewrite.'
    
    def _post_process_ai_response(self, ai_response: str, original_sentence: str, issue: str) -> str:
        """
        Post-process AI response to ensure it follows the exact required format.
        """
        try:
            # Clean up the response
            response = ai_response.strip()
            
            # Check if response already has the correct format
            if "CORRECTED TEXT:" in response and "CHANGE MADE:" in response:
                return response
            
            # Try to extract corrected text from various formats the AI might use
            corrected_text = original_sentence  # fallback
            change_made = "Applied requested fix"  # fallback
            
            # Look for common patterns
            patterns = [
                r'"([^"]+)"',  # Text in quotes
                r'REWRITTEN:\s*"([^"]+)"',
                r'CORRECTED:\s*"([^"]+)"',
                r'FIXED:\s*"([^"]+)"',
                r'SUGGESTION:\s*"([^"]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    corrected_text = match.group(1)
                    break
            
            # Look for change explanation
            change_patterns = [
                r'CHANGE MADE:\s*(.+?)(?:\n|$)',
                r'WHAT CHANGED:\s*(.+?)(?:\n|$)',
                r'FIXED:\s*(.+?)(?:\n|$)',
                r'CHANGED:\s*(.+?)(?:\n|$)'
            ]
            
            for pattern in change_patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    change_made = match.group(1).strip()
                    break
            
            # Force the exact format
            formatted_response = f'CORRECTED TEXT: "{corrected_text}"\nCHANGE MADE: {change_made}'
            
            return formatted_response
            
        except Exception as e:
            logger.warning(f"Post-processing failed: {str(e)}")
            # Return a minimal format if everything fails
            return f'CORRECTED TEXT: "{original_sentence}"\nCHANGE MADE: Applied requested fix'

    def _conjugate_third_person_singular(self, verb: str) -> str:
        """Properly conjugate a verb for third person singular (he/she/it)."""
        verb_lower = verb.lower()
        
        # Handle irregular verbs
        irregular_verbs = {
            'have': 'has',
            'be': 'is', 
            'do': 'does',
            'go': 'goes'
        }
        
        if verb_lower in irregular_verbs:
            return irregular_verbs[verb_lower]
        
        # Apply standard conjugation rules
        if verb_lower.endswith('s') or verb_lower.endswith('ss') or verb_lower.endswith('sh') or verb_lower.endswith('ch') or verb_lower.endswith('x') or verb_lower.endswith('z'):
            return verb + 'es'
        elif verb_lower.endswith('y') and len(verb) > 1 and verb[-2] not in 'aeiou':
            return verb[:-1] + 'ies'
        elif verb_lower.endswith('o') and len(verb) > 1 and verb[-2] not in 'aeiou':
            return verb + 'es'
        else:
            return verb + 's'

# Global instance for easy use
ai_engine = EnhancedAISuggestionEngine()

def get_enhanced_ai_suggestion(feedback_text: str, sentence_context: str = "",
                             document_type: str = "general", 
                             writing_goals: List[str] = None) -> Dict[str, Any]:
    """
    Convenience function to get enhanced AI suggestions.
    
    Args:
        feedback_text: The feedback or issue identified
        sentence_context: The actual sentence or text
        document_type: Type of document (technical, marketing, academic, etc.)
        writing_goals: List of writing goals (clarity, conciseness, etc.)
    
    Returns:
        Dictionary with suggestion and metadata
    """
    return ai_engine.generate_contextual_suggestion(
        feedback_text, sentence_context, document_type, writing_goals
    )

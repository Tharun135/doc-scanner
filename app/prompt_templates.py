"""
Advanced prompt engineering templates for different types of writing feedback.
This module provides specialized prompts for various writing issues and document types.
"""

from typing import Dict, List, Optional
from enum import Enum

class DocumentType(Enum):
    TECHNICAL = "technical"
    ACADEMIC = "academic"
    BUSINESS = "business"
    MARKETING = "marketing"
    CREATIVE = "creative"
    GENERAL = "general"

class FeedbackType(Enum):
    GRAMMAR = "grammar"
    STYLE = "style"
    CLARITY = "clarity"
    STRUCTURE = "structure"
    TONE = "tone"
    CONCISENESS = "conciseness"

class AdvancedPromptTemplates:
    """
    Advanced prompt templates for different types of writing feedback.
    """
    
    @staticmethod
    def get_system_prompt(document_type: DocumentType) -> str:
        """Get specialized system prompt based on document type."""
        
        base_analytical_approach = """

CRITICAL OUTPUT FORMAT:
You MUST output EXACTLY this format, nothing else:

CORRECTED TEXT: "[the exact sentence with the specific fix applied]"
CHANGE MADE: [brief description of what was changed]

RULES:
1. CORRECTED TEXT should be the complete, fixed sentence
2. CHANGE MADE should describe the specific improvement made (e.g., "Changed passive voice to active", "Removed redundant word", "Fixed subject-verb agreement")
3. Do NOT restate the problem or explain why it's important
4. Do NOT provide general writing advice
5. Use the EXACT format shown above

Example:
ISSUE: "Passive voice detected"
ORIGINAL: "Press the enter key to continue"
CORRECTED TEXT: "Press the Enter key to continue"
CHANGE MADE: Capitalized "enter" to "Enter"

Be surgical and precise. Fix only what is requested."""

        system_prompts = {
            DocumentType.TECHNICAL: f"""You are a precision technical text editor. You fix specific technical writing issues by applying the exact correction requested. You provide the corrected text with the precise change made.{base_analytical_approach}

FOCUS: Apply the exact technical writing fix requested.""",
            
            DocumentType.ACADEMIC: f"""You are a precision academic text editor. You fix specific academic writing issues by applying the exact correction requested. You provide the corrected text with the precise change made.{base_analytical_approach}

FOCUS: Apply the exact academic writing fix requested.""",
            
            DocumentType.BUSINESS: f"""You are a precision business text editor. You fix specific business writing issues by applying the exact correction requested. You provide the corrected text with the precise change made.{base_analytical_approach}

FOCUS: Apply the exact business writing fix requested.""",
            
            DocumentType.MARKETING: f"""You are a precision marketing text editor. You fix specific marketing copy issues by applying the exact correction requested. You provide the corrected text with the precise change made.{base_analytical_approach}

FOCUS: Apply the exact marketing copy fix requested.""",
            
            DocumentType.CREATIVE: f"""You are a precision creative text editor. You fix specific creative writing issues by applying the exact correction requested. You provide the corrected text with the precise change made.{base_analytical_approach}

FOCUS: Apply the exact creative writing fix requested.""",
            
            DocumentType.GENERAL: f"""You are a precision text editor. You fix specific writing issues by applying the exact correction requested. You provide the corrected text with the precise change made.{base_analytical_approach}

FOCUS: Apply the exact writing fix requested."""
        }
        
        return system_prompts.get(document_type, system_prompts[DocumentType.GENERAL])
    
    @staticmethod
    def get_feedback_prompt(feedback_type: FeedbackType, issue_description: str, 
                          sentence_context: str, document_type: DocumentType) -> str:
        """Get specialized prompt for specific feedback types."""
        
        base_context = f"""
ORIGINAL SENTENCE: "{sentence_context}"
SPECIFIC ISSUE: {issue_description}

CRITICAL: YOU MUST OUTPUT EXACTLY THIS FORMAT:
CORRECTED TEXT: "[the exact corrected sentence]"
CHANGE MADE: [what specific change was made]

DO NOT OUTPUT ANYTHING ELSE. NO EXPLANATIONS. NO ADDITIONAL ADVICE.
"""
        
        feedback_prompts = {
            FeedbackType.GRAMMAR: f"""{base_context}

TASK: Fix the grammar issue in the sentence.

EXAMPLES:
ORIGINAL: "The report was completed by the team"
ISSUE: "Convert passive voice to active voice"
CORRECTED TEXT: "The team completed the report"
CHANGE MADE: Changed passive voice to active voice

ORIGINAL: "The students can submit their assignments"
ISSUE: "Replace 'can' with better alternative"
CORRECTED TEXT: "The students may submit their assignments"
CHANGE MADE: Replaced "can" with "may"

YOU MUST USE EXACTLY THIS FORMAT:
CORRECTED TEXT: "[exact sentence with the fix applied]"
CHANGE MADE: [brief description of what changed]""",

            FeedbackType.STYLE: f"""{base_context}

TASK: Fix the style issue in the sentence.

EXAMPLES:
ORIGINAL: "It is important to note that we should consider implementing this feature"
ISSUE: "Remove unnecessary words"
CORRECTED TEXT: "We should implement this feature"
CHANGE MADE: Removed unnecessary words "It is important to note that" and "consider"

ORIGINAL: "The thing is that users can access the system"
ISSUE: "Remove filler words"
CORRECTED TEXT: "Users can access the system"
CHANGE MADE: Removed filler phrase "The thing is that"

YOU MUST USE EXACTLY THIS FORMAT:
CORRECTED TEXT: "[exact sentence with the fix applied]"
CHANGE MADE: [brief description of what changed]""",

            FeedbackType.CLARITY: f"""{base_context}

TASK: Fix the clarity issue in the sentence.

EXAMPLES:
ORIGINAL: "The system processes it automatically"
ISSUE: "Clarify ambiguous pronoun 'it'"
CORRECTED TEXT: "The system processes user data automatically"
CHANGE MADE: Replaced ambiguous pronoun "it" with "user data"

ORIGINAL: "Click the enter key"
ISSUE: "Capitalize key names: 'Enter'"
CORRECTED TEXT: "Click the Enter key"
CHANGE MADE: Capitalized "enter" to "Enter"

YOU MUST USE EXACTLY THIS FORMAT:
CORRECTED TEXT: "[exact sentence with the fix applied]"
CHANGE MADE: [brief description of what changed]""",

            FeedbackType.STRUCTURE: f"""{base_context}

TASK: Fix the structural issue in the sentence.

EXAMPLES:
ORIGINAL: "After installation, first download the software"
ISSUE: "Fix logical order"
CORRECTED TEXT: "First download the software, then install it"
CHANGE MADE: Reordered steps to follow logical sequence

ORIGINAL: "The API, which was developed last year, handles requests"
ISSUE: "Simplify complex structure"
CORRECTED TEXT: "The API handles requests. It was developed last year."
CHANGE MADE: Split complex sentence into two simpler sentences

YOU MUST USE EXACTLY THIS FORMAT:
CORRECTED TEXT: "[exact sentence with the fix applied]"
CHANGE MADE: [brief description of what changed]""",

            FeedbackType.TONE: f"""{base_context}

TASK: Fix the tone issue in the sentence.

EXAMPLES:
ORIGINAL: "This is totally broken and we gotta fix it now"
ISSUE: "Make more professional"
CORRECTED TEXT: "This requires immediate attention and resolution"
CHANGE MADE: Made language more professional and formal

ORIGINAL: "The utilization of this methodology facilitates optimization"
ISSUE: "Make less formal"
CORRECTED TEXT: "This method helps improve results"
CHANGE MADE: Replaced formal words with simpler alternatives

YOU MUST USE EXACTLY THIS FORMAT:
CORRECTED TEXT: "[exact sentence with the fix applied]"
CHANGE MADE: [brief description of what changed]""",

            FeedbackType.CONCISENESS: f"""{base_context}

TASK: Fix the wordiness issue in the sentence.

EXAMPLES:
ORIGINAL: "In order to be able to access the system successfully"
ISSUE: "Remove redundant words"
CORRECTED TEXT: "To access the system"
CHANGE MADE: Removed redundant words "in order", "be able to", and "successfully"

ORIGINAL: "The fact of the matter is that we need to make improvements"
ISSUE: "Eliminate unnecessary phrases"
CORRECTED TEXT: "We need to make improvements"
CHANGE MADE: Removed unnecessary phrase "The fact of the matter is that"

YOU MUST USE EXACTLY THIS FORMAT:
CORRECTED TEXT: "[exact sentence with the fix applied]"
CHANGE MADE: [brief description of what changed]"""
        }
        
        return feedback_prompts.get(feedback_type, feedback_prompts[FeedbackType.CLARITY])
    
    @staticmethod
    def get_few_shot_examples(feedback_type: FeedbackType, document_type: DocumentType) -> str:
        """Get relevant few-shot examples for better AI performance."""
        
        examples = {
            (FeedbackType.CLARITY, DocumentType.TECHNICAL): """
EXAMPLE 1:
ISSUE: "Capitalize key names: 'Enter'"
ORIGINAL: "Press the enter key to continue"
CORRECTED TEXT: "Press the Enter key to continue"
CHANGE MADE: Capitalized "enter" to "Enter"

EXAMPLE 2:
ISSUE: "Define acronym API"
ORIGINAL: "Use the API to fetch data"
CORRECTED TEXT: "Use the API (Application Programming Interface) to fetch data"
CHANGE MADE: Added definition for acronym API""",

            (FeedbackType.CONCISENESS, DocumentType.BUSINESS): """
EXAMPLE 1:
ISSUE: "Remove redundant phrase 'in order to'"
ORIGINAL: "In order to improve efficiency, we need to streamline processes"
CORRECTED TEXT: "To improve efficiency, we need to streamline processes"
CHANGE MADE: Removed redundant phrase "in order"

EXAMPLE 2:
ISSUE: "Eliminate filler words"
ORIGINAL: "We basically need to sort of implement this solution"
CORRECTED TEXT: "We need to implement this solution"
CHANGE MADE: Removed filler words "basically" and "sort of"""
        }
        
        key = (feedback_type, document_type)
        if key in examples:
            return f"\nHERE ARE EXAMPLES OF GOOD IMPROVEMENTS:\n{examples[key]}\n"
        
        # Return general examples if no specific match
        return f"\nEXAMPLE FORMAT:\nISSUE: [The specific problem to fix]\nORIGINAL: [Original text]\nCORRECTED TEXT: [Fixed text]\nCHANGE MADE: [What was changed]\n\nFOCUS: Make ONLY the change specified in the issue.\n"
    
    @staticmethod
    def build_complete_prompt(feedback_type: FeedbackType, issue_description: str,
                            sentence_context: str, document_type: DocumentType,
                            writing_goals: List[str] = None) -> Dict[str, str]:
        """Build a complete, optimized prompt with system message and user message."""
        
        writing_goals = writing_goals or ["clarity", "conciseness"]
        goals_text = ", ".join(writing_goals)
        
        system_prompt = AdvancedPromptTemplates.get_system_prompt(document_type)
        few_shot_examples = AdvancedPromptTemplates.get_few_shot_examples(feedback_type, document_type)
        feedback_prompt = AdvancedPromptTemplates.get_feedback_prompt(
            feedback_type, issue_description, sentence_context, document_type
        )
        
        user_prompt = f"""
WRITING PROBLEM TO FIX: {issue_description}
ORIGINAL TEXT: "{sentence_context}"

TASK: Fix ONLY the writing problem specified above. Make no other changes.

The "WRITING PROBLEM" describes what's wrong with the text (e.g., "passive voice detected", "redundant words", "unclear pronoun reference"). Your job is to fix that specific problem.

MANDATORY OUTPUT FORMAT (use exactly this):
CORRECTED TEXT: "[exact sentence with only the specified fix]"
CHANGE MADE: [what was changed]

{few_shot_examples}

CRITICAL REMINDER:
- Fix ONLY the writing problem mentioned
- Use EXACTLY the format shown above
- Do not add explanations or extra advice
- Be precise and surgical

NOW APPLY THE FIX:"""
        
        return {
            "system": system_prompt,
            "user": user_prompt.strip()
        }

def classify_feedback_type(feedback_text: str) -> FeedbackType:
    """Automatically classify the type of feedback based on keywords."""
    
    feedback_lower = feedback_text.lower()
    
    # Grammar keywords
    if any(keyword in feedback_lower for keyword in 
           ['grammar', 'subject-verb', 'tense', 'punctuation', 'comma', 'apostrophe', 'syntax']):
        return FeedbackType.GRAMMAR
    
    # Style keywords
    elif any(keyword in feedback_lower for keyword in 
             ['style', 'word choice', 'flow', 'rhythm', 'awkward', 'clunky']):
        return FeedbackType.STYLE
    
    # Clarity keywords
    elif any(keyword in feedback_lower for keyword in 
             ['unclear', 'confusing', 'ambiguous', 'vague', 'hard to understand']):
        return FeedbackType.CLARITY
    
    # Structure keywords
    elif any(keyword in feedback_lower for keyword in 
             ['structure', 'organization', 'transition', 'logical', 'flow', 'sequence']):
        return FeedbackType.STRUCTURE
    
    # Tone keywords
    elif any(keyword in feedback_lower for keyword in 
             ['tone', 'formal', 'informal', 'voice', 'audience', 'professional']):
        return FeedbackType.TONE
    
    # Conciseness keywords
    elif any(keyword in feedback_lower for keyword in 
             ['long', 'wordy', 'verbose', 'concise', 'redundant', 'repetitive']):
        return FeedbackType.CONCISENESS
    
    # Default to clarity if no specific match
    return FeedbackType.CLARITY

def get_document_type_from_string(doc_type_str: str) -> DocumentType:
    """Convert string to DocumentType enum."""
    try:
        return DocumentType(doc_type_str.lower())
    except ValueError:
        return DocumentType.GENERAL

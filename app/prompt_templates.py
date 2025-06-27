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
        
        system_prompts = {
            DocumentType.TECHNICAL: """You are an expert technical writing editor with 15+ years of experience. You specialize in making complex technical content clear, accurate, and accessible. You understand software documentation, API guides, user manuals, and engineering specifications. Focus on precision, clarity, and user-friendliness.""",
            
            DocumentType.ACADEMIC: """You are a distinguished academic writing consultant with expertise in scholarly communication. You help researchers, students, and academics improve their papers, theses, and publications. Focus on argument strength, evidence support, formal tone, and academic conventions.""",
            
            DocumentType.BUSINESS: """You are a professional business communication expert. You specialize in corporate writing including reports, proposals, emails, and presentations. Focus on professionalism, clarity, persuasiveness, and executive-level communication.""",
            
            DocumentType.MARKETING: """You are a marketing copywriting specialist with expertise in persuasive, engaging content. You understand brand voice, audience psychology, and conversion-focused writing. Focus on engagement, clarity, and compelling calls-to-action.""",
            
            DocumentType.CREATIVE: """You are a creative writing mentor with expertise in storytelling, narrative flow, and engaging prose. You help with fiction, creative nonfiction, and artistic expression. Focus on voice, flow, imagery, and reader engagement.""",
            
            DocumentType.GENERAL: """You are a versatile writing coach with broad expertise across multiple writing contexts. You provide clear, actionable feedback to improve any type of writing. Focus on fundamental principles of clear, effective communication."""
        }
        
        return system_prompts.get(document_type, system_prompts[DocumentType.GENERAL])
    
    @staticmethod
    def get_feedback_prompt(feedback_type: FeedbackType, issue_description: str, 
                          sentence_context: str, document_type: DocumentType) -> str:
        """Get specialized prompt for specific feedback types."""
        
        base_context = f"""
DOCUMENT TYPE: {document_type.value.title()}
SENTENCE/TEXT: "{sentence_context}"
ISSUE IDENTIFIED: {issue_description}
"""
        
        feedback_prompts = {
            FeedbackType.GRAMMAR: f"""{base_context}

TASK: Fix the grammatical issue and explain the rule.

Provide your response in this format:
PROBLEM: [Specific grammatical error]
CORRECTION: [Exact corrected text]
RULE: [Grammar rule explanation]
EXAMPLE: [Additional example of correct usage]

Focus on standard grammar rules, proper punctuation, and sentence structure.""",

            FeedbackType.STYLE: f"""{base_context}

TASK: Improve the writing style while maintaining the original meaning.

Provide your response in this format:
STYLE ISSUE: [What makes this awkward or unclear]
IMPROVED VERSION: [Rewritten text with better style]
EXPLANATION: [Why this version is better]
PRINCIPLE: [Style principle being applied]

Focus on flow, word choice, rhythm, and readability.""",

            FeedbackType.CLARITY: f"""{base_context}

TASK: Make this text clearer and more understandable.

Provide your response in this format:
CLARITY PROBLEM: [What makes this confusing]
CLEARER VERSION: [Rewritten for maximum clarity]
EXPLANATION: [How this improves understanding]
AUDIENCE BENEFIT: [Why readers will appreciate this change]

Focus on removing ambiguity, simplifying complex ideas, and improving comprehension.""",

            FeedbackType.STRUCTURE: f"""{base_context}

TASK: Improve the logical structure and organization.

Provide your response in this format:
STRUCTURAL ISSUE: [Problems with organization or flow]
RESTRUCTURED VERSION: [Better organized text]
LOGIC: [How the new structure improves logic]
FLOW: [How this helps reader follow the argument]

Focus on logical progression, transitions, and information hierarchy.""",

            FeedbackType.TONE: f"""{base_context}

TASK: Adjust the tone to be more appropriate for the context and audience.

Provide your response in this format:
TONE ISSUE: [Current tone problems]
ADJUSTED VERSION: [Text with improved tone]
TONE ACHIEVED: [Description of the new tone]
AUDIENCE FIT: [Why this tone works better for the intended audience]

Focus on formality level, warmth, authority, and audience appropriateness.""",

            FeedbackType.CONCISENESS: f"""{base_context}

TASK: Make this text more concise without losing important information.

Provide your response in this format:
WORDINESS PROBLEM: [What makes this unnecessarily long]
CONCISE VERSION: [Shortened text maintaining meaning]
WORDS SAVED: [Original word count → New word count]
IMPACT: [How conciseness improves the text]

Focus on eliminating redundancy, unnecessary words, and verbose constructions."""
        }
        
        return feedback_prompts.get(feedback_type, feedback_prompts[FeedbackType.CLARITY])
    
    @staticmethod
    def get_few_shot_examples(feedback_type: FeedbackType, document_type: DocumentType) -> str:
        """Get relevant few-shot examples for better AI performance."""
        
        examples = {
            (FeedbackType.CLARITY, DocumentType.TECHNICAL): """
EXAMPLE 1:
ISSUE: Technical jargon without explanation
ORIGINAL: "The API endpoint utilizes RESTful architecture with JWT authentication."
IMPROVED: "The API endpoint uses RESTful architecture (a standard web service design) with JWT authentication (a secure login method)."
EXPLANATION: Added brief explanations for technical terms to help non-technical readers.

EXAMPLE 2:
ISSUE: Complex sentence with multiple concepts
ORIGINAL: "When implementing the caching mechanism, ensure that the TTL values are configured appropriately to balance performance gains with data freshness requirements."
IMPROVED: "When implementing caching, set TTL (time-to-live) values carefully. Balance faster performance with up-to-date data."
EXPLANATION: Broke complex sentence into shorter ones and defined the acronym.""",

            (FeedbackType.CONCISENESS, DocumentType.BUSINESS): """
EXAMPLE 1:
ISSUE: Unnecessary business jargon
ORIGINAL: "In order to optimize our operational efficiency and maximize our ROI, we should leverage our core competencies."
IMPROVED: "To work more efficiently and increase profits, we should use our strengths."
WORDS SAVED: 19 → 13 words
EXPLANATION: Replaced jargon with plain language while keeping the meaning.

EXAMPLE 2:
ISSUE: Redundant phrases
ORIGINAL: "The end result of this analysis shows that we need to make improvements to our customer service."
IMPROVED: "This analysis shows we need better customer service."
WORDS SAVED: 16 → 9 words
EXPLANATION: Removed redundant "end result" and simplified the conclusion."""
        }
        
        key = (feedback_type, document_type)
        if key in examples:
            return f"\nHERE ARE EXAMPLES OF GOOD IMPROVEMENTS:\n{examples[key]}\n"
        
        # Return general examples if no specific match
        return f"\nFOLLOW THESE PRINCIPLES:\n- Be specific and actionable\n- Maintain the original meaning\n- Consider the {document_type.value} audience\n- Focus on {feedback_type.value} improvements\n"
    
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
WRITING GOALS: {goals_text}

{few_shot_examples}

{feedback_prompt}

Remember: Provide specific, actionable feedback that aligns with {document_type.value} writing standards and helps achieve {goals_text}.
"""
        
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

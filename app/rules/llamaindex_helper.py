"""
LlamaIndex Helper for Local AI Processing
Provides unlimited AI suggestions without cloud dependency or quotas.
"""

import logging
import os
from typing import List, Dict, Any, Optional

try:
    from llama_index.core import VectorStoreIndex, Document, Settings
    from llama_index.core.node_parser import SentenceSplitter
    from llama_index.llms.ollama import Ollama
    LLAMAINDEX_AVAILABLE = True
except ImportError as e:
    LLAMAINDEX_AVAILABLE = False
    logging.warning(f"LlamaIndex not available: {e}")
    
    # Create dummy classes for when LlamaIndex is not available
    class Document:
        def __init__(self, text: str, metadata: Dict = None):
            self.text = text
            self.metadata = metadata or {}
    
    class VectorStoreIndex:
        @classmethod
        def from_documents(cls, documents):
            return cls()
        
        def as_query_engine(self, similarity_top_k=3):
            return DummyQueryEngine()
    
    class DummyQueryEngine:
        def query(self, query_str):
            return "LlamaIndex not available - using fallback response"

logger = logging.getLogger(__name__)

class LlamaIndexAIEngine:
    """
    Local AI engine using LlamaIndex with Ollama for unlimited suggestions.
    No cloud dependencies, no quotas, completely local processing.
    """
    
    def __init__(self, model_name: str = "llama3.2:3b"):
        self.model_name = model_name
        self.index = None
        self.query_engine = None
        self.initialized = False
        
        if not LLAMAINDEX_AVAILABLE:
            logger.error("LlamaIndex dependencies not available. Please install: pip install llama-index")
            return
            
        self._initialize_ai_engine()
    
    def _initialize_ai_engine(self):
        """Initialize the local AI engine with LlamaIndex and Ollama."""
        try:
            # Configure LlamaIndex settings - using simple local setup
            Settings.llm = Ollama(model=self.model_name, request_timeout=60.0)
            Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
            
            # Load writing guidelines and rules into the index
            documents = self._load_writing_guidelines()
            self.index = VectorStoreIndex.from_documents(documents)
            
            # Create query engine
            self.query_engine = self.index.as_query_engine(similarity_top_k=3)
            
            self.initialized = True
            logger.info(f"LlamaIndex AI engine initialized successfully with model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LlamaIndex AI engine: {e}")
            self.initialized = False
    
    def _load_writing_guidelines(self) -> List[Document]:
        """Load writing guidelines and rules into LlamaIndex documents."""
        documents = []
        
        # Grammar guidelines
        grammar_guidelines = """
        GRAMMAR AND SYNTAX GUIDELINES:
        
        1. Use active voice instead of passive voice for clarity and directness.
        2. Ensure subject-verb agreement in all sentences.
        3. Use correct tense consistently throughout the document.
        4. Place modifiers close to the words they modify to avoid ambiguity.
        5. Use parallel structure in lists and series.
        6. Avoid sentence fragments and run-on sentences.
        7. Use proper pronoun references and avoid unclear antecedents.
        """
        
        # Clarity guidelines
        clarity_guidelines = """
        CLARITY AND CONCISENESS GUIDELINES:
        
        1. Use simple, clear language instead of complex jargon.
        2. Eliminate unnecessary words and redundant phrases.
        3. Write short, focused sentences (aim for 15-20 words).
        4. Use specific, concrete terms instead of vague language.
        5. Avoid filler words like "very", "quite", "really".
        6. Replace complex words with simpler alternatives when possible.
        7. Define technical terms when first introduced.
        """
        
        # Formatting guidelines
        formatting_guidelines = """
        FORMATTING AND STRUCTURE GUIDELINES:
        
        1. Use consistent heading hierarchy (H1, H2, H3).
        2. Format lists consistently with proper bullets or numbers.
        3. Use code formatting for technical elements.
        4. Maintain consistent spacing and indentation.
        5. Use proper table formatting with clear headers.
        6. Include meaningful section breaks and white space.
        7. Format UI elements consistently (buttons, menus, etc.).
        """
        
        # Tone guidelines
        tone_guidelines = """
        TONE AND VOICE GUIDELINES:
        
        1. Use appropriate tone for the target audience.
        2. Prefer imperative mood for instructions.
        3. Use inclusive, respectful language.
        4. Maintain consistent voice throughout the document.
        5. Avoid overly casual or overly formal language.
        6. Use positive language instead of negative when possible.
        """
        
        # Terminology guidelines
        terminology_guidelines = """
        TERMINOLOGY GUIDELINES:
        
        1. Use consistent terminology throughout the document.
        2. Capitalize product names and proper nouns correctly.
        3. Maintain a glossary of key terms.
        4. Use standard industry terminology.
        5. Avoid creating new terms when standard ones exist.
        6. Define acronyms on first use.
        """
        
        # Accessibility guidelines
        accessibility_guidelines = """
        ACCESSIBILITY GUIDELINES:
        
        1. Provide meaningful alt text for images.
        2. Ensure sufficient color contrast for text.
        3. Use descriptive link text instead of "click here".
        4. Structure content for screen readers.
        5. Use semantic HTML elements properly.
        6. Provide captions for audio/video content.
        7. Design for keyboard navigation compatibility.
        """
        
        # Punctuation guidelines
        punctuation_guidelines = """
        PUNCTUATION GUIDELINES:
        
        1. Use commas correctly in lists and compound sentences.
        2. Use colons and semicolons appropriately.
        3. Use quotation marks consistently for quoted text.
        4. Place periods and commas inside quotation marks.
        5. Use hyphens for compound modifiers.
        6. Use em dashes for breaks in thought.
        7. Avoid excessive exclamation points.
        """
        
        # Capitalization guidelines
        capitalization_guidelines = """
        CAPITALIZATION GUIDELINES:
        
        1. Use sentence case for most headings and UI elements.
        2. Use title case only when specifically required.
        3. Capitalize proper nouns consistently.
        4. Follow standard capitalization rules for acronyms.
        5. Use consistent capitalization for product names.
        6. Capitalize the first word after colons in formal writing.
        """
        
        # Create documents from guidelines
        guidelines = [
            ("Grammar and Syntax", grammar_guidelines),
            ("Clarity and Conciseness", clarity_guidelines),
            ("Formatting and Structure", formatting_guidelines),
            ("Tone and Voice", tone_guidelines),
            ("Terminology", terminology_guidelines),
            ("Accessibility", accessibility_guidelines),
            ("Punctuation", punctuation_guidelines),
            ("Capitalization", capitalization_guidelines)
        ]
        
        for title, content in guidelines:
            doc = Document(text=content, metadata={"category": title})
            documents.append(doc)
        
        return documents
    
    def get_ai_suggestion(self, issue_text: str, sentence_context: str, category: str = "general") -> Dict[str, Any]:
        """
        Get AI-powered suggestion for writing improvement.
        
        Args:
            issue_text: The specific issue or feedback text
            sentence_context: The sentence or context where the issue occurs
            category: The rule category (grammar, clarity, etc.)
        
        Returns:
            Dictionary with suggestion details
        """
        if not self.initialized:
            return self._get_fallback_suggestion(issue_text, sentence_context, category)
        
        try:
            # Construct query for the AI
            query = f"""
            Writing Issue: {issue_text}
            
            Original Sentence: "{sentence_context}"
            
            Category: {category}
            
            Please provide:
            1. A clear explanation of the issue
            2. 2-3 alternative ways to rewrite the sentence
            3. The reasoning behind the improvements
            4. A brief tip for avoiding this issue in the future
            
            Format your response as:
            EXPLANATION: [explanation]
            ALTERNATIVES:
            1. [option 1]
            2. [option 2]
            3. [option 3]
            REASONING: [reasoning]
            TIP: [tip]
            """
            
            # Query the AI engine
            response = self.query_engine.query(query)
            
            return {
                "suggestion": str(response),
                "confidence": 0.9,
                "source": "llama_local_ai",
                "category": category,
                "alternatives": self._extract_alternatives(str(response)),
                "explanation": self._extract_explanation(str(response))
            }
            
        except Exception as e:
            logger.error(f"Error getting AI suggestion: {e}")
            return self._get_fallback_suggestion(issue_text, sentence_context, category)
    
    def _extract_alternatives(self, response: str) -> List[str]:
        """Extract alternative suggestions from AI response."""
        alternatives = []
        lines = response.split('\n')
        in_alternatives = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('ALTERNATIVES:'):
                in_alternatives = True
                continue
            elif line.startswith('REASONING:') or line.startswith('TIP:'):
                in_alternatives = False
                continue
            elif in_alternatives and line and (line.startswith(('1.', '2.', '3.', '-', '•'))):
                # Extract the alternative text
                alt_text = line.split('.', 1)[-1].strip() if '.' in line else line[1:].strip()
                if alt_text:
                    alternatives.append(alt_text)
        
        return alternatives
    
    def _extract_explanation(self, response: str) -> str:
        """Extract explanation from AI response."""
        lines = response.split('\n')
        for line in lines:
            if line.strip().startswith('EXPLANATION:'):
                return line.replace('EXPLANATION:', '').strip()
        return "AI-powered suggestion for improving writing quality."
    
    def _get_fallback_suggestion(self, issue_text: str, sentence_context: str, category: str) -> Dict[str, Any]:
        """Provide fallback suggestion when AI is not available."""
        fallback_suggestions = {
            "grammar": "Consider revising for better grammar and sentence structure.",
            "clarity": "Try to make this sentence clearer and more concise.",
            "formatting": "Check formatting and structure for consistency.",
            "tone": "Consider adjusting the tone for your target audience.",
            "terminology": "Ensure consistent use of terminology.",
            "accessibility": "Review for accessibility best practices.",
            "punctuation": "Check punctuation usage and correctness.",
            "capitalization": "Verify capitalization follows style guidelines."
        }
        
        suggestion = fallback_suggestions.get(category, "Consider improving this text for better readability.")
        
        return {
            "suggestion": f"{suggestion} Original issue: {issue_text}",
            "confidence": 0.5,
            "source": "rule_based_fallback",
            "category": category,
            "alternatives": [],
            "explanation": suggestion
        }
    
    def is_available(self) -> bool:
        """Check if the AI engine is available and initialized."""
        return self.initialized and LLAMAINDEX_AVAILABLE

# Global AI engine instance
ai_engine = LlamaIndexAIEngine()

def get_ai_suggestion(issue_text: str, sentence_context: str, category: str = "general") -> Dict[str, Any]:
    """
    Global function to get AI suggestions.
    
    Args:
        issue_text: The specific issue or feedback text
        sentence_context: The sentence or context where the issue occurs
        category: The rule category
    
    Returns:
        Dictionary with suggestion details
    """
    return ai_engine.get_ai_suggestion(issue_text, sentence_context, category)

def is_ai_available() -> bool:
    """Check if AI engine is available."""
    return ai_engine.is_available()

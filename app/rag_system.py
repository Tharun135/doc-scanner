"""
RAG (Retrieval-Augmented Generation) system using Gemini and LangChain
for enhanced AI suggestions with document context.
"""

import os
import logging
import tempfile
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

try:
    import google.generativeai as genai
    from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import Chroma
    from langchain.schema import Document
    from langchain.chains import RetrievalQA
    from langchain.prompts import PromptTemplate
    from langchain_community.document_loaders import TextLoader
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    logging.warning(f"LangChain/Gemini dependencies not available: {e}")
    LANGCHAIN_AVAILABLE = False

# Load environment variables from .env file (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not available - environment variables must be set manually")

logger = logging.getLogger(__name__)

class GeminiRAGSystem:
    """
    RAG system using Google Gemini for enhanced AI suggestions
    with document context retrieval.
    """
    
    def __init__(self):
        self.llm = None
        self.embeddings = None
        self.vectorstore = None
        self.retrieval_qa = None
        self.is_initialized = False
        self.temp_dir = tempfile.mkdtemp()
        
        if LANGCHAIN_AVAILABLE:
            self._initialize_gemini()
        else:
            logger.warning("RAG system disabled - LangChain dependencies not installed")
    
    def _initialize_gemini(self):
        """Initialize Gemini client and embeddings."""
        try:
            # Get API key from environment
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                logger.warning("No Google API key found. Set GOOGLE_API_KEY environment variable.")
                logger.info("Get API key from: https://makersuite.google.com/app/apikey")
                return
            
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Initialize LangChain components
            self.llm = GoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.1,
                max_output_tokens=500
            )
            
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=api_key
            )
            
            # Initialize empty vector store
            self.vectorstore = Chroma(
                embedding_function=self.embeddings,
                persist_directory=os.path.join(self.temp_dir, "chroma_db")
            )
            
            self.is_initialized = True
            logger.info("Gemini RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini RAG system: {e}")
            self.is_initialized = False
    
    def add_writing_guidelines(self, guidelines_text: str = None):
        """Add writing guidelines and style rules to the knowledge base."""
        if not self.is_initialized:
            return False
            
        try:
            # Default writing guidelines if none provided
            if not guidelines_text:
                guidelines_text = self._get_default_writing_guidelines()
            
            # Split guidelines into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=50,
                separators=["\n\n", "\n", ". ", " "]
            )
            
            chunks = text_splitter.split_text(guidelines_text)
            
            # Create documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": "writing_guidelines",
                        "chunk_id": i,
                        "type": "guideline",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                documents.append(doc)
            
            # Add to vector store
            self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} writing guideline chunks to knowledge base")
            
            # Initialize retrieval QA chain
            self._setup_retrieval_chain()
            return True
            
        except Exception as e:
            logger.error(f"Error adding writing guidelines: {e}")
            return False
    
    def add_document_context(self, document_content: str, document_type: str = "general"):
        """Add current document context to the knowledge base."""
        if not self.is_initialized:
            return False
            
        try:
            # Split document into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=800,
                chunk_overlap=100
            )
            
            chunks = text_splitter.split_text(document_content)
            
            # Create documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": "current_document",
                        "chunk_id": i,
                        "document_type": document_type,
                        "type": "context",
                        "timestamp": datetime.now().isoformat()
                    }
                )
                documents.append(doc)
            
            # Add to vector store
            self.vectorstore.add_documents(documents)
            logger.info(f"Added {len(documents)} document context chunks")
            
            # Refresh retrieval chain
            self._setup_retrieval_chain()
            return True
            
        except Exception as e:
            logger.error(f"Error adding document context: {e}")
            return False
    
    def _setup_retrieval_chain(self):
        """Set up the retrieval QA chain with custom prompt."""
        if not self.vectorstore:
            return
            
        try:
            # Concise, options-focused prompt template
            prompt_template = """
You are a writing assistant. For this writing issue, provide 2-3 brief, practical alternatives.

Context: {context}
Issue: {question}

Format your response EXACTLY like this:
OPTION 1: [One clear rewrite/fix]
OPTION 2: [Alternative rewrite/fix] 
OPTION 3: [Third alternative if applicable]
WHY: [One sentence explaining the improvement]

Keep each option under 15 words. Be direct and actionable."""

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "question"]
            )
            
            # Create retrieval QA chain
            self.retrieval_qa = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 4}
                ),
                chain_type_kwargs={"prompt": prompt},
                return_source_documents=True
            )
            
            logger.info("Retrieval QA chain set up successfully")
            
        except Exception as e:
            logger.error(f"Error setting up retrieval chain: {e}")
    
    def get_rag_suggestion(self, feedback_text: str, sentence_context: str = "", 
                          document_type: str = "general") -> Optional[Dict[str, Any]]:
        """Get RAG-enhanced suggestion for writing improvement."""
        if not self.is_initialized or not self.retrieval_qa:
            logger.warning("RAG system not properly initialized")
            return None
            
        try:
            # Format the query for better retrieval
            query = self._format_rag_query(feedback_text, sentence_context, document_type)
            
            # Get response from RAG chain
            result = self.retrieval_qa({"query": query})
            
            suggestion = result.get("result", "").strip()
            source_docs = result.get("source_documents", [])
            
            if not suggestion:
                return None
            
            # Extract relevant sources
            sources = []
            for doc in source_docs[:2]:  # Top 2 sources
                sources.append({
                    "content": doc.page_content[:100] + "...",
                    "type": doc.metadata.get("type", "unknown"),
                    "source": doc.metadata.get("source", "unknown")
                })
            
            return {
                "suggestion": suggestion,
                "confidence": "high",
                "method": "gemini_rag",
                "sources": sources,
                "context_used": {
                    "retrieval_docs": len(source_docs),
                    "document_type": document_type,
                    "query_type": "rag_enhanced"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting RAG suggestion: {e}")
            return None
    
    def _format_rag_query(self, feedback_text: str, sentence_context: str, document_type: str) -> str:
        """Format the query for optimal retrieval."""
        query_parts = []
        
        # Add the main issue
        query_parts.append(f"Writing issue: {feedback_text}")
        
        # Add context if available
        if sentence_context:
            query_parts.append(f"Sentence: '{sentence_context}'")
        
        # Add document type context
        query_parts.append(f"Document type: {document_type}")
        
        # Add specific improvement request
        query_parts.append("How to improve this writing issue?")
        
        return " | ".join(query_parts)
    
    def _get_default_writing_guidelines(self) -> str:
        """Get default writing guidelines for the knowledge base."""
        return """
        WRITING GUIDELINES AND BEST PRACTICES

        CLARITY AND CONCISENESS:
        - Use active voice instead of passive voice whenever possible
        - Keep sentences under 25 words for better readability
        - Avoid unnecessary words and redundant phrases
        - Use specific, concrete terms instead of vague language
        - Replace weak verbs with strong, action-oriented verbs

        SENTENCE STRUCTURE:
        - Vary sentence length and structure for better flow
        - Use parallel structure in lists and series
        - Place the main idea at the beginning of the sentence
        - Avoid run-on sentences and excessive subordinate clauses
        - Use transitional words to connect ideas smoothly

        WORD CHOICE:
        - Choose precise words over general terms
        - Avoid jargon unless writing for a technical audience
        - Use shorter, simpler words when they convey the same meaning
        - Prefer strong nouns and verbs over adjectives and adverbs
        - Be consistent with terminology throughout the document

        PASSIVE VOICE CORRECTION:
        - Change "The report was written by John" to "John wrote the report"
        - Change "Mistakes were made" to "We made mistakes"
        - Change "The decision will be made" to "Management will decide"

        MODAL VERBS:
        - Use "can" for ability and permission in most contexts
        - Use "may" only for formal permission or uncertainty
        - Use "should" for recommendations
        - Use "must" for requirements and obligations

        BACKUP VS BACK UP:
        - Use "backup" as a noun or adjective (backup files, backup plan)
        - Use "back up" as a verb (back up your files, back up the data)

        DOCUMENT-SPECIFIC GUIDELINES:

        TECHNICAL DOCUMENTS:
        - Define acronyms on first use
        - Use numbered lists for procedures
        - Include specific examples and code snippets
        - Maintain consistent formatting for code elements

        BUSINESS DOCUMENTS:
        - Use clear headings and bullet points
        - Include actionable recommendations
        - Specify deadlines and responsibilities
        - Use professional but accessible language

        ACADEMIC DOCUMENTS:
        - Support claims with evidence and citations
        - Use formal language and third person
        - Maintain objective tone
        - Structure arguments logically

        CREATIVE WRITING:
        - Use vivid, sensory details
        - Vary sentence rhythm and pace
        - Show rather than tell
        - Develop strong character voice

        COMMON IMPROVEMENTS:
        - Replace "there is/are" constructions with stronger verbs
        - Eliminate unnecessary prepositional phrases
        - Combine short, choppy sentences
        - Break up overly complex sentences
        - Use specific numbers instead of vague quantities
        - Replace weak intensifiers (very, really, quite) with precise words
        """
    
    def is_available(self) -> bool:
        """Check if RAG system is available and initialized."""
        return LANGCHAIN_AVAILABLE and self.is_initialized


# Global RAG system instance
rag_system = GeminiRAGSystem()

def get_rag_suggestion(feedback_text: str, sentence_context: str = "", 
                      document_type: str = "general", document_content: str = "") -> Optional[Dict[str, Any]]:
    """
    Get RAG-enhanced suggestion. This is the main function to call from other modules.
    """
    if not rag_system.is_available():
        return None
    
    # Add document context if provided
    if document_content:
        rag_system.add_document_context(document_content, document_type)
    
    # Ensure guidelines are loaded
    if not hasattr(rag_system, '_guidelines_loaded'):
        rag_system.add_writing_guidelines()
        rag_system._guidelines_loaded = True
    
    return rag_system.get_rag_suggestion(feedback_text, sentence_context, document_type)

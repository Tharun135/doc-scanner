"""
Shared spaCy utilities for all grammar rules.
This module provides a single, shared spaCy model instance to avoid memory issues.
"""

import spacy
import logging

logger = logging.getLogger(__name__)

# Global shared spaCy model instance
_nlp_model = None
_model_load_attempted = False

def get_nlp_model():
    """
    Get the shared spaCy model instance.
    Returns None if the model cannot be loaded.
    """
    global _nlp_model, _model_load_attempted
    
    if _model_load_attempted and _nlp_model is None:
        return None
        
    if _nlp_model is None:
        try:
            logger.info("Loading spaCy English model...")
            _nlp_model = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {e}")
            logger.warning("Some advanced grammar features may not work.")
            logger.info("To install spaCy model: python -m spacy download en_core_web_sm")
            _nlp_model = None
        finally:
            _model_load_attempted = True
    
    return _nlp_model

def process_text(text):
    """
    Process text with spaCy if available, otherwise return None.
    """
    nlp = get_nlp_model()
    if nlp:
        try:
            return nlp(text)
        except Exception as e:
            logger.warning(f"Error processing text with spaCy: {e}")
            return None
    return None

def is_spacy_available():
    """Check if spaCy is available and working."""
    return get_nlp_model() is not None

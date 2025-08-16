"""
Simplified RAG System - Fallback Version
Uses local knowledge base without vector embeddings for demonstration.
"""

import logging
import json
from typing import List, Dict, Any, Optional, Tuple
from .knowledge_base import WRITING_RULES_KNOWLEDGE_BASE
import re

logger = logging.getLogger(__name__)

class SimplifiedRAG:
    """
    Simplified RAG system that uses keyword matching instead of vector embeddings.
    This provides rule-based suggestions without requiring heavy dependencies.
    """
    
    def __init__(self):
        self.knowledge_base = WRITING_RULES_KNOWLEDGE_BASE
        self.initialized = True
        logger.info("Simplified RAG system initialized")
    
    def get_rule_based_suggestion(self, 
                                issue_text: str, 
                                sentence_context: str, 
                                category: str = "general") -> Dict[str, Any]:
        """
        Get a rule-based suggestion using keyword matching and pattern recognition.
        """
        
        try:
            # Find the most relevant rule
            relevant_rule = self._find_relevant_rule(issue_text, category)
            
            if relevant_rule:
                # Create a contextual suggestion based on the rule
                suggestion = self._create_contextual_suggestion(
                    relevant_rule, sentence_context, issue_text
                )
                
                return {
                    "suggestion": suggestion,
                    "confidence": 0.8,
                    "source": "simplified_rag",
                    "retrieved_rules": 1,
                    "rule_based": True,
                    "rule_title": relevant_rule.get("rule_title", "Unknown Rule")
                }
            else:
                return self._fallback_suggestion(issue_text, sentence_context, category)
                
        except Exception as e:
            logger.error(f"Error in simplified RAG suggestion: {e}")
            return self._fallback_suggestion(issue_text, sentence_context, category)
    
    def _find_relevant_rule(self, issue_text: str, category: str) -> Optional[Dict[str, Any]]:
        """Find the most relevant rule based on issue text and category."""
        
        issue_lower = issue_text.lower()
        
        # Look in the specific category first
        category_key = f"{category}_rules"
        if category_key in self.knowledge_base:
            for rule in self.knowledge_base[category_key]:
                # Check if issue pattern matches
                if rule["issue_pattern"].lower() in issue_lower:
                    return rule
                
                # Check keywords
                for keyword in rule["keywords"]:
                    if keyword.lower() in issue_lower:
                        return rule
        
        # If no match in specific category, search all categories
        for cat_key, rules in self.knowledge_base.items():
            for rule in rules:
                if rule["issue_pattern"].lower() in issue_lower:
                    return rule
                
                for keyword in rule["keywords"]:
                    if keyword.lower() in issue_lower:
                        return rule
        
        return None
    
    def _create_contextual_suggestion(self, 
                                    rule: Dict[str, Any], 
                                    sentence: str, 
                                    issue_text: str) -> str:
        """Create a contextual suggestion based on the rule and sentence."""
        
        suggestion_parts = []
        
        # Start with the issue description
        suggestion_parts.append(f"**Issue:** {rule['issue_description']}")
        
        # Add the solution
        suggestion_parts.append(f"**Solution:** {rule['solution']}")
        
        # Try to find a relevant example
        best_example = self._find_best_example(rule.get("examples", []), sentence)
        if best_example:
            suggestion_parts.append(f"**Example:**")
            suggestion_parts.append(f"❌ Wrong: \"{best_example['wrong']}\"")
            suggestion_parts.append(f"✅ Better: \"{best_example['right']}\"")
            suggestion_parts.append(f"💡 Why: {best_example['explanation']}")
        
        # Add severity context
        severity = rule.get("severity", "medium")
        if severity == "high":
            suggestion_parts.append("⚠️ **High Priority:** This significantly impacts readability.")
        elif severity == "low":
            suggestion_parts.append("ℹ️ **Low Priority:** This is a minor improvement.")
        
        return "\n\n".join(suggestion_parts)
    
    def _find_best_example(self, examples: List[Dict], sentence: str) -> Optional[Dict]:
        """Find the most relevant example based on sentence similarity."""
        
        if not examples:
            return None
        
        sentence_lower = sentence.lower()
        best_example = None
        best_score = 0
        
        for example in examples:
            # Score based on word overlap
            wrong_words = set(example["wrong"].lower().split())
            sentence_words = set(sentence_lower.split())
            overlap = len(wrong_words.intersection(sentence_words))
            
            if overlap > best_score:
                best_score = overlap
                best_example = example
        
        # Return the best example, or the first one if no good match
        return best_example if best_example else examples[0]
    
    def _fallback_suggestion(self, issue_text: str, sentence_context: str, category: str) -> Dict[str, Any]:
        """Fallback suggestion when no specific rule is found."""
        
        generic_suggestions = {
            "grammar": "Review this sentence for grammar and syntax. Consider checking subject-verb agreement, tense consistency, and sentence structure.",
            "clarity": "This sentence could be clearer. Try using simpler words, shorter sentences, or removing unnecessary phrases.",
            "punctuation": "Check the punctuation in this sentence. Ensure commas, periods, and other marks are used correctly.",
            "tone": "Consider adjusting the tone of this sentence to better match your target audience and purpose.",
            "formatting": "Review the formatting and structure of this content for consistency and readability.",
            "terminology": "Ensure technical terms are used consistently and defined appropriately for your audience.",
            "accessibility": "Consider making this content more accessible and inclusive for all readers.",
            "capitalization": "Check the capitalization in this sentence, including proper nouns and title formatting."
        }
        
        suggestion = generic_suggestions.get(category, f"Review this sentence for {category} improvements.")
        
        return {
            "suggestion": f"**{issue_text.title()}**\n\n{suggestion}\n\n**Sentence:** \"{sentence_context}\"",
            "confidence": 0.5,
            "source": "fallback",
            "retrieved_rules": 0,
            "rule_based": False
        }

# Global simplified RAG instance
simplified_rag = SimplifiedRAG()

def get_rag_suggestion(issue_text: str, sentence_context: str, category: str = "general") -> Dict[str, Any]:
    """
    Main function to get RAG-based suggestions using the simplified system.
    """
    return simplified_rag.get_rule_based_suggestion(issue_text, sentence_context, category)

def is_rag_available() -> bool:
    """Check if RAG system is available."""
    return simplified_rag.initialized

def add_writing_rule(rule: Dict[str, Any]) -> bool:
    """Add a new writing rule to the simplified RAG system."""
    try:
        category_key = f"{rule['category']}_rules"
        if category_key not in simplified_rag.knowledge_base:
            simplified_rag.knowledge_base[category_key] = []
        
        simplified_rag.knowledge_base[category_key].append(rule)
        logger.info(f"Added new rule: {rule['rule_title']}")
        return True
    except Exception as e:
        logger.error(f"Error adding rule: {e}")
        return False

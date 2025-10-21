"""
Pure RAG → LLM Solution Generator
================================

This system does exactly what you want:
1. Flagged issue detected
2. RAG context retrieved from rules_rag_context.json
3. Rich context + issue sent to LLM (Ollama)
4. LLM generates intelligent solution

NO hardcoded answers - everything comes from RAG + LLM intelligence.
"""

import json
import requests
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FlaggedIssue:
    """Represents a flagged writing issue"""
    sentence: str
    issue: str
    line_number: Optional[int] = None
    severity: str = "medium"
    context: str = ""  # Surrounding text for better context

@dataclass
class RAGResponse:
    """Response from RAG system"""
    issue_type: str
    suggestion: str
    detailed_context: str
    examples: List[str]
    confidence: float = 1.0

@dataclass
class LLMResponse:
    """Response from LLM"""
    original_sentence: str
    corrected_sentence: str
    explanation: str
    reasoning: str
    confidence: float = 0.0

class PureRAGLLMSolutionGenerator:
    """Pure RAG → LLM solution generator with no hardcoded answers"""
    
    def __init__(self, rules_file: str = "rules_rag_context.json", config_file: str = "ollama_config.json"):
        """Initialize the pure RAG-LLM system"""
        self.rules_file = rules_file
        self.config_file = config_file
        self.rag_knowledge_base = {}
        self.ollama_config = {}
        
        self.load_rag_knowledge_base()
        self.load_ollama_config()
    
    def load_rag_knowledge_base(self):
        """Load RAG knowledge base from rules_rag_context.json"""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            # Structure the knowledge base for efficient RAG retrieval
            self.rag_knowledge_base = {}
            for rule in rules:
                issue_type = rule["issue"]
                self.rag_knowledge_base[issue_type] = {
                    "suggestion": rule["suggestion"],
                    "context": rule["rag_context"],
                    "examples": self.extract_examples_from_context(rule["rag_context"]),
                    "keywords": self.extract_keywords_from_context(rule["rag_context"])
                }
            
            logger.info(f"Loaded RAG knowledge base with {len(self.rag_knowledge_base)} issue types")
            
        except FileNotFoundError:
            logger.error(f"RAG knowledge base file {self.rules_file} not found")
            self.rag_knowledge_base = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing RAG knowledge base: {e}")
            self.rag_knowledge_base = {}
    
    def load_ollama_config(self):
        """Load Ollama configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.ollama_config = json.load(f)["ollama_config"]
            logger.info("Loaded Ollama configuration")
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            self.ollama_config = {
                "api_url": "http://localhost:11434/api/generate",
                "models": {"balanced": "phi3:mini"},
                "timeouts": {"standard": 15},
                "generation_options": {
                    "standard": {
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "num_predict": 200,
                        "num_ctx": 4096
                    }
                }
            }
    
    def extract_examples_from_context(self, rag_context: str) -> List[str]:
        """Extract examples from RAG context"""
        examples = []
        
        # Look for example patterns
        import re
        
        # Pattern 1: "Example: 'text' → 'text'"
        pattern1 = r"Example:\s*['\"]([^'\"]+)['\"].*?→.*?['\"]([^'\"]+)['\"]"
        matches1 = re.findall(pattern1, rag_context)
        for before, after in matches1:
            examples.append(f"'{before}' → '{after}'")
        
        # Pattern 2: "Example: text"
        pattern2 = r"Example:\s*([^.]+)\."
        matches2 = re.findall(pattern2, rag_context)
        for match in matches2:
            if match not in str(examples):  # Avoid duplicates
                examples.append(match.strip())
        
        return examples
    
    def extract_keywords_from_context(self, rag_context: str) -> List[str]:
        """Extract key concepts from RAG context"""
        # Simple keyword extraction
        keywords = []
        
        # Common technical writing concepts
        concept_words = [
            "readability", "clarity", "concise", "active voice", "passive voice",
            "specific", "precise", "consistent", "professional", "direct",
            "technical", "audience", "instructions", "procedures"
        ]
        
        context_lower = rag_context.lower()
        for word in concept_words:
            if word in context_lower:
                keywords.append(word)
        
        return keywords
    
    def retrieve_rag_context(self, flagged_issue: FlaggedIssue) -> RAGResponse:
        """
        Retrieve relevant context from RAG knowledge base
        This is the RAG step - finding relevant information for the issue
        """
        issue_type = flagged_issue.issue
        
        if issue_type not in self.rag_knowledge_base:
            logger.warning(f"No RAG context found for issue type: {issue_type}")
            return RAGResponse(
                issue_type=issue_type,
                suggestion="No specific guidance available",
                detailed_context="General writing improvement needed",
                examples=[],
                confidence=0.1
            )
        
        rag_entry = self.rag_knowledge_base[issue_type]
        
        return RAGResponse(
            issue_type=issue_type,
            suggestion=rag_entry["suggestion"],
            detailed_context=rag_entry["context"],
            examples=rag_entry["examples"],
            confidence=1.0
        )
    
    def build_enhanced_prompt(self, flagged_issue: FlaggedIssue, rag_response: RAGResponse) -> str:
        """
        Build a rich, contextual prompt for the LLM using RAG information
        This combines the flagged issue with RAG context for maximum intelligence
        """
        
        prompt = f"""You are an expert technical writing assistant with deep knowledge of documentation best practices.

TASK: Improve the following sentence that has been flagged for a writing issue.

FLAGGED SENTENCE: "{flagged_issue.sentence}"

IDENTIFIED ISSUE: {rag_response.issue_type}

RAG KNOWLEDGE CONTEXT:
- Writing Rule: {rag_response.suggestion}
- Detailed Guidance: {rag_response.detailed_context}"""

        if rag_response.examples:
            prompt += f"\n- Examples from Knowledge Base:\n"
            for example in rag_response.examples:
                prompt += f"  • {example}\n"

        if flagged_issue.context:
            prompt += f"\nSURROUNDING CONTEXT: {flagged_issue.context}"

        prompt += f"""

REQUIREMENTS:
1. Rewrite the sentence to fix the identified issue
2. Apply the guidance from the RAG knowledge base
3. Maintain the original meaning and intent
4. Make the writing clearer and more professional
5. Follow technical documentation best practices

OUTPUT FORMAT:
CORRECTED: [Your improved sentence here]
REASONING: [Explain specifically how you applied the RAG guidance to improve the sentence]
EXPLANATION: [Brief user-friendly explanation of why this change improves the writing]

Focus on applying the specific guidance from the knowledge base to create a meaningful improvement."""

        return prompt
    
    def call_ollama_llm(self, prompt: str, quality: str = "standard") -> Optional[str]:
        """Call Ollama LLM with the RAG-enhanced prompt"""
        try:
            # Get model and options from config
            models = self.ollama_config.get("models", {"balanced": "phi3:mini"})
            model = models.get("balanced", "phi3:mini")
            
            gen_options = self.ollama_config.get("generation_options", {}).get(quality, {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 200,
                "num_ctx": 4096
            })
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": gen_options
            }
            
            timeout = self.ollama_config.get("timeouts", {}).get(quality, 15)
            api_url = self.ollama_config.get("api_url", "http://localhost:11434/api/generate")
            
            logger.info(f"Calling Ollama LLM: {model}")
            
            response = requests.post(api_url, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Ollama API timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama API - is Ollama running?")
            return None
        except Exception as e:
            logger.error(f"Ollama LLM call failed: {e}")
            return None
    
    def parse_llm_response(self, llm_output: str, original_sentence: str) -> LLMResponse:
        """Parse the LLM response into structured format"""
        corrected = ""
        reasoning = ""
        explanation = ""
        
        try:
            lines = llm_output.strip().split('\n')
            
            current_section = None
            content_buffer = []
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('CORRECTED:'):
                    if current_section and content_buffer:
                        self._assign_content(current_section, content_buffer, locals())
                    current_section = 'corrected'
                    content_buffer = [line.replace('CORRECTED:', '').strip()]
                    
                elif line.startswith('REASONING:'):
                    if current_section and content_buffer:
                        self._assign_content(current_section, content_buffer, locals())
                    current_section = 'reasoning'
                    content_buffer = [line.replace('REASONING:', '').strip()]
                    
                elif line.startswith('EXPLANATION:'):
                    if current_section and content_buffer:
                        self._assign_content(current_section, content_buffer, locals())
                    current_section = 'explanation'
                    content_buffer = [line.replace('EXPLANATION:', '').strip()]
                    
                elif line and current_section:
                    content_buffer.append(line)
            
            # Handle the last section
            if current_section and content_buffer:
                self._assign_content(current_section, content_buffer, locals())
        
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            corrected = "Error parsing LLM response"
            reasoning = "Unable to parse LLM output"
            explanation = "LLM response format error"
        
        return LLMResponse(
            original_sentence=original_sentence,
            corrected_sentence=corrected or "No correction provided",
            reasoning=reasoning or "No reasoning provided",
            explanation=explanation or "No explanation provided",
            confidence=0.8 if corrected and corrected != original_sentence else 0.1
        )
    
    def _assign_content(self, section: str, content_buffer: List[str], local_vars: dict):
        """Helper to assign parsed content to variables"""
        content = ' '.join(content_buffer).strip()
        if section == 'corrected':
            local_vars['corrected'] = content
        elif section == 'reasoning':
            local_vars['reasoning'] = content
        elif section == 'explanation':
            local_vars['explanation'] = content
    
    def generate_rag_llm_solution(self, flagged_issue: FlaggedIssue) -> LLMResponse:
        """
        Main method: Pure RAG → LLM workflow
        
        1. Retrieve RAG context for the issue
        2. Build enhanced prompt with RAG information
        3. Send to LLM for intelligent solution
        4. Parse and return structured response
        """
        
        # Step 1: RAG - Retrieve relevant context
        logger.info(f"RAG: Retrieving context for '{flagged_issue.issue}'")
        rag_response = self.retrieve_rag_context(flagged_issue)
        
        if rag_response.confidence < 0.5:
            logger.warning(f"Low confidence RAG retrieval for: {flagged_issue.issue}")
        
        # Step 2: Build RAG-enhanced prompt
        logger.info("Building RAG-enhanced prompt for LLM")
        enhanced_prompt = self.build_enhanced_prompt(flagged_issue, rag_response)
        
        # Step 3: Send to LLM
        logger.info("Sending RAG-enhanced prompt to LLM")
        llm_output = self.call_ollama_llm(enhanced_prompt)
        
        if not llm_output:
            logger.error("LLM call failed - no response received")
            return LLMResponse(
                original_sentence=flagged_issue.sentence,
                corrected_sentence="LLM service unavailable",
                reasoning="Unable to connect to LLM service",
                explanation="AI service is currently unavailable. Please try again later.",
                confidence=0.0
            )
        
        # Step 4: Parse LLM response
        logger.info("Parsing LLM response")
        llm_response = self.parse_llm_response(llm_output, flagged_issue.sentence)
        
        logger.info(f"Generated solution with confidence: {llm_response.confidence:.2f}")
        
        return llm_response

def test_pure_rag_llm_system():
    """Test the pure RAG → LLM system"""
    
    print("🧠 Pure RAG → LLM Solution Generator Test")
    print("=" * 50)
    
    # Initialize the system
    generator = PureRAGLLMSolutionGenerator()
    
    # Test cases
    test_issues = [
        FlaggedIssue(
            sentence="Delete the languages that are not needed.",
            issue="Passive voice",
            context="This appears in a user manual section about language settings."
        ),
        FlaggedIssue(
            sentence="The application runs diagnostics and reports errors, and then logs them into the system automatically.",
            issue="Long sentence",
            context="This is part of a technical overview section."
        ),
        FlaggedIssue(
            sentence="The system works fine after the update.",
            issue="Vague terms",
            context="This appears in a troubleshooting guide."
        )
    ]
    
    for i, issue in enumerate(test_issues, 1):
        print(f"\n🔍 Test Case {i}: {issue.issue}")
        print("-" * 30)
        print(f"Original: '{issue.sentence}'")
        print(f"Context: {issue.context}")
        
        # Generate RAG → LLM solution
        solution = generator.generate_rag_llm_solution(issue)
        
        print(f"\n✨ RAG-LLM Solution:")
        print(f"Corrected: '{solution.corrected_sentence}'")
        print(f"Reasoning: {solution.reasoning}")
        print(f"Explanation: {solution.explanation}")
        print(f"Confidence: {solution.confidence:.1%}")

if __name__ == "__main__":
    test_pure_rag_llm_system()
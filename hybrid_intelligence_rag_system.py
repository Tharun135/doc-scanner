"""
Hybrid Intelligence RAG-LLM System with Model Selection
======================================================

This implements your hybrid intelligence approach:
- phi3:mini for fast, lightweight tasks (90% of cases)
- llama3:8b for deep reasoning and complex analysis
- Integrated with Flask backend
- RAG-enhanced context for both models
"""

import json
import requests
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligenceMode(Enum):
    """Intelligence modes for model selection"""
    FAST = "fast"           # phi3:mini - quick responses
    DEFAULT = "default"     # phi3:mini - balanced
    DEEP = "deep"          # llama3:8b - complex reasoning
    QUALITY = "quality"    # llama3:8b - best quality

@dataclass
class FlaggedIssue:
    """Represents a flagged writing issue with complexity assessment"""
    sentence: str
    issue: str
    line_number: Optional[int] = None
    severity: str = "medium"
    context: str = ""
    complexity: str = "default"  # "fast", "default", "deep"

class HybridIntelligenceRAGSystem:
    """Hybrid RAG-LLM system with intelligent model selection"""
    
    def __init__(self, rules_file: str = "rules_rag_context.json", config_file: str = "ollama_config.json"):
        """Initialize the hybrid intelligence system"""
        self.rules_file = rules_file
        self.config_file = config_file
        self.rag_knowledge_base = {}
        self.ollama_config = {}
        
        # Model mapping
        self.model_map = {
            IntelligenceMode.FAST: "phi3:mini",
            IntelligenceMode.DEFAULT: "phi3:mini", 
            IntelligenceMode.DEEP: "llama3:8b",
            IntelligenceMode.QUALITY: "llama3:8b"
        }
        
        self.load_rag_knowledge_base()
        self.load_ollama_config()
    
    def load_rag_knowledge_base(self):
        """Load RAG knowledge base from rules_rag_context.json"""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            self.rag_knowledge_base = {}
            for rule in rules:
                issue_type = rule["issue"]
                self.rag_knowledge_base[issue_type] = {
                    "suggestion": rule["suggestion"],
                    "context": rule["rag_context"],
                    "examples": self.extract_examples_from_context(rule["rag_context"]),
                    "complexity": self.assess_issue_complexity(issue_type, rule["rag_context"])
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
                "chat_url": "http://localhost:11434/api/chat",
                "models": {
                    "fast": "phi3:mini",
                    "balanced": "phi3:mini", 
                    "quality": "llama3:8b"
                }
            }
    
    def assess_issue_complexity(self, issue_type: str, rag_context: str) -> str:
        """Assess the complexity of an issue to determine model selection"""
        
        # Complex issues that benefit from deeper reasoning
        complex_issues = [
            "Complex sentence structure",
            "Inconsistent terminology", 
            "Style inconsistency",
            "Ambiguous references",
            "Use of jargon"
        ]
        
        # Simple issues that can be handled quickly
        simple_issues = [
            "Title capitalization",
            "Improper punctuation",
            "Improper numbering",
            "Inconsistent formatting"
        ]
        
        # Check context length and complexity indicators
        context_complexity_indicators = [
            "nested clauses", "multiple", "complex", "intricate", 
            "sophisticated", "nuanced", "context-dependent"
        ]
        
        if issue_type in complex_issues:
            return "deep"
        elif issue_type in simple_issues:
            return "fast"
        elif any(indicator in rag_context.lower() for indicator in context_complexity_indicators):
            return "deep"
        else:
            return "default"
    
    def extract_examples_from_context(self, rag_context: str) -> List[str]:
        """Extract examples from RAG context"""
        examples = []
        import re
        
        # Pattern for examples with arrows
        pattern1 = r"Example:\s*['\"]([^'\"]+)['\"].*?→.*?['\"]([^'\"]+)['\"]"
        matches1 = re.findall(pattern1, rag_context)
        for before, after in matches1:
            examples.append(f"'{before}' → '{after}'")
        
        return examples
    
    def determine_intelligence_mode(self, flagged_issue: FlaggedIssue) -> IntelligenceMode:
        """Determine which intelligence mode to use based on issue complexity"""
        
        # Check if user explicitly specified complexity
        if flagged_issue.complexity == "deep":
            return IntelligenceMode.DEEP
        elif flagged_issue.complexity == "fast":
            return IntelligenceMode.FAST
        
        # Get RAG-based complexity assessment
        rag_entry = self.rag_knowledge_base.get(flagged_issue.issue, {})
        rag_complexity = rag_entry.get("complexity", "default")
        
        # Consider sentence length and context
        sentence_length = len(flagged_issue.sentence.split())
        context_length = len(flagged_issue.context.split()) if flagged_issue.context else 0
        
        # Decision logic for hybrid intelligence
        if (rag_complexity == "deep" or 
            sentence_length > 25 or 
            context_length > 50 or
            flagged_issue.severity == "high"):
            return IntelligenceMode.DEEP
        elif (rag_complexity == "fast" or 
              sentence_length < 10 or
              flagged_issue.severity == "low"):
            return IntelligenceMode.FAST
        else:
            return IntelligenceMode.DEFAULT
    
    def build_hybrid_prompt(self, flagged_issue: FlaggedIssue, rag_context: dict, mode: IntelligenceMode) -> str:
        """Build prompt optimized for the selected intelligence mode"""
        
        base_prompt = f"""You are a writing style expert specializing in technical documentation.

TASK: Improve the following flagged sentence using the provided guidance.

FLAGGED SENTENCE: "{flagged_issue.sentence}"
ISSUE TYPE: {flagged_issue.issue}

RAG GUIDANCE:
- Rule: {rag_context.get('suggestion', 'Improve writing quality')}
- Context: {rag_context.get('context', 'Apply best practices')}"""

        if rag_context.get('examples'):
            base_prompt += f"\n- Examples: {', '.join(rag_context['examples'])}"

        if flagged_issue.context:
            base_prompt += f"\n\nSURROUNDING CONTEXT: {flagged_issue.context}"

        # Mode-specific instructions
        if mode in [IntelligenceMode.DEEP, IntelligenceMode.QUALITY]:
            base_prompt += """

DEEP ANALYSIS REQUIRED:
1. Analyze the sentence structure and context thoroughly
2. Consider multiple improvement approaches
3. Evaluate the impact on readability and clarity
4. Provide detailed reasoning for your choices
5. Consider the target audience and documentation type

DETAILED OUTPUT FORMAT:
CORRECTED: [Your improved sentence]
ANALYSIS: [Deep analysis of the issue and your approach]
REASONING: [Detailed explanation of your corrections]
ALTERNATIVES: [Other possible improvements considered]
EXPLANATION: [User-friendly summary]"""
        
        else:  # FAST or DEFAULT mode
            base_prompt += """

EFFICIENT ANALYSIS:
1. Apply the RAG guidance directly
2. Make clear, focused improvements
3. Maintain original meaning and intent

CONCISE OUTPUT FORMAT:
CORRECTED: [Your improved sentence]
REASONING: [How you applied the guidance]
EXPLANATION: [Brief explanation of the improvement]"""

        return base_prompt
    
    def call_ollama_chat(self, prompt: str, model: str, mode: IntelligenceMode) -> Optional[str]:
        """Call Ollama using the chat API with hybrid intelligence"""
        try:
            # Prepare system message based on intelligence mode
            if mode in [IntelligenceMode.DEEP, IntelligenceMode.QUALITY]:
                system_content = "You are a senior technical writing expert with deep knowledge of documentation best practices, style guides, and advanced writing techniques. Provide thorough analysis and detailed reasoning. IMPORTANT: Always use 'Application' instead of 'technical writer' in your suggestions."
            else:
                system_content = "You are a technical writing expert. Provide clear, focused improvements based on the given guidance. IMPORTANT: Always use 'Application' instead of 'technical writer' in your suggestions."
            
            # Use chat API format
            chat_url = self.ollama_config.get("chat_url", "http://localhost:11434/api/chat")
            
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": prompt}
                ],
                "stream": False,
                "options": self.get_model_options(mode)
            }
            
            timeout = 30 if mode in [IntelligenceMode.DEEP, IntelligenceMode.QUALITY] else 15
            
            logger.info(f"Calling Ollama with {model} in {mode.value} mode")
            
            response = requests.post(chat_url, json=payload, timeout=timeout)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                logger.error(f"Ollama chat API error: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Ollama timeout in {mode.value} mode")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama - is it running?")
            return None
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            return None
    
    def get_model_options(self, mode: IntelligenceMode) -> dict:
        """Get model-specific options based on intelligence mode"""
        
        if mode == IntelligenceMode.FAST:
            return {
                "temperature": 0.1,
                "top_p": 0.8,
                "num_predict": 100,
                "num_ctx": 2048
            }
        elif mode == IntelligenceMode.DEFAULT:
            return {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 150,
                "num_ctx": 3072
            }
        else:  # DEEP or QUALITY
            return {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 300,
                "num_ctx": 4096,
                "repeat_penalty": 1.1
            }
    
    def generate_hybrid_solution(self, flagged_issue: FlaggedIssue) -> dict:
        """
        Generate solution using hybrid intelligence model selection
        
        This is your main method that implements:
        - RAG context retrieval
        - Intelligent model selection
        - Optimized prompting for each model
        """
        
        # Step 1: Retrieve RAG context
        rag_context = self.rag_knowledge_base.get(flagged_issue.issue, {})
        
        if not rag_context:
            return {
                "success": False,
                "error": f"No RAG context found for issue: {flagged_issue.issue}",
                "model_used": None,
                "intelligence_mode": None
            }
        
        # Step 2: Determine intelligence mode
        intelligence_mode = self.determine_intelligence_mode(flagged_issue)
        selected_model = self.model_map[intelligence_mode]
        
        logger.info(f"Selected {intelligence_mode.value} mode with model {selected_model}")
        
        # Step 3: Build optimized prompt
        prompt = self.build_hybrid_prompt(flagged_issue, rag_context, intelligence_mode)
        
        # Step 4: Call appropriate model
        llm_response = self.call_ollama_chat(prompt, selected_model, intelligence_mode)
        
        if not llm_response:
            return {
                "success": False,
                "error": "LLM service unavailable",
                "model_used": selected_model,
                "intelligence_mode": intelligence_mode.value
            }
        
        # Step 5: Parse response
        parsed_response = self.parse_hybrid_response(llm_response, intelligence_mode)
        
        return {
            "success": True,
            "original": flagged_issue.sentence,
            "corrected": parsed_response.get("corrected", ""),
            "reasoning": parsed_response.get("reasoning", ""),
            "explanation": parsed_response.get("explanation", ""),
            "analysis": parsed_response.get("analysis", ""),  # Deep mode only
            "alternatives": parsed_response.get("alternatives", ""),  # Deep mode only
            "model_used": selected_model,
            "intelligence_mode": intelligence_mode.value,
            "rag_context": rag_context
        }
    
    def parse_hybrid_response(self, response: str, mode: IntelligenceMode) -> dict:
        """Parse LLM response based on intelligence mode"""
        
        result = {
            "corrected": "",
            "reasoning": "",
            "explanation": "",
            "analysis": "",
            "alternatives": ""
        }
        
        lines = response.strip().split('\n')
        current_section = None
        content_buffer = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('CORRECTED:'):
                if current_section and content_buffer:
                    result[current_section] = ' '.join(content_buffer).strip()
                current_section = 'corrected'
                content_buffer = [line.replace('CORRECTED:', '').strip()]
                
            elif line.startswith('REASONING:'):
                if current_section and content_buffer:
                    result[current_section] = ' '.join(content_buffer).strip()
                current_section = 'reasoning'
                content_buffer = [line.replace('REASONING:', '').strip()]
                
            elif line.startswith('EXPLANATION:'):
                if current_section and content_buffer:
                    result[current_section] = ' '.join(content_buffer).strip()
                current_section = 'explanation'
                content_buffer = [line.replace('EXPLANATION:', '').strip()]
                
            elif line.startswith('ANALYSIS:') and mode in [IntelligenceMode.DEEP, IntelligenceMode.QUALITY]:
                if current_section and content_buffer:
                    result[current_section] = ' '.join(content_buffer).strip()
                current_section = 'analysis'
                content_buffer = [line.replace('ANALYSIS:', '').strip()]
                
            elif line.startswith('ALTERNATIVES:') and mode in [IntelligenceMode.DEEP, IntelligenceMode.QUALITY]:
                if current_section and content_buffer:
                    result[current_section] = ' '.join(content_buffer).strip()
                current_section = 'alternatives'
                content_buffer = [line.replace('ALTERNATIVES:', '').strip()]
                
            elif line and current_section:
                content_buffer.append(line)
        
        # Handle the last section
        if current_section and content_buffer:
            result[current_section] = ' '.join(content_buffer).strip()
        
        return result

def test_hybrid_intelligence():
    """Test the hybrid intelligence system"""
    
    print("🧠 Hybrid Intelligence RAG-LLM System Test")
    print("=" * 55)
    
    system = HybridIntelligenceRAGSystem()
    
    # Test cases with different complexities
    test_cases = [
        FlaggedIssue(
            sentence="Delete the languages that are not needed.",
            issue="Passive voice",
            complexity="fast",  # Simple case
            context="User manual section"
        ),
        FlaggedIssue(
            sentence="When the server is restarted after maintenance, which usually happens weekly, all temporary sessions are cleared.",
            issue="Complex sentence structure", 
            complexity="deep",  # Complex case requiring deep analysis
            context="Technical documentation for system administrators"
        ),
        FlaggedIssue(
            sentence="The system works fine after the update.",
            issue="Vague terms",
            complexity="default",  # Standard case
            context="Troubleshooting guide"
        )
    ]
    
    for i, issue in enumerate(test_cases, 1):
        print(f"\n🔍 Test Case {i}: {issue.issue}")
        print(f"   Sentence: '{issue.sentence}'")
        print(f"   Requested Complexity: {issue.complexity}")
        
        result = system.generate_hybrid_solution(issue)
        
        if result['success']:
            print(f"\n✨ Hybrid Intelligence Result:")
            print(f"   Model Used: {result['model_used']}")
            print(f"   Intelligence Mode: {result['intelligence_mode']}")
            print(f"   Corrected: '{result['corrected']}'")
            print(f"   Reasoning: {result['reasoning']}")
            print(f"   Explanation: {result['explanation']}")
            
            if result.get('analysis'):
                print(f"   Deep Analysis: {result['analysis']}")
            if result.get('alternatives'):
                print(f"   Alternatives: {result['alternatives']}")
        else:
            print(f"   ❌ Error: {result['error']}")
            print(f"   Attempted Mode: {result['intelligence_mode']}")

if __name__ == "__main__":
    test_hybrid_intelligence()
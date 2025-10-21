"""
DocScanner AI - RAG-Enhanced Writing Suggestions with Ollama Integration
=====================================================================

This script integrates your writing rules JSON with Ollama to generate
intelligent, context-aware solutions for flagged writing issues.

Features:
- Loads writing rules from JSON
- Processes flagged sentences
- Uses Ollama for LLM-powered solutions
- Returns corrected sentences with explanations
- Supports batch processing
- Includes fallback strategies
"""

import json
import requests
import subprocess
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FlaggedIssue:
    """Represents a flagged writing issue"""
    sentence: str
    issue: str
    line_number: Optional[int] = None
    severity: str = "medium"

@dataclass
class AIResponse:
    """Represents the AI-generated solution"""
    original_sentence: str
    corrected_sentence: str
    explanation: str
    issue_type: str
    confidence: float = 0.0

class OllamaRagSolutionGenerator:
    """Main class for generating RAG-enhanced solutions using Ollama"""
    
    def __init__(self, rules_file: str = "rules_rag_context.json", config_file: str = "ollama_config.json"):
        """Initialize the solution generator"""
        self.rules_file = rules_file
        self.config_file = config_file
        self.rules_dict = {}
        self.config = {}
        self.load_rules()
        self.load_config()
    
    def load_rules(self):
        """Load writing rules from JSON file"""
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                rules = json.load(f)
            
            # Create dictionary for quick lookup
            self.rules_dict = {rule["issue"]: rule for rule in rules}
            logger.info(f"Loaded {len(self.rules_dict)} writing rules")
            
        except FileNotFoundError:
            logger.error(f"Rules file {self.rules_file} not found")
            self.rules_dict = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing rules file: {e}")
            self.rules_dict = {}
    
    def load_config(self):
        """Load Ollama configuration"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)["ollama_config"]
            logger.info("Loaded Ollama configuration")
            
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_file} not found, using defaults")
            self.config = {
                "api_url": "http://localhost:11434/api/generate",
                "models": {"balanced": "phi3:mini"},
                "timeouts": {"standard": 10}
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
    
    def build_prompt(self, sentence: str, rule: Dict) -> str:
        """Build the prompt for Ollama based on the sentence and rule"""
        return f"""You are a technical writing assistant specializing in documentation improvement.

SENTENCE TO IMPROVE: "{sentence}"

ISSUE IDENTIFIED: {rule['issue']}
SUGGESTION: {rule['suggestion']}
DETAILED CONTEXT: {rule['rag_context']}

TASK: Please rewrite the sentence to fix the identified issue and provide a clear explanation.

REQUIRED OUTPUT FORMAT:
CORRECTED: [Your improved sentence here]
EXPLANATION: [Brief explanation of why this change improves clarity/readability]

Be concise but thorough. Focus on the specific issue mentioned."""

    def call_ollama_api(self, prompt: str, model: str = "phi3:mini", quality: str = "standard") -> Optional[str]:
        """Call Ollama API to generate response"""
        try:
            # Get configuration for the quality level
            gen_options = self.config.get("generation_options", {}).get(quality, {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 150,
                "num_ctx": 2048
            })
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": gen_options
            }
            
            timeout = self.config.get("timeouts", {}).get(quality, 10)
            
            response = requests.post(
                self.config.get("api_url", "http://localhost:11434/api/generate"),
                json=payload,
                timeout=timeout
            )
            
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
            logger.error("Cannot connect to Ollama API")
            return None
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            return None
    
    def call_ollama_cli(self, prompt: str, model: str = "phi3:mini") -> Optional[str]:
        """Fallback: Call Ollama via command line"""
        try:
            result = subprocess.run(
                ["ollama", "run", model, prompt],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Ollama CLI error: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error("Ollama CLI timeout")
            return None
        except FileNotFoundError:
            logger.error("Ollama CLI not found in PATH")
            return None
        except Exception as e:
            logger.error(f"Ollama CLI call failed: {e}")
            return None
    
    def parse_ai_response(self, response: str) -> Tuple[str, str]:
        """Parse the AI response to extract corrected sentence and explanation"""
        corrected = ""
        explanation = ""
        
        try:
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('CORRECTED:'):
                    corrected = line.replace('CORRECTED:', '').strip()
                elif line.startswith('EXPLANATION:'):
                    explanation = line.replace('EXPLANATION:', '').strip()
                elif 'CORRECTED' in line and ':' in line:
                    corrected = line.split(':', 1)[1].strip()
                elif 'EXPLANATION' in line and ':' in line:
                    explanation = line.split(':', 1)[1].strip()
            
            # If structured parsing fails, try to extract from unstructured text
            if not corrected and not explanation:
                # Look for quoted sentences as corrected version
                import re
                quoted_sentences = re.findall(r'"([^"]*)"', response)
                if quoted_sentences:
                    corrected = quoted_sentences[-1]  # Take the last quoted sentence
                
                # Use the rest as explanation
                explanation = response.replace(corrected, '').strip()
        
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            corrected = "Error parsing response"
            explanation = "Unable to parse AI response"
        
        return corrected, explanation
    
    def generate_solution(self, flagged_issue: FlaggedIssue) -> AIResponse:
        """Generate a solution for a single flagged issue"""
        # Get the rule for this issue
        rule = self.rules_dict.get(flagged_issue.issue)
        
        if not rule:
            logger.warning(f"No rule found for issue: {flagged_issue.issue}")
            return AIResponse(
                original_sentence=flagged_issue.sentence,
                corrected_sentence="No rule available",
                explanation=f"No guidance available for issue type: {flagged_issue.issue}",
                issue_type=flagged_issue.issue,
                confidence=0.0
            )
        
        # Build prompt
        prompt = self.build_prompt(flagged_issue.sentence, rule)
        
        # Try different models based on configuration
        models = self.config.get("models", {"balanced": "phi3:mini"})
        
        # Try API first, then CLI as fallback
        response = None
        model_used = None
        
        for quality, model in models.items():
            logger.info(f"Trying {model} ({quality} quality)")
            
            # Try API first
            response = self.call_ollama_api(prompt, model, quality)
            if response:
                model_used = model
                break
            
            # Try CLI as fallback
            response = self.call_ollama_cli(prompt, model)
            if response:
                model_used = model
                break
        
        if not response:
            logger.error("All Ollama calls failed")
            return AIResponse(
                original_sentence=flagged_issue.sentence,
                corrected_sentence="AI service unavailable",
                explanation="Unable to connect to AI service",
                issue_type=flagged_issue.issue,
                confidence=0.0
            )
        
        # Parse the response
        corrected, explanation = self.parse_ai_response(response)
        
        return AIResponse(
            original_sentence=flagged_issue.sentence,
            corrected_sentence=corrected,
            explanation=explanation,
            issue_type=flagged_issue.issue,
            confidence=0.8  # You can implement confidence scoring later
        )
    
    def generate_batch_solutions(self, flagged_issues: List[FlaggedIssue]) -> List[AIResponse]:
        """Generate solutions for multiple flagged issues"""
        solutions = []
        
        logger.info(f"Processing {len(flagged_issues)} flagged issues")
        
        for i, issue in enumerate(flagged_issues, 1):
            logger.info(f"Processing issue {i}/{len(flagged_issues)}: {issue.issue}")
            
            solution = self.generate_solution(issue)
            solutions.append(solution)
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.5)
        
        return solutions
    
    def export_solutions(self, solutions: List[AIResponse], filename: str = "ai_solutions.json"):
        """Export solutions to JSON file"""
        solutions_data = []
        
        for solution in solutions:
            solutions_data.append({
                "original_sentence": solution.original_sentence,
                "corrected_sentence": solution.corrected_sentence,
                "explanation": solution.explanation,
                "issue_type": solution.issue_type,
                "confidence": solution.confidence
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(solutions_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Solutions exported to {filename}")

def main():
    """Example usage of the OllamaRagSolutionGenerator"""
    
    # Initialize the generator
    generator = OllamaRagSolutionGenerator()
    
    # Example flagged issues (normally these would come from your DocScanner)
    test_issues = [
        FlaggedIssue(
            sentence="The application runs diagnostics and reports errors, and then logs them into the system automatically.",
            issue="Long sentence"
        ),
        FlaggedIssue(
            sentence="The issue was resolved by the developer.",
            issue="Passive voice"
        ),
        FlaggedIssue(
            sentence="The system works fine after the update.",
            issue="Vague terms"
        ),
        FlaggedIssue(
            sentence="Click save button then logout and you can close the window.",
            issue="Improper list structure"
        )
    ]
    
    print("🤖 DocScanner AI - RAG-Enhanced Solutions")
    print("=" * 50)
    
    # Generate solutions
    solutions = generator.generate_batch_solutions(test_issues)
    
    # Display results
    for i, solution in enumerate(solutions, 1):
        print(f"\n📝 Issue #{i}: {solution.issue_type}")
        print(f"Original: {solution.original_sentence}")
        print(f"Corrected: {solution.corrected_sentence}")
        print(f"Explanation: {solution.explanation}")
        print("-" * 50)
    
    # Export to file
    generator.export_solutions(solutions, "rag_ai_solutions.json")
    print(f"\n✅ Generated {len(solutions)} solutions and exported to 'rag_ai_solutions.json'")

if __name__ == "__main__":
    main()
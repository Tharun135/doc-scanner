"""
Fallback Solution Generator
==========================

This provides intelligent solutions even when Ollama is not available,
using rule-based transformations and your RAG context.
"""

from ollama_rag_integration import OllamaRagSolutionGenerator, FlaggedIssue, AIResponse
import re
import json

class FallbackSolutionGenerator(OllamaRagSolutionGenerator):
    """Extended generator with rule-based fallbacks when Ollama is unavailable"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_fallback_patterns()
    
    def load_fallback_patterns(self):
        """Load rule-based transformation patterns"""
        # Import enhanced passive voice processor
        try:
            from enhanced_passive_voice_processor import EnhancedPassiveVoiceProcessor
            self.passive_processor = EnhancedPassiveVoiceProcessor()
        except ImportError:
            self.passive_processor = None
        
        self.fallback_patterns = {
            "Long sentence": {
                "pattern": r"(.+?),\s*and\s*(.+)",
                "transform": lambda m: f"{m.group(1).strip()}. {m.group(2).strip().capitalize()}",
                "explanation": "Split long sentence at conjunctions for better readability."
            },
            
            "Passive voice": {
                "custom_handler": True,
                "explanation": "Converted from passive to active voice to make the action clearer."
            },
            
            "Title capitalization": {
                "pattern": r"^(.+)$",
                "transform": lambda m: self.title_case(m.group(1)),
                "explanation": "Applied proper title case capitalization."
            },
            
            "Vague terms": {
                "replacements": {
                    "fine": "functioning correctly",
                    "good": "operational",
                    "bad": "non-functional", 
                    "nice": "user-friendly",
                    "great": "highly effective",
                    "works": "operates",
                    "stuff": "components",
                    "things": "elements"
                },
                "explanation": "Replaced vague terms with specific technical language."
            }
        }
    
    def title_case(self, text):
        """Apply proper title case"""
        # Words that should not be capitalized (except at start/end)
        minor_words = ['a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'if', 'in', 'is', 'of', 'on', 'or', 'the', 'to', 'up', 'via']
        
        words = text.lower().split()
        result = []
        
        for i, word in enumerate(words):
            if i == 0 or i == len(words) - 1 or word not in minor_words:
                result.append(word.capitalize())
            else:
                result.append(word)
        
        return ' '.join(result)
    
    def apply_vague_terms_fix(self, sentence):
        """Apply vague terms replacement"""
        result = sentence
        replacements_made = []
        
        for vague, precise in self.fallback_patterns["Vague terms"]["replacements"].items():
            pattern = r'\b' + re.escape(vague) + r'\b'
            if re.search(pattern, result, re.IGNORECASE):
                result = re.sub(pattern, precise, result, flags=re.IGNORECASE)
                replacements_made.append(f"'{vague}' → '{precise}'")
        
        if replacements_made:
            return result, f"Replaced vague terms: {', '.join(replacements_made)}"
        else:
            return result, "Made text more specific and technical"
    
    def generate_fallback_solution(self, flagged_issue: FlaggedIssue) -> AIResponse:
        """Generate solution using rule-based patterns"""
        
        sentence = flagged_issue.sentence
        issue_type = flagged_issue.issue
        
        # Get the rule context
        rule = self.rules_dict.get(issue_type, {})
        base_explanation = rule.get('suggestion', 'Applied writing improvement')
        
        corrected = sentence
        explanation = base_explanation
        
        # Apply pattern-based transformations
        if issue_type in self.fallback_patterns:
            pattern_info = self.fallback_patterns[issue_type]
            
            # Handle passive voice with enhanced processor
            if issue_type == "Passive voice" and self.passive_processor:
                try:
                    corrected, explanation = self.passive_processor.transform_passive_to_active(sentence)
                except Exception as e:
                    corrected = sentence
                    explanation = f"Passive voice detected. {rule.get('suggestion', 'Convert to active voice.')}"
            
            elif issue_type == "Vague terms":
                corrected, explanation = self.apply_vague_terms_fix(sentence)
            
            elif "pattern" in pattern_info:
                pattern = pattern_info["pattern"]
                transform = pattern_info["transform"]
                
                match = re.search(pattern, sentence)
                if match:
                    try:
                        corrected = transform(match)
                        explanation = pattern_info["explanation"]
                    except:
                        corrected = sentence
                        explanation = f"Rule-based fix attempted for {issue_type}"
        
        # If no transformation was applied, provide the RAG context as explanation
        if corrected == sentence and rule:
            explanation = f"Suggested fix: {rule.get('suggestion', 'Apply writing guidelines')}. Context: {rule.get('rag_context', 'Follow technical writing best practices.')[:100]}..."
        
        return AIResponse(
            original_sentence=sentence,
            corrected_sentence=corrected,
            explanation=explanation,
            issue_type=issue_type,
            confidence=0.6  # Medium confidence for rule-based fixes
        )
    
    def generate_solution(self, flagged_issue: FlaggedIssue) -> AIResponse:
        """Try Ollama first, then fall back to rule-based solution"""
        
        # Try the parent class method (Ollama)
        ollama_solution = super().generate_solution(flagged_issue)
        
        # If Ollama failed, use fallback
        if ollama_solution.corrected_sentence in ["AI service unavailable", "No rule available"]:
            return self.generate_fallback_solution(flagged_issue)
        
        return ollama_solution

def test_fallback_generator():
    """Test the fallback generator"""
    
    print("🔧 Testing Fallback Solution Generator")
    print("=" * 45)
    
    generator = FallbackSolutionGenerator()
    
    test_cases = [
        FlaggedIssue(
            sentence="The application runs diagnostics and reports errors, and then logs them into the system automatically.",
            issue="Long sentence"
        ),
        FlaggedIssue(
            sentence="The issue was resolved by the developer.",
            issue="Passive voice" 
        ),
        FlaggedIssue(
            sentence="installing the application",
            issue="Title capitalization"
        ),
        FlaggedIssue(
            sentence="The system works fine and everything is good.",
            issue="Vague terms"
        )
    ]
    
    print("Testing rule-based fallbacks...")
    print()
    
    for i, issue in enumerate(test_cases, 1):
        solution = generator.generate_fallback_solution(issue)
        
        print(f"🔍 Test {i}: {solution.issue_type}")
        print(f"   Original:  \"{solution.original_sentence}\"")
        print(f"   ✨ Fixed:   \"{solution.corrected_sentence}\"")
        print(f"   💡 Why:    {solution.explanation}")
        print(f"   📊 Confidence: {solution.confidence:.1%}")
        print()
    
    return generator

if __name__ == "__main__":
    # Test the fallback system
    generator = test_fallback_generator()
    
    print("\n" + "="*50)
    print("🎯 OLLAMA SETUP GUIDE")
    print("="*50)
    print()
    print("To enable full AI-powered solutions:")
    print()
    print("1. Install Ollama:")
    print("   Visit: https://ollama.ai")
    print("   Download and install for Windows")
    print()
    print("2. Install a model:")
    print("   ollama pull phi3:mini    # Fast, good quality")
    print("   ollama pull llama3:8b    # Slower, better quality")
    print()
    print("3. Start Ollama service:")
    print("   ollama serve")
    print()
    print("4. Test the connection:")
    print("   curl http://localhost:11434/api/tags")
    print()
    print("✅ Until then, the system uses intelligent rule-based fallbacks!")
import unittest
from unittest.mock import patch
import os
import sys

# Ensure project root is in python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

class TestFallback(unittest.TestCase):
    @patch('app.services.style_guide_service.generate_style_suggestion_local_ollama')
    def test_local_rule_engine_fallback_extraction(self, mock_ollama):
        # Setup env to simulate local mode and disable cloud fallback
        os.environ["ALLOW_CLOUD_LLM"] = "false"
        os.environ["DOCSCANNER_MODE"] = "local"
        
        # Mock Ollama call to raise an exception (simulating offline/timeout)
        mock_ollama.side_effect = Exception("Ollama offline")
        
        from app.services.style_guide_service import generate_style_suggestion
        
        # Test case: Heading style violation
        feedback_text = 'Use lowercase in headings except for the first word and proper nouns. Words to lowercase: Common, Configurator. Suggested: "Launching common configurator on IEM"'
        sentence = "Launching Common Configurator on IEM"
        
        result = generate_style_suggestion(sentence, "SG-HE-002", feedback_text)
        
        print("Resulting Suggestion:", result.get("suggestion"))
        print("Resulting AI Answer:", result.get("ai_answer"))
        print("Resulting Version:", result.get("prompt_version"))
        
        # Verify it fell back and extracted the suggestion correctly
        self.assertEqual(result.get("suggestion"), "Launching common configurator on IEM")
        self.assertEqual(result.get("prompt_version"), "local_rule_engine_fallback")
        self.assertIn("Generated locally via Rule Engine", result.get("ai_answer"))

    def test_placeholder_post_processing(self):
        from app.services.style_guide_service import parse_openai_feedback
        original = "OPC UA Connector page opens displaying the below tabs:"
        
        placeholders = [
            "3. Suggested rewrite: [Keep Original Sentence]",
            "3. Suggested rewrite: Keep Original Sentence",
            "3. Suggested rewrite: Correct as is.",
            "3. Suggested rewrite: no change",
            "3. Suggested rewrite: [No changes needed]",
            "3. Original sentence: \"OPC UA Connector page opens displaying the below tabs:\"",
        ]
        
        for text in placeholders:
            _, _, suggestion = parse_openai_feedback(text, original_sentence=original)
            self.assertEqual(suggestion, original, f"Failed on: {text}")
            
        print("Placeholder post-processing tests passed!")

if __name__ == '__main__':
    unittest.main()

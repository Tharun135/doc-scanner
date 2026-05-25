import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure project root is in python path
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

class TestPrivacyRouting(unittest.TestCase):
    def setUp(self):
        # Clean env
        self.env_patcher = patch.dict(os.environ, {})
        self.env_patcher.start()
        
    def tearDown(self):
        self.env_patcher.stop()

    @patch('app.services.style_guide_service.select_model')
    @patch('app.services.style_guide_service.http_session.post')
    def test_allow_cloud_false_ollama_success(self, mock_post, mock_select_model):
        # Arrange
        os.environ["ALLOW_CLOUD_LLM"] = "false"
        os.environ["DOCSCANNER_MODE"] = "local"
        mock_select_model.return_value = "llama3"
        
        # Mock Ollama success response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "1. Issue detected: Test\n2. Explanation: Test\n3. Suggested rewrite: Test"}
        mock_post.return_value = mock_response

        # Act
        from app.services.style_guide_service import generate_style_suggestion
        result = generate_style_suggestion("This is a sentence.", "terminology")

        # Assert
        self.assertEqual(result["ai_answer"], "Generated locally via Ollama (llama3)")
        mock_post.assert_called_once()

    @patch('app.services.style_guide_service.http_session.post')
    def test_allow_cloud_false_ollama_failure_fail_closed(self, mock_post):
        # Arrange
        os.environ["ALLOW_CLOUD_LLM"] = "false"
        os.environ["DOCSCANNER_MODE"] = "local"
        
        # Mock Ollama error
        mock_post.side_effect = Exception("Ollama connection timed out")

        # Act
        from app.services.style_guide_service import generate_style_suggestion
        result = generate_style_suggestion("This is a sentence.", "terminology")

        # Assert
        self.assertEqual(result["prompt_version"], "fail_closed_error")
        self.assertIn("Fail closed error", result["ai_answer"])
        self.assertIn("Local model unavailable", result["ai_answer"])

    @patch('openai.OpenAI')
    @patch('app.services.style_guide_service.http_session.post')
    def test_allow_cloud_true_ollama_failure_openai_success(self, mock_post, mock_openai):
        # Arrange
        os.environ["ALLOW_CLOUD_LLM"] = "true"
        os.environ["OPENAI_API_KEY"] = "fake-key"
        os.environ["DOCSCANNER_MODE"] = "hybrid"
        
        # Mock Ollama error
        mock_post.side_effect = Exception("Ollama offline")
        
        # Mock OpenAI client response
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.output_text = "1. Issue detected: Test\n2. Explanation: Test\n3. Suggested rewrite: Test"
        mock_client.responses.create.return_value = mock_response

        # Act
        from app.services.style_guide_service import generate_style_suggestion
        result = generate_style_suggestion("This is a sentence.", "terminology")

        # Assert
        self.assertEqual(result["ai_answer"], "Generated via OpenAI (gpt-5.5) with local RAG grounding")
        mock_post.assert_called_once()
        mock_client.responses.create.assert_called_once()

if __name__ == '__main__':
    unittest.main()

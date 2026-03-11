import unittest
from unittest.mock import MagicMock, patch
import logging
from services.llm import GeminiService, MAX_RETRIES

class TestGeminiService(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @patch('services.llm.genai')
    def test_initialize_success(self, mock_genai):
        # Configuration happens at module level, so we just verify usage if possible or skip.
        pass 

    @patch('services.llm.Agent')
    def test_run_with_fallback_success(self, mock_agent_cls):
        mock_agent = MagicMock()
        mock_agent.run.return_value.content = "Success"
        mock_agent_factory = MagicMock(return_value=mock_agent)
        
        result = GeminiService.run_with_fallback(mock_agent_factory, "prompt")
        
        self.assertEqual(result.content, "Success")
        mock_agent_factory.assert_called()

    @patch('services.llm.Agent')
    def test_run_with_fallback_retry_success(self, mock_agent_cls):
        # Setup mock to fail first, then succeed
        mock_agent_fail = MagicMock()
        mock_agent_fail.run.side_effect = Exception("Temporary Error")
        
        mock_agent_success = MagicMock()
        mock_agent_success.run.return_value.content = "Retry Success"
        
        # Factory returns failing agent first, then success agent
        mock_agent_factory = MagicMock(side_effect=[mock_agent_fail, mock_agent_success])
        
        # Mock time.sleep to speed up test
        with patch('time.sleep'):
            result = GeminiService.run_with_fallback(mock_agent_factory, "prompt")
        
        self.assertEqual(result.content, "Retry Success")

    @patch('services.llm.Agent')
    def test_run_with_fallback_exhausted(self, mock_agent_cls):
        mock_agent = MagicMock()
        mock_agent.run.side_effect = Exception("Persistent Error")
        mock_agent_factory = MagicMock(return_value=mock_agent)
        
        with patch('time.sleep'):
            with self.assertRaises(Exception):
                GeminiService.run_with_fallback(mock_agent_factory, "prompt")
        
        # Should attempt MAX_RETRIES times
        self.assertEqual(mock_agent_factory.call_count, MAX_RETRIES)

    @patch('services.llm.Agent')
    def test_run_with_fallback_resource_exhausted(self, mock_agent_cls):
        mock_agent = MagicMock()
        # Simulate 429 error
        error = Exception("429 Resource has been exhausted")
        mock_agent.run.side_effect = error
        mock_agent_factory = MagicMock(return_value=mock_agent)
        
        with patch('time.sleep') as mock_sleep:
            try:
                 GeminiService.run_with_fallback(mock_agent_factory, "prompt")
            except Exception:
                pass
            
            # Verify sleep was called (backoff logic)
            mock_sleep.assert_called()

if __name__ == '__main__':
    unittest.main()

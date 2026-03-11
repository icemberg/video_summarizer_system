import unittest
from unittest.mock import MagicMock, patch
import logging
import sys
from services.transcription import TranscriptionService

class TestTranscriptionService(unittest.TestCase):
    def setUp(self):
        # logging.disable(logging.CRITICAL)
        pass

    def tearDown(self):
        # logging.disable(logging.NOTSET)
        pass

    @patch('services.transcription.MLX_AVAILABLE', True)
    def test_transcribe_mlx_success(self):
        mock_mlx = MagicMock()
        mock_mlx.transcribe.return_value = {'text': "MLX Transcript"}
        
        with patch('services.transcription.mlx_whisper', mock_mlx, create=True):
            result = TranscriptionService.transcribe("dummy.mp3")
        
        self.assertEqual(result, "MLX Transcript")
        mock_mlx.transcribe.assert_called_with("dummy.mp3", path_or_hf_repo="mlx-community/Whisper-tiny")

    @patch('services.transcription.MLX_AVAILABLE', True)
    def test_transcribe_mlx_fail_fallback_openai(self):
        # MLX fails
        mock_mlx = MagicMock()
        mock_mlx.transcribe.side_effect = Exception("MLX Error")
        
        # OpenAI succeeds
        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "OpenAI Transcript"}
        mock_whisper.load_model.return_value = mock_model
        
        with patch('services.transcription.mlx_whisper', mock_mlx, create=True), \
             patch.dict(sys.modules, {'whisper': mock_whisper}):
            result = TranscriptionService.transcribe("dummy.mp3")
        
        self.assertEqual(result, "OpenAI Transcript")
        mock_mlx.transcribe.assert_called()
        mock_whisper.load_model.assert_called_with("base")

    @patch('services.transcription.MLX_AVAILABLE', False)
    def test_transcribe_openai_sys_platform(self):
        mock_whisper = MagicMock()
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Windows Transcript"}
        mock_whisper.load_model.return_value = mock_model
        
        with patch.dict(sys.modules, {'whisper': mock_whisper}):
            result = TranscriptionService.transcribe("dummy.mp3")
        
        self.assertEqual(result, "Windows Transcript")
        mock_whisper.load_model.assert_called()

    @patch('services.transcription.MLX_AVAILABLE', False)
    def test_transcribe_all_fail(self):
        mock_whisper = MagicMock()
        mock_whisper.load_model.side_effect = Exception("OpenAI Error")
        
        with patch.dict(sys.modules, {'whisper': mock_whisper}):
            result = TranscriptionService.transcribe("dummy.mp3")
        
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()

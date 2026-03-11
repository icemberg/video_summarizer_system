import unittest
from unittest.mock import MagicMock, patch
import logging
from core.processor import VideoProcessor
from core.definitions import AnalysisResult

class TestVideoProcessor(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @patch('core.processor.YouTubeManager')
    @patch('core.processor.GeminiService')
    @patch('core.processor.TranscriptionService')
    @patch('core.processor.YouTubeTranscriptApi', create=True)
    def test_process_youtube_captions_available(self, mock_ytt_api, mock_transcription, mock_gemini, mock_youtube):
        processor = VideoProcessor()
        # Case: Captions found, direct analysis
        # YouTubeManager is used as class/static
        mock_youtube.extract_video_id.return_value = "vid123"
        mock_youtube.check_transcript_available.return_value = (True, "found")
        
        # Mock direct API fetch in processor.py
        mock_line = MagicMock()
        mock_line.text = "Hello world"
        mock_ytt_api.return_value.fetch.return_value = [mock_line]
        
        # GeminiService is used as class/static
        mock_gemini.run_with_fallback.return_value.content = "Analysis Result"
        
        result = processor.process_youtube("http://yt.com", "query")
        
        self.assertEqual(result.content, "Analysis Result")
        mock_youtube.download_audio.assert_not_called()

    @patch('core.processor.YouTubeManager')
    @patch('core.processor.GeminiService')
    @patch('core.processor.TranscriptionService')
    @patch('core.processor.AUDIO_DIR')
    def test_process_youtube_download_and_transcribe(self, mock_audio_dir, mock_transcription, mock_gemini, mock_youtube):
        # Case: No captions, must download
        mock_youtube.extract_video_id.return_value = "vid123"
        mock_youtube.check_transcript_available.return_value = (False, "missing")
        
        # Mock download returning a path (which is child of AUDIO_DIR usually, but here checking return value usage)
        # In process_youtube, audio_path = YouTubeManager.download_audio(url)
        # Then if audio_path.exists()...
        # We need audio_path to be a mock with .exists() == True
        mock_audio_path = MagicMock()
        mock_audio_path.exists.return_value = True
        mock_youtube.download_audio.return_value = mock_audio_path
        
        # TranscriptionService is used as instance.
        mock_transcription.return_value.transcribe.return_value = "Transcribed Text"
        mock_gemini.run_with_fallback.return_value.content = "Analysis Result"
        
        processor = VideoProcessor()
        result = processor.process_youtube("http://yt.com", "query")
        
        self.assertEqual(result.content, "Analysis Result")
        mock_youtube.download_audio.assert_called()
        mock_transcription.return_value.transcribe.assert_called()
        mock_audio_path.unlink.assert_called() # Check cleanup

    @patch('core.processor.genai')
    @patch('core.processor.MediaManager')
    @patch('core.processor.GeminiService')
    @patch('core.processor.TranscriptionService')
    @patch('core.processor.AUDIO_DIR')
    def test_process_upload_success(self, mock_audio_dir, mock_transcription, mock_gemini, mock_media, mock_genai):
        # Case: Upload -> Extract -> Transcribe -> Analyze
        mock_media.extract_audio.return_value = True
        
        # Mock AUDIO_DIR / ... -> audio_path
        mock_audio_path = MagicMock()
        mock_audio_path.exists.return_value = True
        mock_audio_dir.__truediv__.return_value = mock_audio_path
        
        # TranscriptionService instance mock
        mock_transcription.return_value.transcribe.return_value = "Video Transcript"
        
        mock_gemini.run_with_fallback.return_value.content = "Upload Analysis"
        
        # Mock genai upload
        mock_genai.upload_file.return_value = MagicMock()
        
        processor = VideoProcessor()
        with patch('pathlib.Path.unlink'):
            result = processor.process_upload("video.mp4", "query")
            
        self.assertEqual(result.content, "Upload Analysis")
        mock_media.extract_audio.assert_called()
        mock_transcription.return_value.transcribe.assert_called()

from pathlib import Path

if __name__ == '__main__':
    unittest.main()

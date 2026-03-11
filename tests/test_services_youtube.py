import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import logging
from services.youtube import YouTubeManager

class TestYouTubeManager(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_extract_video_id(self):
        self.assertEqual(YouTubeManager.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        self.assertEqual(YouTubeManager.extract_video_id("https://youtu.be/dQw4w9WgXcQ"), "dQw4w9WgXcQ")
        self.assertIsNone(YouTubeManager.extract_video_id("invalid_url"))

    @patch('services.youtube.YouTubeTranscriptApi')
    def test_check_transcript_available_manual(self, mock_api_cls):
        mock_api_instance = mock_api_cls.return_value
        
        # Create a mock transcript object
        t1 = MagicMock()
        t1.is_generated = False
        
        mock_api_instance.list.return_value = [t1]
        
        is_avail, msg = YouTubeManager.check_transcript_available("vid_id")
        self.assertTrue(is_avail)
        self.assertIn("Manually created", msg)

    @patch('services.youtube.YouTubeTranscriptApi')
    def test_check_transcript_available_generated(self, mock_api_cls):
        mock_api_instance = mock_api_cls.return_value
        
        # Create a mock transcript object
        t1 = MagicMock()
        t1.is_generated = True
        
        mock_api_instance.list.return_value = [t1]
        
        is_avail, msg = YouTubeManager.check_transcript_available("vid_id")
        self.assertTrue(is_avail)
        self.assertIn("Auto-generated", msg)

    @patch('services.youtube.YouTubeTranscriptApi')
    def test_check_transcript_none(self, mock_api_cls):
        mock_api_instance = mock_api_cls.return_value
        mock_api_instance.list.return_value = []
        
        is_avail, msg = YouTubeManager.check_transcript_available("vid_id")
        self.assertFalse(is_avail)

    @patch('services.youtube.yt_dlp')
    @patch('services.youtube.shutil.which')
    def test_download_audio_success(self, mock_which, mock_ytdlp):
        mock_which.return_value = "/usr/bin/ffmpeg"
        
        # Mock context manager
        mock_ydl_instance = MagicMock()
        mock_ytdlp.YoutubeDL.return_value.__enter__.return_value = mock_ydl_instance
        
        # Mock Path.glob to return a simulated downloaded file
        from pathlib import Path
        mock_file = Path("/fake/dir/yt_1234.m4a")
        with patch('pathlib.Path.glob', return_value=[mock_file]):
            result = YouTubeManager.download_audio("http://url")
            
        self.assertIsNotNone(result)
        self.assertEqual(result, mock_file)
        mock_ydl_instance.download.assert_called_with(["http://url"])

    @patch('services.youtube.shutil.which')
    def test_download_audio_no_ffmpeg(self, mock_which):
        mock_which.return_value = None
        result = YouTubeManager.download_audio("http://url")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()

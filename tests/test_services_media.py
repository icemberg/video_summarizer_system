import unittest
from unittest.mock import MagicMock, patch
import logging
from services.media import MediaManager

class TestMediaManager(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @patch('services.media.shutil.which')
    def test_is_ffmpeg_available_true(self, mock_which):
        mock_which.return_value = "/usr/bin/ffmpeg"
        self.assertTrue(MediaManager.check_ffmpeg_available())

    @patch('services.media.subprocess.run')
    def test_is_ffmpeg_available_false(self, mock_subprocess):
        mock_subprocess.return_value.returncode = 1
        self.assertFalse(MediaManager.check_ffmpeg_available())

    @patch('services.media.subprocess.run')
    @patch('services.media.shutil.which')
    def test_extract_audio_success(self, mock_which, mock_subprocess):
        mock_which.return_value = "/bin/ffmpeg"
        mock_subprocess.return_value.returncode = 0
        
        result = MediaManager.extract_audio("input.mp4", "output.mp3")
        
        self.assertTrue(result)
        mock_subprocess.assert_called()

    @patch('services.media.shutil.which')
    def test_extract_audio_fail_no_ffmpeg(self, mock_which):
        mock_which.return_value = None
        result = MediaManager.extract_audio("input.mp4", "output.mp3")
        self.assertFalse(result)

    @patch('services.media.subprocess.run')
    @patch('services.media.shutil.which')
    def test_extract_audio_fail_subprocess(self, mock_which, mock_subprocess):
        mock_which.return_value = "/bin/ffmpeg"
        mock_subprocess.side_effect = Exception("FFmpeg failed")
        
        result = MediaManager.extract_audio("input.mp4", "output.mp3")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()

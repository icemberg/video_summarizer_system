import unittest
from unittest.mock import MagicMock, patch
import logging
from ui.state import init_state, save_uploaded_file, cleanup_file

class TestUIState(unittest.TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @patch('ui.state.st')
    def test_init_state(self, mock_st):
        # Setup session state as a MagicMock that behaves like a dict but allows attribute access
        mock_state = MagicMock()
        mock_state.__contains__.side_effect = lambda key: False # Simulate empty
        mock_st.session_state = mock_state
        
        init_state()
        
        # Check if messages list was assigned
        self.assertTrue(hasattr(mock_state, 'messages'))

    @patch('ui.state.tempfile.NamedTemporaryFile')
    def test_save_uploaded_file(self, mock_temp):
        mock_file = MagicMock()
        mock_file.name = "test.mp4"
        mock_file.read.return_value = b"data"
        
        # Mock context manager for NamedTemporaryFile
        mock_tmp_ctx = MagicMock()
        mock_temp.return_value.__enter__.return_value = mock_tmp_ctx
        mock_tmp_ctx.name = "temp_path.mp4"
        
        result = save_uploaded_file(mock_file)
        
        self.assertEqual(result, "temp_path.mp4")
        mock_tmp_ctx.write.assert_called_with(b"data")

    @patch('ui.state.os.remove')
    @patch('ui.state.os.path.exists')
    def test_cleanup_file(self, mock_exists, mock_remove):
        mock_exists.return_value = True
        
        cleanup_file("some/path")
        
        mock_remove.assert_called_with("some/path")

if __name__ == '__main__':
    unittest.main()

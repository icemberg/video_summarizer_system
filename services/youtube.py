import re
import uuid
import shutil
from pathlib import Path
from typing import Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

from utils.logger import get_logger
from config import AUDIO_DIR

logger = get_logger(__name__)

class YouTubeManager:
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r"(?:v=|/videos/|embed/|youtu\.be/|/live/|/shorts/)([A-Za-z0-9_-]{6,})",
            r"youtu\.be/([A-Za-z0-9_-]{6,})",
            r"youtube\.com/shorts/([A-Za-z0-9_-]{6,})",
            r"youtube\.com/live/([A-Za-z0-9_-]{6,})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def check_transcript_available(video_id: str) -> Tuple[bool, str]:
        """
        Check if a transcript is available via the API.
        Returns (is_available, message).
        """
        try:
            logger.info(f"Listing transcripts for {video_id}")
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            
            manually_created = [t for t in transcript_list if not t.is_generated]
            generated = [t for t in transcript_list if t.is_generated]
            
            if manually_created:
                return True, "Manually created captions available"
            if generated:
                return True, "Auto-generated captions available"
            return False, "No captions found"
        except Exception as e:
            logger.error(f"Error checking transcript: {e}")
            return False, str(e)

    @staticmethod
    def download_audio(url: str) -> Optional[Path]:
        """
        Download audio from YouTube using yt-dlp to a temp file.
        Returns the path to the downloaded file or None.
        """
        try:
            logger.info(f"Attempting to download audio from {url}")
            temp_id = str(uuid.uuid4())[:8]
            output_path = AUDIO_DIR / f"yt_{temp_id}" # yt-dlp adds extension
            
            ffmpeg_path = shutil.which("ffmpeg")
            logger.info(f"FFmpeg path resolved to: {ffmpeg_path}")
            
            if not ffmpeg_path:
                logger.error("FFmpeg not found in PATH conversation")
                return None

            class YDLLogger:
                def debug(self, msg):
                    if msg.startswith('[debug] '):
                        logger.debug(msg)
                    else:
                        self.info(msg)
                def info(self, msg):
                    if msg.startswith('[download]') and '%' in msg:
                        import sys
                        sys.stdout.write(f"\r{msg:<100}")
                        sys.stdout.flush()
                    else:
                        logger.info(msg)
                def warning(self, msg): logger.warning(msg)
                def error(self, msg): logger.error(msg)

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f"yt_{temp_id}.%(ext)s",
                'paths': {'home': str(AUDIO_DIR)}, # Use native string path
                'ffmpeg_location': str(Path(ffmpeg_path).parent), # Directory is often safer
                'logger': YDLLogger(),
                'verbose': True, # Enable verbose for more debug info in our logs
                'noplaylist': True, # CRITICAL: Prevent downloading entire playlists to a single temp file
                'fixup': 'never', # Prevent FixupM4a container correction entirely
            }
            
            logger.info(f"Initialized yt-dlp options with home path: {AUDIO_DIR}. Starting download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Since we use 'best' codec, the extension could be .webm, .m4a, or .mp3
            # We search for the file beginning with the temp_id
            downloaded_files = list(AUDIO_DIR.glob(f"yt_{temp_id}.*"))
            if downloaded_files:
                final_path = downloaded_files[0]
                logger.info(f"Download successful: {final_path}")
                return final_path
            
            logger.error(f"Download finished but file not found at {final_path}")
            return None

        except Exception as e:
            logger.error(f"Download failed with error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None


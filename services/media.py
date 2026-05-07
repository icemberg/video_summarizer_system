import shutil
import subprocess
from pathlib import Path
from utils.logger import get_logger
import mlx_whisper


logger = get_logger(__name__)

class MediaManager:
    @staticmethod
    def check_ffmpeg_available() -> bool:
        """Check if ffmpeg is available in the system path."""
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
            available = result.returncode == 0
            if available:
                logger.info("FFmpeg is available.")
            else:
                logger.warning("FFmpeg command failed.")
            return available
        except Exception as e:
            logger.error(f"Error checking FFmpeg: {e}")
            return False

    @staticmethod
    def extract_audio(video_path: str, output_path: str) -> bool:
        """
        Extract audio from video file using ffmpeg.
        Falls back to moviepy if ffmpeg fails (though moviepy usually relies on ffmpeg).
        """
        logger.info(f"Extracting audio from {video_path} to {output_path}")
        try:
            # Try ffmpeg first
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", video_path, "-vn",
                    "-acodec", "libmp3lame", "-q:a", "2",
                    output_path
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except subprocess.CalledProcessError:
            logger.warning("FFmpeg extraction failed. Trying moviepy fallback...")
            try:
                from moviepy import VideoFileClip
                clip = VideoFileClip(video_path)
                clip.audio.write_audiofile(output_path, logger=None)
                clip.close()
                return True
            except Exception as e:
                logger.error(f"MoviePy fallback failed: {e}")
                return False
        except Exception as e:
            logger.error(f"Audio extraction error: {e}")
            return False

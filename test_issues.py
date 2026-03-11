import traceback
import sys
import logging
from utils.logger import get_logger
from services.youtube import YouTubeManager
from youtube_transcript_api import YouTubeTranscriptApi

logging.basicConfig(level=logging.DEBUG)

print("Methods in YouTubeTranscriptApi:")
print(dir(YouTubeTranscriptApi))
try:
    print(getattr(YouTubeTranscriptApi, 'list_transcripts'))
except Exception as e:
    print("Error getting list_transcripts:", e)

print("Testing download...")
res = YouTubeManager.download_audio("https://www.youtube.com/watch?v=1vB7VjB20cc")
print("Download result:", res)

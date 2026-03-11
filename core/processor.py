import time
import google.generativeai as genai
from pathlib import Path
import shutil
from services.media import MediaManager
from services.youtube import YouTubeManager
from services.transcription import TranscriptionService
from services.llm import GeminiService
from utils.logger import get_logger
from config import AUDIO_DIR
from core.definitions import AnalysisResult
from youtube_transcript_api import YouTubeTranscriptApi

logger = get_logger(__name__)

class VideoProcessor:
    def __init__(self):
        self.transcription_service = TranscriptionService()

    def _get_agent_factory(self, tools=None, instructions=None):
        def factory(model_id):
            return GeminiService.create_agent(
                model_id=model_id,
                tools=tools,
                instructions=instructions or ["Analyze video content."]
            )
        return factory

    def process_upload(self, video_path: str, query: str) -> AnalysisResult:
        """
        Workflow 1: Upload -> Extract -> Transcribe -> Analyze
        """
        logger.info(f"Processing upload: {video_path}")
        
        # 1. Extract Audio
        audio_path = AUDIO_DIR / f"{Path(video_path).stem}.mp3"
        MediaManager.extract_audio(video_path, str(audio_path))

        # 2. Transcribe
        transcript = None
        if audio_path.exists():
            transcript = self.transcription_service.transcribe(str(audio_path))
        
        # 3. Analyze
        if transcript:
            prompt = (
                f"Summarize this transcript and answer the user's query:\n\n"
                f"{transcript}\n\nUser question: {query}\n\n"
                f"Provide a detailed, user-friendly, and actionable response."
            )
            response = GeminiService.run_with_fallback(self._get_agent_factory(), prompt)
            return AnalysisResult(content=response.content)
        else:
             # Fallback to multimodal analysis
             # Upload video file to Gemini
             logger.info("Uploading video to Gemini for multimodal analysis...")
             processed_video = genai.upload_file(video_path)
             while processed_video.state.name == "PROCESSING":
                 time.sleep(1)
                 processed_video = genai.get_file(processed_video.name)
            
             prompt = (
                 f"Analyze the uploaded video for content and context.\n"
                 f"Respond to the following query using video insights:\n{query}\n"
                 f"Provide a detailed, user-friendly, and actionable response."
             )
             
             # Pass video file to run_with_fallback
             response = GeminiService.run_with_fallback(
                 self._get_agent_factory(), 
                 prompt, 
                 videos=[processed_video]
             )
             return AnalysisResult(content=response.content)

    def process_youtube(self, url: str, query: str) -> AnalysisResult:
        """
        Workflow 2: URL -> Check Captions -> (Download) -> Transcribe -> Analyze
        """
        logger.info(f"Starting YouTube processing for URL: {url}")
        
        video_id = YouTubeManager.extract_video_id(url)
        if not video_id:
            logger.error("Failed to extract video ID")
            return AnalysisResult(content="Invalid YouTube URL")
        
        logger.info(f"Extracted video ID: {video_id}")

        # 1. Check Captions
        logger.info("Checking for captions...")
        has_captions, msg = YouTubeManager.check_transcript_available(video_id)
        logger.info(f"Captions available: {has_captions} ({msg})")
        
        transcript = None
        if has_captions:
            logger.info("Attempting to fetch captions directly via API...")
            try:
                ytt_api = YouTubeTranscriptApi()
                captions_list = ytt_api.fetch(video_id)
                transcript = " ".join([line.text for line in captions_list])
                logger.info("Successfully fetched captions via API.")
            except Exception as e:
                logger.warning(f"Failed to fetch captions directly despite availability: {e}")
                transcript = None

        if not transcript:
            # 2. Download & Transcribe (Fallback for missing/restricted captions)
            logger.info("Captions missing or restricted. Falling back to downloading audio...")
            audio_path = YouTubeManager.download_audio(url)
            if not audio_path:
                logger.error("Failed to download audio")
                return AnalysisResult(content="Failed to download audio from YouTube (or ffmpeg missing).")
            
            logger.info(f"Audio downloaded to {audio_path}. Starting transcription...")
            transcript = self.transcription_service.transcribe(str(audio_path))
            logger.info(f"Transcription result: {'Success' if transcript else 'Failure'}")
            
            # Cleanup
            try:
                if audio_path.exists():
                    logger.info("Cleaning up temp audio file")
                    audio_path.unlink()
            except Exception as e: 
                logger.warning(f"Failed to delete temp audio: {e}")

        if transcript:
            logger.info("Analyzing transcript...")
            prompt = (
                f"Summarize this YouTube video transcript and answer the user's query:\n\n"
                f"Transcript:\n{transcript}\n\n"
                f"User question: {query}\n\n"
                f"Provide a detailed, user-friendly, and actionable response."
            )
            response = GeminiService.run_with_fallback(self._get_agent_factory(), prompt)
            return AnalysisResult(content=response.content)
        else:
            logger.warning("Transcription failed. Falling back to metadata analysis.")
            # Last resort: Agent only analysis without transcript
            prompt = (
                f"The user provided this YouTube link: {url}\n"
                f"Unfortunately, captions are not available and audio transcription failed.\n"
                f"Please provide analysis based on video title, description, and web search.\n"
                f"User query: {query}"
            )
            response = GeminiService.run_with_fallback(self._get_agent_factory(), prompt)
            return AnalysisResult(content=response.content)

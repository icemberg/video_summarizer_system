import sys
import warnings
from utils.logger import get_logger

logger = get_logger(__name__)

# Check for MLX (Only on macOS)
try:
    if sys.platform != "darwin":
        logger.info(f"MLX disabled: Not running on macOS (current: {sys.platform})")
        MLX_AVAILABLE = False
    else:
        import mlx_whisper
        MLX_AVAILABLE = True
        logger.info("MLX Whisper is available.")
except ImportError:
    MLX_AVAILABLE = False
    logger.info("MLX Whisper not installed.")

class TranscriptionService:
    @staticmethod
    def transcribe(audio_path: str) -> str:
        """
        Transcribe audio using the best available Whisper implementation.
        Priority: MLX Whisper -> OpenAI Whisper
        """
        transcript = None
        logger.info(f"Starting transcription for {audio_path}")
        logger.info(f"MLX_AVAILABLE: {MLX_AVAILABLE}")
        
        # 1. Try MLX Whisper
        if MLX_AVAILABLE:
            try:
                logger.info("Entering MLX Whisper block...")
                logger.info("Attempting transcription with MLX Whisper (mlx_whisper.transcribe)...")
                # Add validation that it doesn't hang
                import time
                start_time = time.time()
                result = mlx_whisper.transcribe(audio_path, path_or_hf_repo="mlx-community/Whisper-tiny")
                end_time = time.time()
                logger.info(f"MLX Whisper returned in {end_time - start_time:.2f}s")
                
                if isinstance(result, dict) and 'text' in result:
                    transcript = result['text']
                else:
                    transcript = str(result)
                
                logger.info(f"MLX Result type: {type(result)}")
                
                if transcript:
                    logger.info("MLX Whisper transcription successful")
                    return transcript
            except Exception as e:
                logger.warning(f"MLX Whisper failed with error: {e}")
                import traceback
                logger.warning(traceback.format_exc())

        # 2. Fallback to OpenAI Whisper
        if not transcript:
            try:
                import whisper
                import ssl
                
                # WORKAROUND: Fix for SSL: UNEXPECTED_EOF_WHILE_READING
                # This often happens in corporate environments or with missing local certs
                try:
                    ssl._create_default_https_context = ssl._create_unverified_context
                    logger.info("Applied SSL workaround for Whisper download.")
                except AttributeError:
                    pass

                logger.info("Falling back to OpenAI Whisper...")
                logger.info("Loading OpenAI Whisper 'base' model...")
                # Lazy load model
                model = whisper.load_model("base")
                logger.info("Model loaded. Starting transcription...")
                result = model.transcribe(audio_path)
                transcript = result["text"]
                if transcript:
                    logger.info("OpenAI Whisper transcription successful")
                    return transcript
            except ImportError:
                logger.error("OpenAI Whisper not installed")
            except Exception as e:
                logger.error(f"OpenAI Whisper failed: {e}")
                import traceback
                logger.error(traceback.format_exc())

        logger.info("Transcription finished (result: {})".format("Success" if transcript else "Failure"))
        return transcript

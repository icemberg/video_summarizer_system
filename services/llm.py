import time
import random
import google.generativeai as genai
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.youtube_tools import YouTubeTools
from config import GOOGLE_API_KEY, MAX_RETRIES, BASE_BACKOFF
from utils.logger import get_logger

logger = get_logger(__name__)

if GOOGLE_API_KEY:
    logger.info(f"Using API Key: {GOOGLE_API_KEY[:10]}...")
    # Force reset the client in case Streamlit kept the old one in memory
    genai.configure(api_key=GOOGLE_API_KEY)
    genai._default_client = None 
    genai.configure(api_key=GOOGLE_API_KEY)

class GeminiService:
    @staticmethod
    def get_available_models(exclude=None):
        if exclude is None:
            exclude = set()
        models = []
        try:
            all_models = genai.list_models()
            for m in all_models:
                name = getattr(m, "name", "")
                if "gemini" in name.lower() and name not in exclude:
                    models.append(name)
        except Exception as e:
            logger.error(f"Error listing models: {e}")
        return models or ["gemini-1.5-flash"]

    @staticmethod
    def select_model(exclude_models=None):
        available = GeminiService.get_available_models(exclude_models)
        # Simple selection: first available
        return available[0] if available else "gemini-1.5-flash"

    @staticmethod
    def create_agent(model_id: str, tools=None, instructions=None):
        return Agent(
            model=Gemini(id=model_id),
            tools=tools or [],
            instructions=instructions or [],
            show_tool_calls=True,
            markdown=True,
        )

    @staticmethod
    def is_rate_limit_error(error) -> tuple[bool, int | None]:
        msg = str(error).lower()
        if "429" in msg or "rate limit" in msg or "quota" in msg:
            return True, None
        return False, None

    @staticmethod
    def run_with_fallback(agent_factory, prompt, **kwargs):
        """
        Executes agent run with retry logic as described in README.
        agent_factory:() -> Agent (recreated on rotation)
        """
        used_models = set()
        current_model = GeminiService.select_model() # Initial selection logic should be passed in or handled by factory, simplified here
        
        # We need to manage the agent instance ourselves to support rotation
        agent = agent_factory(current_model)

        for attempt in range(MAX_RETRIES):
            try:
                response = agent.run(prompt, **kwargs)
                response_text = response.content if hasattr(response, 'content') else str(response)
                
                if not response_text or not response_text.strip():
                    raise ValueError("Empty response from agent")
                
                return response
            
            except Exception as e:
                is_rate, retry_after = GeminiService.is_rate_limit_error(e)
                logger.warning(f"Attempt {attempt+1} failed: {e}")

                if is_rate or "empty response" in str(e).lower():
                    used_models.add(current_model)
                    current_model = GeminiService.select_model(exclude_models=used_models)
                    logger.info(f"Rotating to model: {current_model}")
                    
                    wait_time = retry_after if retry_after else (BASE_BACKOFF * (2 ** attempt) + random.random())
                    time.sleep(wait_time)
                    
                    # Recreate agent with new model
                    agent = agent_factory(current_model)
                else:
                    if attempt == MAX_RETRIES - 1:
                        raise e
                    # For non-rate-limit errors, we might still want to retry or rotate
                    # conforming to strict flow: "Generic error: try to rotate model"
                    used_models.add(current_model)
                    current_model = GeminiService.select_model(exclude_models=used_models)
                    agent = agent_factory(current_model)

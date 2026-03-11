import os
import streamlit as st

# WORKAROUND: Fix for Streamlit + PyTorch "RuntimeError: Tried to instantiate class '__path__._path'"
# This error occurs when Streamlit's file watcher inspects PyTorch internal classes.
# We set the watcher to 'poll' or 'none' to avoid this, though 'poll' is often sufficient.
# Alternatively, we can rely on the user to run with --server.fileWatcherType=poll
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "poll"

from config import GOOGLE_API_KEY
from core.processor import VideoProcessor
from ui.state import init_state, save_uploaded_file, cleanup_file
from ui.components import render_dependency_status, render_model_info
from services.llm import GeminiService

# Page Config
st.set_page_config(
    page_title="Multimodal AI Agent- Video Summarizer",
    page_icon="🎥",
    layout="wide"
)

st.title("Phidata Video AI Summarizer Agent 🎥🎤🖬")
st.header("Powered by Gemini 2.0 Flash Exp (Refactored)")

# Initialize State
init_state()

# Dependencies
render_dependency_status()

# Model Initialization
if "current_model" not in st.session_state:
    st.session_state.current_model = GeminiService.select_model()
if "used_models" not in st.session_state:
    st.session_state.used_models = set()

render_model_info()

# Processor
processor = VideoProcessor()

# UI Layout
video_file = st.file_uploader(
    "Upload a video file", type=['mp4', 'mov', 'avi'], help="Upload a video for AI analysis"
)

youtube_url = st.text_input(
    "Or enter a YouTube video URL to summarize",
    placeholder="https://www.youtube.com/watch?v=...",
    help="Provide a YouTube link to analyze using online sources (no download).",
)

# 1. Video Upload Flow
if video_file:
    video_path = save_uploaded_file(video_file)
    st.video(video_path, format="video/mp4", start_time=0)

    user_query = st.text_area(
        "What insights are you seeking from the video?",
        placeholder="Ask anything about the video content.",
        help="Provide specific questions or insights you want from the video."
    )

    if st.button("🔍 Analyze Video", key="analyze_video_button"):
        if not user_query:
            st.warning("Please enter a question or insight to analyze.")
        else:
            try:
                with st.spinner("Processing video and gathering insights..."):
                    result = processor.process_upload(video_path, user_query)
                st.subheader("Analysis Result")
                st.markdown(result.content)
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                cleanup_file(video_path)

# 2. YouTube Flow
elif youtube_url:
    user_query_yt = st.text_area(
        "What insights are you seeking from the YouTube video?",
        placeholder="Ask anything about the video content.",
        help="Provide specific questions or insights you want from the video.",
        key="yt_text_area",
    )

    if st.button("🔗 Summarize YouTube", key="summarize_youtube_button"):
        if not user_query_yt:
            st.warning("Please enter a question or insight to analyze.")
        else:
            try:
                # We can't easily show step-by-step progress like "Checking captions" 
                # inside the processor without callbacks, but st.spinner covers general wait.
                # For better UX, we could inject a callback, but keeping it simple for now.
                with st.spinner("Analyzing YouTube video (checking captions, downloading if needed)..."):
                    result = processor.process_youtube(youtube_url, user_query_yt)
                
                st.subheader("Analysis Result")
                st.markdown(result.content)
            except Exception as e:
                st.error(f"An error occurred: {e}")

else:
    st.info("Upload a video file or enter a YouTube URL to begin.")

# Style
st.markdown(
    """
    <style>
    .stTextArea textarea {
        height: 100px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

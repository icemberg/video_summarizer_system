import streamlit as st
from services.media import MediaManager
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    import mlx_whisper
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False

def render_dependency_status():
    """Renders the standard dependency status expander."""
    ffmpeg_ok = MediaManager.check_ffmpeg_available()
    
    with st.expander("🔧 Dependency Status"):
        cols = st.columns(2)
        with cols[0]:
            st.write("**Installed Packages:**")
            st.write(f"- yt-dlp: {'✅' if YT_DLP_AVAILABLE else '❌'}")
            st.write(f"- OpenAI Whisper: ⏳ (lazy load)")
            st.write(f"- MLX Whisper: {'✅' if MLX_AVAILABLE else '❌'}")
        with cols[1]:
            st.write("**System Tools:**")
            st.write(f"- FFmpeg: {'✅' if ffmpeg_ok else '❌'}")
        
        if not ffmpeg_ok:
            st.error("❌ FFmpeg is not detected. This will cause YouTube transcription to fail.")
            st.code("""
# Install FFmpeg on Windows:
winget install -e --id Gyan.FFmpeg
# Verify installation:
ffmpeg -version
            """, language="bash")

def render_model_info():
    if "current_model" in st.session_state:
        st.info(f"Using model: {st.session_state.current_model}")

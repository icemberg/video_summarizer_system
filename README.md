# 🎥 Phidata Video AI Summarizer Agent

A powerful AI-driven video summarization tool that leverages Google's Gemini models with automatic failover, YouTube audio transcription, and intelligent caption detection.

---

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [Workflow Explanation](#workflow-explanation)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)

---

## ✨ Features

### Core Capabilities
- 🎬 **Video Upload & Analysis** - Upload MP4, MOV, or AVI files for AI-powered analysis
- 🔗 **YouTube URL Support** - Analyze videos directly from YouTube URLs
- 🤖 **Multi-Modal AI** - Uses Google Gemini models with automatic model rotation
- 🔄 **Automatic Quota Management** - Detects API quota limits and switches to available models
- 🎙️ **Smart Transcription Fallback** - Multiple transcription strategies (captions → MLX → Whisper)
- 🌐 **Web Research Integration** - Agent performs DuckDuckGo searches for context
- 💾 **Session State Management** - Remembers model usage and quota limits per session

### Transcription Chain
1. **YouTube Captions** - Attempts to fetch video captions first
2. **MLX Whisper** (optional) - Uses MLX-optimized Whisper if available
3. **OpenAI Whisper** - Falls back to local Whisper transcription
4. **Web Search** - Uses agent's DuckDuckGo tool for metadata analysis

### Error Handling
- ✅ Automatic detection of API 429 quota errors
- ✅ Intelligent model switching (up to 5 attempts)
- ✅ Missing caption detection and automatic transcription
- ✅ Dependency validation at startup
- ✅ Graceful fallbacks for missing tools

---

## 🚀 Installation

### Prerequisites
- Python 3.10+
- Git
- FFmpeg (for audio extraction)

### Step 1: Clone/Setup Project

```bash
cd "c:\Users\ASUS\all python files\video summarizer"
```

### Step 2: Create Virtual Environment

```bash
python -m venv visum
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
& "visum\Scripts\Activate.ps1"
```

**Windows (CMD):**
```cmd
visum\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source visum/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Install FFmpeg

**Windows (via WinGet):**
```powershell
winget install -e --id Gyan.FFmpeg
```

**Windows (via Chocolatey):**
```bash
choco install ffmpeg
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### Step 6: Install PyTorch (CPU-only)

```bash
pip uninstall -y torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Step 7: Set Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
PHIDATA_API_KEY=your_phidata_api_key_here  # Optional: For Phidata Agent dashboard features
```

**Get your Google API key:** [Google AI Studio](https://ai.google.dev/)
**Get your Phidata API key:** [Phidata](https://phidata.com/) (Optional)

---

## 🎯 Quick Start

### 1. Run the App

```powershell
# Activate your environment if it isn't already
& "visum\Scripts\Activate.ps1"

# Start the Streamlit server
streamlit run app.py
```

The app will open at `http://localhost:8501`

### 2. Run the Test Suite (Optional)

To verify that your installation (ffmpeg, tools, api) is correctly set up:
```powershell
python run_tests.py
```

### Example Usage

1. **Upload a Video:**
   - Click "Upload a video file"
   - Select MP4/MOV/AVI file
   - Watch the preview
   - Enter your question in the text area
   - Click "🔍 Analyze Video"

2. **Analyze YouTube Video:**
   - Paste a YouTube URL in the text field
   - Enter your question
   - Click "🔗 Summarize YouTube"
   - App automatically downloads and transcribes if captions unavailable

---

## 📖 Usage Guide

### Video Upload Workflow

```
1. User uploads video file
   ↓
2. File saved to temp location
   ↓
3. Video preview displayed
   ↓
4. User enters analysis query
   ↓
5. Video uploaded to Google Generative AI
   ↓
6. Audio extracted (ffmpeg/moviepy)
   ↓
7. Whisper transcribes audio
   ↓
8. Agent analyzes transcript + query
   ↓
9. Response displayed (auto-switches models on quota)
   ↓
10. Temp files cleaned up
```

### YouTube URL Workflow

```
1. User enters YouTube URL + query
   ↓
2. Agent attempts web search + caption extraction
   ↓
3. If captions found → return response
   ↓
4. If captions missing → detect via response check
   ↓
5. Download audio with yt-dlp + ffmpeg
   ↓
6. Transcribe with Whisper
   ↓
7. Re-analyze with transcript
   ↓
8. Display final response
```

### Model Selection

The app automatically:
- Lists all available Gemini models
- Selects one with "generateContent" support
- Tracks which models have hit quota limits
- Rotates to next available model on 429 errors
- Retries up to 5 times before giving up

---

## 🔄 Workflow Explanation

### 1️⃣ Initialization Phase

```
┌─────────────────────────────────────┐
│  Check Available Dependencies       │
├─────────────────────────────────────┤
│ • MLX Whisper (optional)            │
│ • yt-dlp (YouTube download)         │
│ • ffmpeg (audio extraction)         │
│ • OpenAI Whisper (lazy load)        │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Initialize Google Gemini API       │
├─────────────────────────────────────┤
│ • Load API key from .env            │
│ • Configure genai client            │
│ • List available models             │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  Set Up Streamlit Session State     │
├─────────────────────────────────────┤
│ • current_model: active Gemini      │
│ • used_models: quota-exhausted set  │
│ • Display status to user            │
└─────────────────────────────────────┘
```

### 2️⃣ Model Selection & Rotation

**Function: `select_gemini_model(exclude_models=None)`**

```
Input: Set of models to skip (quota-exhausted)
   ↓
Query genai.list_models()
   ↓
Loop 1: Find Gemini model with "generateContent" support
        (Excludes models in exclude_models set)
   ↓
If not found, Loop 2: Find ANY Gemini model not excluded
   ↓
If still not found, Fallback: "gemini-1.5-flash"
   ↓
Output: Selected model name (e.g., "models/gemini-2.5-flash")
```

### 3️⃣ Agent Run with Automatic Failover

**Function: `run_agent_with_fallback(agent, prompt, max_retries=5)`**

```
for attempt in 1..5:
   ├─ CALL: agent.run(prompt)
   │   ↓
   ├─ Wait for response
   │   ↓
   ├─ Check response for ERROR INDICATORS:
   │   [429, quota, exceeded, rate limit, error occurred]
   │   ↓
   ├─ IF ERROR DETECTED:
   │   ├─ Add current model to used_models
   │   ├─ Select next available model
   │   ├─ Reinitialize agent with new model
   │   ├─ Show user: "Switched to [model_name]"
   │   └─ Retry same prompt
   │   ↓
   ├─ ELIF SUCCESS (no error):
   │   └─ Return response immediately
   │   ↓
   └─ ON EXCEPTION:
       ├─ Same model-switching logic
       └─ Retry with next model

Output: First successful response or error after 5 attempts
```

### 4️⃣ Transcription Fallback Chain

```
User uploads video/YouTube URL
   ↓
1st OPTION: YouTubeTools (captions extraction)
   └─ Returns immediately if successful
   ↓
2nd OPTION: MLXTranscribe (if installed)
   ├─ Extracts audio from video
   ├─ Transcribes with mlx_whisper
   └─ Returns if successful
   ↓
3rd OPTION: OpenAI Whisper
   ├─ Downloads YouTube audio with yt-dlp + ffmpeg
   ├─ Transcribes with local Whisper "base" model
   └─ Returns if successful
   ↓
4th OPTION: Fallback to agent response
   └─ Use whatever the model provides
```

### 5️⃣ Error Handling Layers

```
┌─────────────────────────────────────────┐
│   LAYER 1: API Quota (429 errors)       │
├─────────────────────────────────────────┤
│ Detection: Response contains "429"      │
│ Action: Rotate to next available model  │
│ Retry: Up to 5 times                    │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│   LAYER 2: Missing Captions             │
├─────────────────────────────────────────┤
│ Detection: Response says "unable to"    │
│ Action: Trigger YouTube audio download  │
│ Fallback: Whisper transcription         │
└─────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────┐
│   LAYER 3: Missing Dependencies         │
├─────────────────────────────────────────┤
│ Detection: FFmpeg or yt-dlp missing     │
│ Action: Show warning at startup         │
│ Fallback: Skip transcription            │
└─────────────────────────────────────────┘
```

### 6️⃣ Complete Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                   STREAMLIT APP (Frontend)                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ VIDEO UPLOAD ───────────┐  ┌─ YOUTUBE URL ──────────┐    │
│  │ • File uploader UI        │  │ • Text input + query   │   │
│  │ • Temp save               │  │ • Submit button        │   │
│  └──────────┬────────────────┘  └──────┬─────────────────┘   │
│             │                         │                      │
└─────────────┼─────────────────────────┼─────────────────────
              │                         │
              ↓                         ↓
┌──────────────────────────────────────────────────────────────┐
│                   AGENT PROCESSING LAYER                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─ run_agent_with_fallback() ──────────────────────────┐    │
│  │ • Call agent.run(prompt)                             │    │
│  │ • Check response for errors                          │    │
│  │ • Auto-switch models on quota (up to 5 times)        │    │
│  └──────────┬──────────────────────────────────────────┘     │
│             │                                                │
│             ├─ Invokes: YouTubeTools (caption extraction)    │
│             ├─ Invokes: DuckDuckGo (web search)              │
│             └─ Invokes: MLXTranscribe (if available)         │
│                                                              │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     ↓
┌──────────────────────────────────────────────────────────────┐
│               FALLBACK TRANSCRIPTION LAYER                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  IF response has missing captions/transcript:                │
│  ├─ download_youtube_audio_and_transcribe()                  │
│  │  ├─ yt-dlp: Download best audio                           │
│  │  ├─ ffmpeg: Extract to MP3                                │
│  │  └─ Whisper: Transcribe to text                           │
│  │                                                           │
│  └─ Re-run agent with transcript                             │
│                                                              │
└────────────────────┬───────────────────────────────────────
                     │
                     ↓
        ┌────────────────────────┐
        │  Google Generative AI  │
        │  (Gemini models)       │
        │                        │
        │ • gemini-2.5-flash     │
        │ • gemini-2.0-flash     │
        │ • gemini-1.5-flash     │
        │ • gemini-1.5-pro       │
        └────────────────────────┘
```

---

## 🔧 Troubleshooting

### Issue: "MLX Transcribe is not installed"

**Solution:** This is a warning, not an error. The app will use OpenAI Whisper instead. To suppress the warning:

```bash
pip install mlx-whisper
# or install MLX separately
pip install mlx
```

### Issue: "Could not extract audio automatically (ffmpeg or moviepy missing)"

**Solution:** Install FFmpeg:

```powershell
# Windows
winget install -e --id Gyan.FFmpeg

# or via Chocolatey
choco install ffmpeg
```

Verify installation:
```bash
ffmpeg -version
```

### Issue: "YouTube audio download/transcription failed"

**Solution:** Ensure dependencies are installed:

```bash
pip install yt-dlp
pip install openai-whisper
ffmpeg -version  # verify FFmpeg installed
```

### Issue: "All available models have exceeded their quota limits"

**Solution:** 
- Wait for quota reset (typically hourly for free tier)
- Check your API usage at: https://ai.google.dev/pricing

### Issue: "OSError: [Errno 28] No space left on device"

**Solution:** Video downloads and audio extractions are saved temporarily into `storage/`. Over time, this directory might grow large. You can safely clear this by deleting the contents:
```powershell
# Windows PowerShell
Remove-Item -Path "storage\audio\*" -Recurse -Force
Remove-Item -Path "storage\video\*" -Recurse -Force
```

### Issue: Streamlit crashing with torch errors

**Solution:** Reinstall CPU-only PyTorch:

```bash
pip uninstall -y torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Issue: "Could not list models" or API configuration errors

**Solution:**
1. Verify API key is set in `.env`:
   ```bash
   echo "GOOGLE_API_KEY=your_key_here" > .env
   ```

2. Test API connection:
   ```python
   import google.generativeai as genai
   genai.configure(api_key="your_key")
   print([m.name for m in genai.list_models()])
   ```

---

## 📦 Architecture

### Project Structure

```
video summarizer/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── .env                     # API keys (not in git)
├── visum/                   # Virtual environment
├── storage/
│   └── audio/              # Temporary audio files for transcription
└── mlx/                    # Optional MLX virtual environment
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `select_gemini_model()` | Dynamically selects available Gemini model |
| `run_agent_with_fallback()` | Executes agent with auto-model switching on quota errors |
| `transcribe_with_whisper()` | Local Whisper transcription (lazy load) |
| `download_youtube_audio_and_transcribe()` | Downloads YouTube audio and transcribes |
| `initialize_agent()` | Creates Phi Agent with tools (YouTubeTools, MLXTranscribe) |
| `check_ffmpeg_available()` | Validates ffmpeg binary at startup |

### Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `phidata` | AI agent framework |
| `google-generativeai` | Gemini API client |
| `yt-dlp` | YouTube audio download |
| `openai-whisper` | Local speech-to-text |
| `torch` | ML framework (CPU-only) |
| `moviepy` | Optional video processing |

---

## 🤝 Contributing

To improve this project:

1. Fork the repository
2. Create a feature branch
3. Test your changes with `streamlit run app.py`
4. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🆘 Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review [Workflow Explanation](#workflow-explanation)
- Visit: https://ai.google.dev/docs
- GitHub Issues: [Your repo link here]

---

## 🎯 Roadmap

- [ ] Support for more video platforms (Vimeo, etc.)
- [ ] Custom model selection UI
- [ ] Batch video processing
- [ ] Caching of transcriptions
- [ ] Export results to PDF/JSON
- [ ] Multi-language support
- [ ] Advanced filtering/search in transcripts

---

**Last Updated:** February 12, 2026  
**Version:** 1.0.0

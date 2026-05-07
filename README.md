<div align="center">

# 🎬 Visum

**AI-Powered Multi-Agent Video Transcription & Summarization System**

[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework: Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![AI: Gemini 2.5](https://img.shields.io/badge/AI-Gemini_2.5_Flash-8E75B2.svg?logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Whisper: MLX](https://img.shields.io/badge/Inference-MLX_Whisper-black.svg?logo=apple&logoColor=white)](https://github.com/ml-explore/mlx)
[![Status: Active](https://img.shields.io/badge/Status-Active_Development-brightgreen.svg)]()

*Visum is a high-performance, local-first multi-agent system designed to extract, transcribe, and intelligently summarize long-form video content using state-of-the-art LLMs and accelerated local audio processing.*

[**Documentation**](#) • [**Quick Start**](#8-quick-start) • [**Architecture**](#4-architecture) • [**Contributing**](#20-contributing)

---

<img src="https://via.placeholder.com/1200x600/0f172a/ffffff?text=Visum+UI+Dashboard+Preview" alt="Visum Dashboard Preview" width="100%"/>

</div>


## 2. OVERVIEW


**Visum** is an intelligent orchestrator for processing rich media. As video content scales exponentially, the ability to rapidly digest, analyze, and search through hours of footage becomes critical. Visum solves this by combining **local, privacy-preserving transcription** (via Apple's MLX-optimized Whisper) with the extreme context windows and reasoning capabilities of **Google's Gemini 2.5 Flash**.

### Why Visum?
- **Speed over Network**: By utilizing `mlx-whisper` and `yt-dlp`, Visum pushes heavy audio processing to your local machine (specifically optimized for Apple Silicon and modern hardware), drastically reducing cloud compute costs.
- **Agentic Summarization**: It doesn't just "summarize." Visum deploys a multi-agent framework powered by `phidata` to execute multi-step reasoning, utilizing custom YouTube tools to extract metadata, captions, and context before generating tailored insights.
- **Modular Pipeline**: From media extraction (`ffmpeg`/`moviepy`) to LLM orchestration and vectorization (`pgvector`), the architecture is strictly modular, allowing drop-in replacements for models and processing nodes.

**Target Use Cases:**
- 📚 **Researchers & Students**: Instantly digest hour-long lectures.
- 💼 **Content Strategists**: Extract key quotes, SEO tags, and summaries from podcasts.
- 👨‍💻 **Developers**: Build automated content ingestion pipelines via the underlying API.


## 3. FEATURES


| Feature | Description | Status | Technical Notes |
| :--- | :--- | :---: | :--- |
| **Local Transcription** | Ultra-fast audio decoding via MLX Whisper | 🟢 Active | `mlx-whisper==0.4.3`, handles large audio chunks locally |
| **Agentic Reasoning** | Multi-agent coordination for complex video queries | 🟢 Active | Powered by `phidata` and Gemini 2.5 Flash |
| **Custom Tools** | Direct YouTube API/scraping integration | 🟢 Active | Integrates `youtube-transcript-api` & custom extraction |
| **Media Extraction** | Robust audio demuxing with multi-level fallbacks | 🟢 Active | `ffmpeg` primary, `moviepy` fallback |
| **Stateful UI** | Reactive, session-based dashboard | 🟢 Active | Built on `streamlit` with custom session state handlers |
| **RAG Integration** | Vector search over transcribed video segments | 🟡 Beta | Utilizing `pgvector`, `sqlalchemy`, and `psycopg` |
| **Async Processing** | Non-blocking transcription & inference | 🟡 Beta | `asyncio` & `FastAPI` / `uvicorn` backend pending full rollout |


## 4. ARCHITECTURE


Visum operates on a robust, state-machine-driven data pipeline. Below are detailed visual representations of how the system processes data, routes between agents, and retrieves context.

### 1. Request Lifecycle
This diagram illustrates the end-to-end journey of a user request, from URL submission to final summary delivery.

```mermaid
graph TD
    %% Styling
    classDef user fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef process fill:#1e293b,stroke:#64748b,stroke-width:1px,color:#fff;
    classDef local fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef cloud fill:#4c1d95,stroke:#8b5cf6,stroke-width:2px,color:#fff;

    User(["User URL Request"]):::user --> UI[Streamlit Frontend]:::process
    UI --> Core[Core Processor]:::process
    Core --> Check{"Captions Available?"}:::process
    
    Check -->|Yes| YTAPI[YouTube Transcript API]:::cloud
    Check -->|No| YTDLP[Download Audio via yt-dlp]:::process
    
    YTDLP --> AudioFile("Storage: .mp3 / .wav"):::process
    AudioFile --> MLX[MLX-Whisper Local Inference]:::local
    
    YTAPI --> RawText[Raw Transcript Text]:::process
    MLX --> RawText
    
    RawText --> Agent[Phidata Orchestrator]:::cloud
    Agent --> Gemini[Gemini 2.5 Flash API]:::cloud
    Gemini --> Final[Structured Markdown Summary]:::process
    Final --> UI
```

### 2. Multi-Agent Routing
Complex requests are routed to specialized agents based on the necessary tasks (e.g., fetching metadata vs. analytical reasoning).

```mermaid
flowchart LR
    classDef router fill:#b91c1c,stroke:#fca5a5,color:#fff
    classDef agent fill:#4338ca,stroke:#818cf8,color:#fff
    
    In["User Query"] --> Router{"Agent Router"}:::router
    
    Router -->|Metadata/Stats| YT[YouTube Agent]:::agent
    Router -->|Raw Audio| Audio[Whisper Agent]:::agent
    Router -->|Synthesis| Sum[Summarization Agent]:::agent
    
    YT --> |Context| Sum
    Audio --> |Transcript| Sum
    
    Sum --> Out[Final Response]
```

### 3. Tool Execution Loop
Agents in Visum use a ReAct (Reason + Act) loop to autonomously decide when and how to invoke external tools (like YouTube scrapers).

```mermaid
sequenceDiagram
    participant A as Agent (Gemini)
    participant T as Tool Registry
    participant E as External Service (YouTube)
    
    Note over A, E: Autonomous Tool Execution Loop
    
    loop Until Task Complete
        A->>A: Thought: I need the video duration.
        A->>T: Call Tool: get_video_metadata(url)
        T->>E: HTTP GET Request
        E-->>T: JSON Response {duration: "10:32"}
        T-->>A: Observation: Duration is 10:32
        A->>A: Thought: I have the metadata, now I need captions.
    end
    
    A->>A: Thought: I have all required data.
    A-->>User: Final generated response.
```

### 4. RAG Pipeline (Retrieval-Augmented Generation)
For interacting with long videos, transcripts are chunked, embedded, and stored in a vector database (`pgvector`) for rapid semantic retrieval.

```mermaid
graph TD
    classDef db fill:#0369a1,stroke:#7dd3fc,color:#fff
    
    Trans[Raw Transcript] --> Chunk[Text Chunker]
    Chunk --> Embed["Embedding Model: text-embedding-004"]
    Embed --> VecDB[("PostgreSQL + pgvector")]:::db
    
    UserQ["User: 'When did they mention Python?'"] --> QEmbed[Query Embedding]
    QEmbed --> Search{Cosine Similarity Search}
    VecDB --> Search
    
    Search --> TopK[Top-K Transcript Chunks]
    TopK --> LLM[Gemini LLM]
    UserQ --> LLM
    LLM --> FinalAnswer[Synthesized Answer]
```


## 5. TECH STACK


### Frontend & UI
| Technology | Purpose | Justification |
| :--- | :--- | :--- |
| **Streamlit** | Core Application UI | Enables rapid, reactive, Python-native stateful dashboards. |

### Backend & Orchestration
| Technology | Purpose | Justification |
| :--- | :--- | :--- |
| **Python 3.12** | Core Language | Type-safe, high-performance features; standard for AI. |
| **Phidata** | Agent Orchestration | Lightweight, highly structured framework for building tool-calling agents. |
| **FastAPI / Uvicorn** | API Layer | High-performance ASGI framework for programmatic system access. |

### AI, ML & Data
| Technology | Purpose | Justification |
| :--- | :--- | :--- |
| **MLX-Whisper** | Local Transcription | Apple Silicon optimized; massive speedups over PyTorch Whisper on Mac. |
| **Gemini 2.5 Flash** | Core LLM | Massive context window (1M+ tokens), ideal for full-video transcript ingestion. |
| **PostgreSQL & pgvector** | Vector Store | Production-ready ACID database with native highly-efficient vector embedding support. |
| **yt-dlp / FFmpeg** | Media Processing | Industry standard for secure, fast media streaming, downloading, and demuxing. |


## 6. INSTALLATION


### Prerequisites
- **Python 3.12+**
- **FFmpeg** installed and added to PATH
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt install ffmpeg`
  - Windows: `winget install ffmpeg`
- **PostgreSQL** (Optional, for Vector DB features)

### Local Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/visum.git
   cd visum
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv visum
   .\visum\Scripts\activate

   # Linux / macOS
   python -m venv visum
   source visum/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify FFmpeg installation:**
   ```bash
   ffmpeg -version
   ```


## 7. ENVIRONMENT VARIABLES


Create a `.env` file in the root directory. Copy the structure from `.env.example`:

| Variable | Description | Required | Default |
| :--- | :--- | :---: | :--- |
| `GEMINI_API_KEY` | Your Google AI Studio API key | Yes | `None` |
| `OPENAI_API_KEY` | Optional: For fallback models / OpenAI Whisper | No | `None` |
| `GROQ_API_KEY` | Optional: For high-speed LLM inference | No | `None` |
| `DATABASE_URL` | PostgreSQL connection string for pgvector | No | `postgresql://user:pass@localhost:5432/visum` |
| `STORAGE_PATH` | Local directory for temp audio/video files | No | `./storage/audio` |

```ini
# .env file
GEMINI_API_KEY="AIzaSyYourKeyHere..."
STORAGE_PATH="./storage/audio"
```


## 8. QUICK START


### Launching the UI Dashboard
Start the Streamlit application:
```bash
streamlit run app.py
```
Navigate to `http://localhost:8501` in your browser.

### Minimal Python API Example
To use the core processor directly in your code without the UI:

```python
from core.processor import VideoProcessor
from services.llm import GeminiService

# Initialize the LLM Service
agent = GeminiService.create_agent(
    model_id="models/gemini-2.5-flash",
    instructions=["Summarize the following video transcript with key takeaways."]
)

# Initialize Processor
processor = VideoProcessor(agent_service=agent)

# Process a URL
result = processor.summarize("https://youtube.com/watch?v=example")
print(result.summary)
```


## 9. USAGE EXAMPLES


### 1. Generating a Structured Markdown Report
```python
from services.custom_youtube_tools import CustomYouTubeTools

tools = CustomYouTubeTools()
captions = tools.get_youtube_video_captions("https://youtu.be/some_id")

prompt = f"""
Analyze the following transcript and format the output as:
1. Executive Summary
2. Key Arguments
3. Actionable Takeaways

Transcript: {captions}
"""

response = agent.run(prompt)
print(response.content)
```

### 2. Testing Custom Tools
You can directly interact with the YouTube metadata tool:
```bash
python tests/test_custom_tool.py
```


## 10. PROJECT STRUCTURE


```text
visum/
├── app.py                      # Streamlit entry point
├── core/                       
│   └── processor.py            # Core state machine and pipeline orchestration
├── services/                   # External APIs and Local Compute integrations
│   ├── custom_youtube_tools.py # Phidata tool implementations
│   ├── llm.py                  # Gemini / Groq agent factories
│   ├── media.py                # FFmpeg/MoviePy audio extraction
│   ├── transcription.py        # MLX-Whisper bindings
│   └── youtube.py              # yt-dlp integrations
├── ui/                         
│   ├── components.py           # Reusable Streamlit UI widgets
│   └── state.py                # Session state management
├── tests/                      # Pytest suite
│   ├── test_core_processor.py
│   ├── test_services_media.py
│   └── ...
├── storage/                    # Local cache for media and transcripts
├── MLXTRANSCRIBE_ANALYSIS.md   # Architectural decisions for transcription
├── requirements.txt            # Dependency lockfile
└── .env                        # Environment configurations
```


## 11. CONFIGURATION


Visum is highly configurable. Key parameters can be adjusted directly in the component initialization:

- **Model Selection:** Swap `gemini-2.5-flash` for `gemini-1.5-pro` in `services.llm` for tasks requiring deeper analytical reasoning over speed.
- **Whisper Quantization:** MLX-Whisper parameters in `services.transcription` can be tuned for fp16, int8, or int4 depending on available VRAM/Unified Memory.
- **Audio Extraction Quality:** Set FFmpeg bitrate parameters in `services.media.py` (Default: `libmp3lame -q:a 2`).


## 12. AGENT CAPABILITIES


The Phidata agents in Visum are equipped with:
- **Tool Use (Function Calling):** Capable of autonomously fetching transcripts, channel metadata, and video duration without human intervention.
- **Context Management:** Handles long-form transcripts by utilizing Gemini 2.5 Flash's massive context window, avoiding the need for aggressive chunking on medium-length videos.
- **Fallback Logic:** The system gracefully downgrades. If `youtube-transcript-api` fails (e.g., no captions available), the system automatically routes to `yt-dlp` -> `media.py` -> `mlx-whisper` to generate transcripts from scratch.

*Limitations:* Currently, multi-agent debate (e.g., Researcher Agent vs. Writer Agent) is conceptual and being actively developed. 


## 13. API REFERENCE


*(Note: FastAPI layer is currently in beta. Core logic operates via Python classes).*

### `VideoProcessor`
**Method:** `process(url: str, mode: str = "summarize") -> Dict`
- **Description:** Main entry point for video processing.
- **Returns:** JSON object containing `video_id`, `raw_transcript`, and `agent_summary`.


## 14. EVALUATION


- **Transcription Latency (Apple M-Series):** MLX-Whisper achieves ~15x-20x real-time speed. A 1-hour audio file transcribes in ~3-4 minutes on an M2 Pro.
- **Token Efficiency:** By utilizing Gemini 2.5 Flash, the system passes raw transcripts efficiently without complex LangChain map-reduce chunking overhead, reducing latency and preserving document cohesiveness.


## 15. SECURITY


- **Secret Management:** Strictly relies on `.env` parsing via `python-dotenv`. Keys are never hardcoded.
- **Execution Sandboxing:** Subprocesses (`subprocess.run` in `media.py`) strictly define arguments to prevent injection attacks via malicious URLs.
- **Data Privacy:** Local transcription ensures audio files never leave your machine unless sent explicitly to the LLM for summarization. 


## 16. DEPLOYMENT


Visum is currently optimized for local execution. 

### Docker (Coming Soon)
A `Dockerfile` utilizing multi-stage builds (handling FFmpeg system dependencies alongside Python packages) is under active development.


## 17. TESTING


The project uses `pytest` for comprehensive testing.

**Run all tests:**
```bash
python run_tests.py
# or directly:
pytest tests/ -v
```

**Test Coverage Includes:**
- Mocked LLM responses (`test_services_llm.py`)
- FFmpeg fallback logic (`test_services_media.py`)
- UI State mutations (`test_ui_state.py`)


## 18. PERFORMANCE OPTIMIZATION


- **MLX Hardware Acceleration:** By utilizing `mlx-whisper==0.4.3`, Visum bypasses PyTorch overhead on Apple Silicon, utilizing unified memory efficiently.
- **Lazy Loading:** UI components and heavy ML models are loaded into Streamlit's `@st.cache_resource` to prevent memory leaks across re-runs.
- **Cleanup:** `storage/` is automatically pruned of `.mp3` and `.mp4` artifacts post-transcription to save disk space.


## 19. ROADMAP


- [x] Streamlit UI Implementation
- [x] MLX-Whisper Integration
- [x] Phidata Agent Orchestration
- [x] Media Fallback Mechanisms (FFmpeg -> MoviePy)
- [ ] **Short-term:** FastAPI backend for headless execution
- [ ] **Short-term:** Docker compose stack with PostgreSQL/pgvector
- [ ] **Long-term:** Multi-modal support (analyzing video frames via Gemini Vision)
- [ ] **Long-term:** Agent memory persistence across sessions


## 20. CONTRIBUTING


We welcome contributions! 

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Run formatting and tests (`pytest`)
4. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
5. Push to the Branch (`git push origin feature/AmazingFeature`)
6. Open a Pull Request

*Please ensure all PRs maintain the existing code style and include tests for new functionality.*


## 21. FAQ


<details>
<summary><strong>Do I need a GPU to run this?</strong></summary>
No, but it is highly recommended. On Apple Silicon, MLX handles the heavy lifting. On Windows/Linux, standard CPU processing will work but transcription will be significantly slower unless configured with CUDA/PyTorch Whisper.
</details>

<details>
<summary><strong>Why does FFmpeg extraction fail sometimes?</strong></summary>
Ensure FFmpeg is globally accessible in your system PATH. Visum uses `moviepy` as a fallback, but FFmpeg is required for optimal performance.
</details>

<details>
<summary><strong>Can I use OpenAI instead of Gemini?</strong></summary>
Yes. The modular `services.llm` and Phidata orchestrator allow you to swap in `OpenAIAgent` with minimal code changes.
</details>


## 22. LICENSE


Distributed under the MIT License. See `LICENSE` for more information.


## 23. ACKNOWLEDGEMENTS


- [Apple MLX Team](https://github.com/ml-explore/mlx) for the incredibly fast local inference framework.
- [Phidata](https://github.com/phidatahq/phidata) for elegant agent orchestration.
- [Streamlit](https://streamlit.io/) for the rapid UI framework.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for robust media extraction.


## 24. CONTACT / COMMUNITY


**Project Link:** [https://github.com/your-username/visum](https://github.com/your-username/visum)  
**Discussions:** [GitHub Discussions](#)  
**Twitter:** [@YourHandle](#)

---
<div align="center">
<i>Built with ❤️ by the Visum Open Source Community</i>
</div>

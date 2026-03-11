from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum, auto

class SourceType(Enum):
    VIDEO_FILE = auto()
    YOUTUBE_URL = auto()

class VideoSource(BaseModel):
    source_type: SourceType
    path: Optional[str] = None  # File path or URL
    video_id: Optional[str] = None # For YouTube
    title: Optional[str] = None
    description: Optional[str] = None

class AnalysisRequest(BaseModel):
    video_source: VideoSource
    query: str
    provide_transcript: bool = True

class AnalysisResult(BaseModel):
    content: str
    metadata: dict = Field(default_factory=dict)

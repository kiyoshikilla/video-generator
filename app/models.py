from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from typing import Dict, List


class TextTS(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000
    )
    voice: str = Field(
        ...,
        description="Choose the voice for your text"
    )

class VideoProcessingRequest(BaseModel):
    task_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description= "Name for the task"
    )


    video_blocks: Dict[str, List[HttpUrl]] = Field(
        ...,
        description= "Array of video's links"
        )
    
    audio_blocks: Dict[str, List[HttpUrl]] = Field(
        ...,
        description="Array of music links"
    )

    text_to_speach: List[TextTS] = Field(
        ...,
        description="List of text and voice to generate audio"
    )




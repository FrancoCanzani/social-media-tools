from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class VideoMetadata(BaseModel):
    author: str
    channel_url: str
    channel_id: str
    title: str
    thumbnail: str
    description: Optional[str]
    keywords: List[str]
    resolutions: List[str]
    publish_date: date
    length: int
    rating: Optional[float]
    views: int
    captions: Optional[List[str]]

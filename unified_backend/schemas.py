from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class Source(BaseModel):
    document_id: int
    filename: str
    snippet: str

    model_config = {"from_attributes": True}

class ChatOut(BaseModel):
    reply: str
    sources: List[Source]

    model_config = {"from_attributes": True}

class UploadOut(BaseModel):
    document_id: int
    filename: str

    model_config = {"from_attributes": True}

class FileItem(BaseModel):
    id: int
    filename: str
    created_at: datetime

    model_config = {"from_attributes": True}

class FAQItem(BaseModel):
    question: str
    count: int

    model_config = {"from_attributes": True}

# -----------------------------
# MoodBot
# -----------------------------
class MoodChatIn(BaseModel):
    user_id: str
    session_id: str
    message: str = ""

class MoodChatOut(BaseModel):
    reply: str
    stage: str
    username: Optional[str] = None
    model_config = {"from_attributes": True}

class MoodLogOut(BaseModel):
    id: int
    user_id: str
    session_id: str
    username: str
    mood: str
    reason: Optional[str]
    date: str
    created_at: datetime
    model_config = {"from_attributes": True}

class MoodAnalyticsOut(BaseModel):
    buckets: Dict[str, int]
    reasons: List[str]
    top_moods: Dict[str, int]
    model_config = {"from_attributes": True}

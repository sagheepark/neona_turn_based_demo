from pydantic import BaseModel
from typing import List, Dict, Optional

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    character_prompt: str
    history: List[Dict[str, str]] = []
    character_id: str
    
class ChatResponse(BaseModel):
    character: str
    dialogue: str
    emotion: str = "neutral"
    speed: float = 1.0
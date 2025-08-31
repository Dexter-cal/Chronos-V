from pydantic import BaseModel
from typing import Dict, Any

class HintRequest(BaseModel):
    player_id: str
    context: Dict[str, Any]

class Hint(BaseModel):
    hint_text: str
    hint_type: str = "text"

from pydantic import BaseModel
from typing import List, Optional

class GameTheme(BaseModel):
    """
    Defines the high-level theme or prompt for the game world generation.
    This is a shared model to be used by various AI services.
    """
    prompt: str
    setting: Optional[str] = None # e.g., "fantasy", "sci-fi"
    tone: Optional[str] = None # e.g., "dark", "whimsical"
    key_nouns: List[str] = [] # e.g., ["dragons", "spaceships", "zombies"]

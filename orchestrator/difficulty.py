from pydantic import BaseModel
from typing import Dict, Any
import datetime

class PlayerEvent(BaseModel):
    event_type: str
    timestamp: datetime.datetime = datetime.datetime.now()
    payload: Dict[str, Any] = {}

class DifficultySettings(BaseModel):
    enemy_health_modifier: float = 1.0
    loot_drop_rate_modifier: float = 1.0
    puzzle_complexity_modifier: float = 1.0

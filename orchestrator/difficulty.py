from pydantic import BaseModel
from typing import Dict, Any
import datetime

class PlayerEvent(BaseModel):
    event_type: str
    timestamp: datetime.datetime = datetime.datetime.now()
    payload: Dict[str, Any] = {}

class DifficultySettings(BaseModel):
    # General difficulty level, e.g., 1.0 is normal, 1.5 is hard
    difficulty_level: float = 1.0

    # Modifiers for combat
    enemy_health_modifier: float = 1.0
    enemy_count_multiplier: float = 1.0

    # Modifiers for quests and rewards
    quest_reward_multiplier: float = 1.0
    item_requirement_multiplier: float = 1.0

    # Modifiers for world/economy
    loot_drop_rate_modifier: float = 1.0
    puzzle_complexity_modifier: float = 1.0

def adjust_difficulty(events: list[PlayerEvent], current_settings: DifficultySettings) -> DifficultySettings:
    """
    Adjusts the difficulty settings based on recent player events.
    """
    success_events = len([e for e in events if e.event_type in ["QUEST_COMPLETED", "BOSS_DEFEATED"]])
    failure_events = len([e for e in events if e.event_type in ["PLAYER_DIED", "QUEST_FAILED"]])

    # Simple adjustment logic
    net_success = success_events - failure_events

    new_level = current_settings.difficulty_level
    if net_success > 2: # If player has 3 more successes than failures
        new_level += 0.1
    elif net_success < -1: # If player has 2 more failures than successes
        new_level -= 0.1

    # Clamp the difficulty level to a reasonable range (e.g., 0.5 to 2.0)
    new_level = max(0.5, min(new_level, 2.0))

    # Create new settings based on the adjusted level
    new_settings = DifficultySettings(
        difficulty_level=new_level,
        # Scale other modifiers based on the new level
        enemy_count_multiplier=1.0 * new_level,
        enemy_health_modifier=1.0 * new_level,
        quest_reward_multiplier=1.0 / new_level, # Harder difficulty gives slightly worse rewards
        item_requirement_multiplier=1.0 * new_level
    )

    print(f"Difficulty adjusted. Old level: {current_settings.difficulty_level:.2f}, New level: {new_settings.difficulty_level:.2f}")

    return new_settings

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
import random
from .shared_models import GameTheme
from .content_generator_ai import generate_themed_list
from .difficulty import DifficultySettings

class QuestStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ObjectiveType(str, Enum):
    FETCH = "FETCH"
    KILL = "KILL"
    GOTO = "GOTO"

class QuestObjective(BaseModel):
    objective_id: str
    description: str
    type: ObjectiveType
    target: str # e.g., "item_id", "enemy_type", "location_name"
    required_amount: int
    current_amount: int = 0

class QuestReward(BaseModel):
    experience: int = 0
    gold: int = 0
    items: List[str] = [] # List of item IDs

class Quest(BaseModel):
    quest_id: str
    title: str
    description: str
    status: QuestStatus = QuestStatus.NOT_STARTED
    objectives: List[QuestObjective]
    rewards: QuestReward

def generate_quest(player_level: int = 1, theme: Optional[GameTheme] = None, difficulty: Optional[DifficultySettings] = None) -> Quest:
    """
    Generates a new procedural quest based on player level, a given theme,
    and current difficulty settings.
    """
    # If no theme/difficulty is provided, create default ones
    if not theme:
        theme = GameTheme(prompt="A classic fantasy world with monsters and magic.", setting="fantasy")
    if not difficulty:
        difficulty = DifficultySettings()

    # --- Quest Generation ---
    quest_type = random.choice([ObjectiveType.FETCH, ObjectiveType.KILL])

    if quest_type == ObjectiveType.FETCH:
        # Dynamically generate item names based on the theme
        item_pool = generate_themed_list(theme, "collectible items", count=5)
        item_name = random.choice(item_pool)
        # Scale amount by difficulty
        base_amount = random.randint(3, 8)
        amount = int(base_amount * difficulty.item_requirement_multiplier)
        amount = max(1, amount) # Ensure at least 1 is required

        title = f"A Collector's Task: {item_name}"
        description = f"A local contact needs {amount} {item_name}(s) for their work."
        objective = QuestObjective(
            objective_id=str(uuid.uuid4()),
            description=f"Collect {amount} {item_name}(s).",
            type=ObjectiveType.FETCH,
            target=item_name,
            required_amount=amount
        )

    elif quest_type == ObjectiveType.KILL:
        # Dynamically generate enemy names based on the theme
        enemy_pool = generate_themed_list(theme, "common enemy types", count=5)
        enemy_name = random.choice(enemy_pool)
        # Scale amount by difficulty
        base_amount = random.randint(2, 5)
        amount = int(base_amount * difficulty.enemy_count_multiplier)
        amount = max(1, amount) # Ensure at least 1 is required

        title = f"A Menace to be Dealt With: {enemy_name}s"
        description = f"The area has been compromised by {enemy_name}s. They need to be cleared out."
        objective = QuestObjective(
            objective_id=str(uuid.uuid4()),
            description=f"Eliminate {amount} {enemy_name}s.",
            type=ObjectiveType.KILL,
            target=enemy_name,
            required_amount=amount
        )

    # Generate and scale rewards
    base_xp = player_level * 50 + random.randint(10, 25)
    base_gold = player_level * 20 + random.randint(5, 15)
    xp_reward = int(base_xp * difficulty.quest_reward_multiplier)
    gold_reward = int(base_gold * difficulty.quest_reward_multiplier)

    quest = Quest(
        quest_id=str(uuid.uuid4()),
        title=title,
        description=description,
        objectives=[objective],
        rewards=QuestReward(experience=xp_reward, gold=gold_reward)
    )

    return quest

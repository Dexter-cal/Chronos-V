from pydantic import BaseModel
from typing import List, Dict, Any
from enum import Enum
import uuid
import random

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

def generate_quest(player_level: int = 1) -> Quest:
    """
    Generates a new procedural quest based on player level.
    """
    quest_type = random.choice([ObjectiveType.FETCH, ObjectiveType.KILL])

    if quest_type == ObjectiveType.FETCH:
        item_name = random.choice(["Glimmering Shard", "Wolf Pelt", "Ancient Herb", "Spider Silk"])
        amount = random.randint(3, 8)
        title = f"A Collector's Task"
        description = f"A local merchant needs {amount} {item_name}s. They say they can be found in the nearby forest."
        objective = QuestObjective(
            objective_id=str(uuid.uuid4()),
            description=f"Collect {amount} {item_name}s.",
            type=ObjectiveType.FETCH,
            target=item_name,
            required_amount=amount
        )

    elif quest_type == ObjectiveType.KILL:
        enemy_name = random.choice(["Dire Wolf", "Giant Spider", "Goblin Scout", "Forest Bandit"])
        amount = random.randint(2, 5)
        title = f"A Menace to be Dealt With"
        description = f"The area has been plagued by {enemy_name}s. Someone needs to thin their numbers."
        objective = QuestObjective(
            objective_id=str(uuid.uuid4()),
            description=f"Defeat {amount} {enemy_name}s.",
            type=ObjectiveType.KILL,
            target=enemy_name,
            required_amount=amount
        )

    # Generate rewards based on player level and quest difficulty
    xp_reward = player_level * 50 + random.randint(10, 25)
    gold_reward = player_level * 20 + random.randint(5, 15)

    quest = Quest(
        quest_id=str(uuid.uuid4()),
        title=title,
        description=description,
        objectives=[objective],
        rewards=QuestReward(experience=xp_reward, gold=gold_reward)
    )

    return quest

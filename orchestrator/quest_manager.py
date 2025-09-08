from typing import Dict, Optional
from .quest_ai import Quest, QuestStatus

# In-memory "database" for active quests.
# The key is the quest_id (str), and the value is the Quest object.
_active_quests: Dict[str, Quest] = {}

def add_quest(quest: Quest):
    """Adds a newly generated quest to the manager."""
    if quest.quest_id not in _active_quests:
        _active_quests[quest.quest_id] = quest

def get_quest_status(quest_id: str) -> Optional[Quest]:
    """Retrieves a quest from the manager."""
    return _active_quests.get(quest_id)

def accept_quest(quest_id: str) -> Optional[Quest]:
    """Marks a quest as IN_PROGRESS."""
    quest = get_quest_status(quest_id)
    if quest and quest.status == QuestStatus.NOT_STARTED:
        quest.status = QuestStatus.IN_PROGRESS
        return quest
    return None

def update_objective_progress(quest_id: str, objective_id: str, progress_amount: int) -> Optional[Quest]:
    """Updates the progress of a specific quest objective."""
    quest = get_quest_status(quest_id)
    if not quest or quest.status != QuestStatus.IN_PROGRESS:
        return None

    for objective in quest.objectives:
        if objective.objective_id == objective_id:
            objective.current_amount += progress_amount
            # Clamp the progress to the required amount
            if objective.current_amount >= objective.required_amount:
                objective.current_amount = objective.required_amount
            break

    # Check if all objectives are complete
    all_objectives_complete = all(obj.current_amount >= obj.required_amount for obj in quest.objectives)
    if all_objectives_complete:
        quest.status = QuestStatus.COMPLETED

    return quest

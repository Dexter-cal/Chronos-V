from pydantic import BaseModel
from typing import List, Optional
from .quest_ai import Quest
from .npc_ai import DialogueResponse
from .shared_models import GameTheme

class CoordinatedWorldOutput(BaseModel):
    """
    Represents the combined output of all AI services, orchestrated by a single theme.
    """
    theme: GameTheme
    generated_quests: List[Quest]
    sample_dialogue: List[DialogueResponse]
    # Future fields can be added here, e.g., generated_map, character_backstories, etc.

import random
from .quest_ai import generate_quest
from .npc_ai import generate_dialogue, DialogueRequest, DialogueStrategyType

def coordinate_generation(theme: GameTheme) -> CoordinatedWorldOutput:
    """
    Takes a high-level theme and orchestrates the various AI services
    to generate a consistent set of game assets.
    """
    print(f"--- Genesis AI: Starting coordinated generation for theme: {theme.prompt} ---")

    # 1. Generate a quest consistent with the theme
    print("Generating themed quest...")
    generated_quest = generate_quest(player_level=1, theme=theme)

    # 2. Generate a sample dialogue snippet consistent with the theme
    print("Generating themed dialogue...")
    # We'll create a sample prompt that might lead to a themed response
    sample_prompt = f"Hello there. I'm looking for clues about {random.choice(theme.key_nouns or ['anything interesting'])}."
    dialogue_request = DialogueRequest(
        npc_id="generic_npc",
        player_prompt=sample_prompt,
        theme=theme,
        strategy=DialogueStrategyType.LLM # Use the LLM for more nuanced themed responses
    )
    generated_dialogue = generate_dialogue(dialogue_request)

    # 3. Assemble the coordinated output
    print("Assembling coordinated output...")
    coordinated_output = CoordinatedWorldOutput(
        theme=theme,
        generated_quests=[generated_quest],
        sample_dialogue=[generated_dialogue]
    )

    print("--- Genesis AI: Coordinated generation complete. ---")
    return coordinated_output

from pydantic import BaseModel
from typing import List, Optional, Dict
from .quest_ai import Quest, generate_quest
from .npc_ai import DialogueResponse, DialogueRequest, DialogueStrategyType, generate_dialogue
from .shared_models import GameTheme
from . import world_builder_ai
from . import content_generator_ai
import random

class CoordinatedWorldOutput(BaseModel):
    """
    Represents the combined output of all AI services, orchestrated by a single theme.
    """
    theme: GameTheme
    world_map: List[List[str]]
    locations: Dict[str, Dict] # { "Location Name": {"x": 10, "y": 15} }
    generated_quests: List[Quest]
    sample_dialogue: List[DialogueResponse]

def coordinate_generation(theme: GameTheme) -> CoordinatedWorldOutput:
    """
    Takes a high-level theme and orchestrates the various AI services
    to generate a consistent set of game assets.
    """
    print(f"--- Genesis AI: Starting coordinated generation for theme: {theme.prompt} ---")

    # 1. Generate lists of thematic content
    print("Brainstorming thematic content...")
    themed_locations = content_generator_ai.generate_themed_list(theme, "points of interest", count=3)

    # 2. Generate the world map
    print("Generating world map...")
    base_map = world_builder_ai.generate_basic_map(width=50, height=20)
    final_map, location_coords = world_builder_ai.place_themed_locations(base_map, themed_locations)

    # 3. Generate a quest consistent with the theme
    print("Generating themed quest...")
    generated_quest = generate_quest(player_level=1, theme=theme)

    # 4. Generate a sample dialogue snippet consistent with the theme
    print("Generating themed dialogue...")
    sample_prompt = f"Hello there. I'm looking for clues about {random.choice(theme.key_nouns or ['anything interesting'])}."
    dialogue_request = DialogueRequest(
        npc_id="generic_npc",
        player_prompt=sample_prompt,
        theme=theme,
        strategy=DialogueStrategyType.LLM
    )
    generated_dialogue = generate_dialogue(dialogue_request)

    # 5. Assemble the coordinated output
    print("Assembling coordinated output...")
    coordinated_output = CoordinatedWorldOutput(
        theme=theme,
        world_map=final_map,
        locations=location_coords,
        generated_quests=[generated_quest],
        sample_dialogue=[generated_dialogue]
    )

    print("--- Genesis AI: Coordinated generation complete. ---")
    return coordinated_output

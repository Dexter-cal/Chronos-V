from typing import List
from .shared_models import GameTheme
from .npc_ai import DialogueRequest, DialogueStrategyType, generate_dialogue
import re

def generate_themed_list(theme: GameTheme, content_type: str, count: int = 5) -> List[str]:
    """
    Uses the LLM to generate a list of thematically appropriate strings.

    Args:
        theme: The GameTheme object describing the world.
        content_type: A string describing the type of content to generate (e.g., "enemy types", "item names").
        count: The number of items to generate.

    Returns:
        A list of generated strings.
    """
    print(f"--- Content Generator: Generating {count} {content_type} for theme: {theme.prompt} ---")

    # 1. Engineer the prompt
    prompt = (
        f"You are a creative AI assistant for a game development project. "
        f"The game's theme is: '{theme.prompt}'. "
        f"The setting is '{theme.setting}' and the tone is '{theme.tone}'. "
        f"List exactly {count} thematic {content_type}. "
        f"The list should be a single line of comma-separated values. For example: item1, item2, item3"
    )

    # 2. Call the LLM
    request = DialogueRequest(
        npc_id="content_generator",
        player_prompt=prompt,
        strategy=DialogueStrategyType.LLM,
        theme=theme # Pass the theme for system prompt consistency
    )
    response = generate_dialogue(request)
    raw_list = response.npc_response

    print(f"LLM generated raw list: '{raw_list}'")

    # 3. Parse the response
    # A simple parser that splits by comma and strips whitespace.
    # This is brittle and could be improved with more robust parsing or by asking the LLM for JSON.
    items = [item.strip() for item in raw_list.split(',')]

    # Clean up any empty strings that might result from parsing
    items = [item for item in items if item]

    print(f"Parsed list: {items}")

    if not items:
        # Fallback if parsing fails
        return [f"Themed {content_type} 1", f"Themed {content_type} 2"]

    return items

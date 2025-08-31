from pydantic import BaseModel
from typing import Dict, Any

class AssistiveAIRequest(BaseModel):
    """
    Represents a request from a player to the In-Game Assistive AI.
    """
    player_id: str
    request_text: str
    game_context: Dict[str, Any] = {}

class AssistiveAIResponse(BaseModel):
    """
    Represents a response from the Assistive AI back to the player.
    """
    response_text: str
    action_taken: str # e.g., "DELEGATED_TO_LIGHTING_AI"

class ModuleCommand(BaseModel):
    """
    Represents a command to be sent to another AI module.
    """
    target_module: str
    command: str
    parameters: Dict[str, Any] = {}

# Placeholder for the core logic of the Assistive AI
def process_player_request(request: AssistiveAIRequest) -> AssistiveAIResponse:
    """
    Processes the player's request and determines the appropriate action.
    For now, this is a simple placeholder.
    """
    # In a real implementation, an LLM would parse the request_text.
    # For now, we'll use simple keyword matching.
    if "dark" in request.request_text or "see" in request.request_text:
        command = ModuleCommand(
            target_module="LightingAI",
            command="increase_brightness",
            parameters={"area": "current_location"}
        )
        response_text = f"I've asked the Lighting AI to brighten up this area for you."
        action_taken = "DELEGATED_TO_LIGHTING_AI"
    elif "stuck" in request.request_text or "bridge" in request.request_text:
        command = ModuleCommand(
            target_module="WorldBuilderAI",
            command="create_bridge",
            parameters={"location": "player_location"}
        )
        response_text = f"I've asked the World Builder AI to help you with a path forward."
        action_taken = "DELEGATED_TO_WORLD_BUILDER_AI"
    else:
        command = ModuleCommand(
            target_module="NarrativeAI",
            command="provide_hint",
            parameters={}
        )
        response_text = "I'm not sure how to fix that directly, but I've asked the Narrative AI to give you a hint."
        action_taken = "DELEGATED_TO_NARRATIVE_AI"

    print(f"Generated command: {command}")

    return AssistiveAIResponse(
        response_text=response_text,
        action_taken=action_taken
    )

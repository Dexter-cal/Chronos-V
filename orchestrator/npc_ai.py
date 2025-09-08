from pydantic import BaseModel
from typing import Dict, Any

class DialogueRequest(BaseModel):
    npc_id: str
    player_prompt: str

class DialogueResponse(BaseModel):
    npc_response: str

# Placeholder for NPC AI models and logic
# In a real implementation, this module would manage NPC behaviors, dialogue, and states.

class NPCRequest(BaseModel):
    request_type: str
    parameters: Dict[str, Any]

class NPCResponse(BaseModel):
    status: str
    data: Any

def process_npc_request(request: NPCRequest) -> NPCResponse:
    print(f"NPC AI received request: {request}")
    # Placeholder logic
    if request.request_type == "assign_quest_to_npc":
        return NPCResponse(status="success", data={"npc_id": "npc_bard_01", "quest_assigned": True})
    return NPCResponse(status="failure", data={"error": "Unknown request type"})

def generate_dialogue(request: DialogueRequest) -> DialogueResponse:
    """
    Generates a dialogue response based on the player's prompt.
    This is a simple rule-based implementation.
    """
    prompt = request.player_prompt.lower()

    if "hello" in prompt or "hi" in prompt:
        response_text = "Greetings, traveler."
    elif "quest" in prompt:
        response_text = "I may have a task for you. Are you brave enough?"
    elif "bye" in prompt:
        response_text = "Farewell."
    else:
        response_text = "I don't understand."

    return DialogueResponse(npc_response=response_text)

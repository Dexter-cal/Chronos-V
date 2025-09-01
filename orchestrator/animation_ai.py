from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Viseme(BaseModel):
    """
    Represents a single viseme (lip shape) at a specific time.
    """
    viseme_name: str  # e.g., "A", "E", "O", "sil" (silent)
    timestamp: float  # in seconds from the start of the audio

class AnimationTrigger(BaseModel):
    """
    Represents a trigger for a body animation at a specific time.
    """
    animation_name: str  # e.g., "wave", "point_left", "shrug"
    timestamp: float  # in seconds

class AnimationRequest(BaseModel):
    """
    Represents a request to the Animation AI to generate animation data.
    """
    text: Optional[str] = None
    audio_data: Optional[bytes] = None # Placeholder for raw audio data
    emotional_context: str  # e.g., "happy", "sad", "angry"
    narrative_context: str # e.g., "greeting_player", "giving_quest"

class AnimationResponse(BaseModel):
    """
    Represents a response from the Animation AI containing the generated animation data.
    """
    visemes: List[Viseme]
    animation_triggers: List[AnimationTrigger]

# --- Rule-Based Animation Logic ---

def _generate_visemes_from_text(text: str) -> List[Viseme]:
    """
    Generates a simple, placeholder sequence of visemes based on the length of the text.
    """
    visemes = [Viseme(viseme_name="sil", timestamp=0.0)]
    if not text:
        return visemes

    duration = len(text) * 0.1  # Assume 0.1 seconds per character
    num_visemes = int(duration / 0.2)
    viseme_options = ["A", "E", "I", "O", "U"]

    for i in range(num_visemes):
        timestamp = (i + 1) * 0.2
        viseme_name = viseme_options[i % len(viseme_options)]
        visemes.append(Viseme(viseme_name=viseme_name, timestamp=timestamp))

    visemes.append(Viseme(viseme_name="sil", timestamp=duration + 0.2))
    return visemes

def _get_animation_triggers(emotional_context: str, narrative_context: str) -> List[AnimationTrigger]:
    """
    Generates animation triggers based on the emotional and narrative context.
    """
    animation_triggers = []
    if "greeting" in narrative_context:
        animation_triggers.append(AnimationTrigger(animation_name="wave", timestamp=0.1))

    if emotional_context == "happy":
        animation_triggers.append(AnimationTrigger(animation_name="smile", timestamp=0.2))
    elif emotional_context == "sad":
        animation_triggers.append(AnimationTrigger(animation_name="slump_shoulders", timestamp=0.5))
    elif emotional_context == "angry":
        animation_triggers.append(AnimationTrigger(animation_name="shake_fist", timestamp=0.3))

    return animation_triggers

# --- Core Animation AI Logic ---
def process_animation_request(request: AnimationRequest) -> AnimationResponse:
    """
    Processes an animation request using simple, rule-based logic.
    """
    print(f"Received animation request: {request}")

    visemes = _generate_visemes_from_text(request.text)
    animation_triggers = _get_animation_triggers(request.emotional_context, request.narrative_context)

    return AnimationResponse(
        visemes=visemes,
        animation_triggers=animation_triggers
    )

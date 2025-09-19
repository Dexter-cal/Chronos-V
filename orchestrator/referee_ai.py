from pydantic import BaseModel
from typing import List, Dict
from transformers import pipeline

class ModerationVerdict(BaseModel):
    """
    Represents the outcome of a content moderation check.
    """
    is_toxic: bool
    label: str
    score: float
    suggested_action: str = "NONE"

# Initialize the pipeline and cache it to avoid reloading the model
_toxicity_classifier = None

def _get_classifier():
    """Initializes and returns the toxicity classifier pipeline."""
    global _toxicity_classifier
    if _toxicity_classifier is None:
        print("AI Referee: Initializing toxicity classifier model...")
        _toxicity_classifier = pipeline(
            "text-classification",
            model="s-nlp/roberta_toxicity_classifier"
        )
        print("AI Referee: Model initialized.")
    return _toxicity_classifier

def analyze_player_chat(message: str) -> ModerationVerdict:
    """
    Analyzes a player's chat message for toxicity.
    """
    classifier = _get_classifier()
    results = classifier(message)

    # The model returns a list with a dictionary, e.g., [{'label': 'toxic', 'score': 0.99...}]
    result = results[0]
    label = result['label']
    score = result['score']

    is_toxic = label == 'toxic' and score > 0.8 # Use a threshold

    suggested_action = "NONE"
    if is_toxic:
        if score > 0.95:
            suggested_action = "MUTE"
        else:
            suggested_action = "WARN"

    return ModerationVerdict(
        is_toxic=is_toxic,
        label=label,
        score=score,
        suggested_action=suggested_action
    )

from pydantic import BaseModel
from typing import Dict, Any, Type, Optional
from enum import Enum
import abc
from transformers import pipeline
from .shared_models import GameTheme
from .safety_ai import is_content_safe

# --- Request/Response Models ---

class DialogueStrategyType(str, Enum):
    RULE_BASED = "RULE_BASED"
    LLM = "LLM"

class DialogueRequest(BaseModel):
    npc_id: str # Kept for API consistency, though not used by stateless LLM
    player_prompt: str
    strategy: DialogueStrategyType = DialogueStrategyType.RULE_BASED
    theme: Optional[GameTheme] = None

class DialogueResponse(BaseModel):
    npc_response: str

# --- Dialogue Generation Strategies ---

class DialogueStrategy(abc.ABC):
    """Abstract base class for all dialogue generation strategies."""
    @abc.abstractmethod
    def generate(self, request: DialogueRequest) -> DialogueResponse:
        pass

class RuleBasedStrategy(DialogueStrategy):
    """Generates dialogue based on simple keyword matching, aware of the theme."""
    def generate(self, request: DialogueRequest) -> DialogueResponse:
        prompt = request.player_prompt.lower()

        greeting = "Greetings, traveler."
        if request.theme and "sci-fi" in request.theme.prompt.lower():
            greeting = "State your purpose, organic."

        if "hello" in prompt or "hi" in prompt:
            response_text = greeting
        elif "quest" in prompt:
            response_text = "I may have a task for you. Are you brave enough?"
        elif "bye" in prompt:
            response_text = "Farewell."
        else:
            response_text = "Your words are noise to me."

        return DialogueResponse(npc_response=response_text)

class LLMStrategy(DialogueStrategy):
    """A stateless strategy that uses a pre-trained model for generation."""

    _pipeline = None

    def __init__(self):
        if LLMStrategy._pipeline is None:
            print("LLMStrategy: Initializing text-generation pipeline...")
            # Using a simpler pipeline task for stateless generation
            LLMStrategy._pipeline = pipeline("text-generation", model="microsoft/DialoGPT-medium")
            print("LLMStrategy: Pipeline initialized.")

    def generate(self, request: DialogueRequest) -> DialogueResponse:
        # Construct a prompt with theme context
        full_prompt = request.player_prompt
        if request.theme:
            system_prompt = f"In a '{request.theme.setting or 'fantasy'}' world with a '{request.theme.tone or 'neutral'}' tone, a character is asked: '{request.player_prompt}'. They reply: "
            full_prompt = system_prompt

        # Generate a response. Using text-generation is stateless.
        generated_outputs = self._pipeline(full_prompt, max_length=60, num_return_sequences=1, pad_token_id=50256)
        response_text = generated_outputs[0]['generated_text'].replace(full_prompt, "").strip()

        if not response_text:
            response_text = "I am unsure how to respond."

        # --- AI Safety Check ---
        if not is_content_safe(response_text):
            print(f"LLMStrategy: Unsafe content detected. Original response: '{response_text}'")
            response_text = "I am not able to discuss such things."

        return DialogueResponse(npc_response=response_text)

# --- Strategy Factory ---

_strategies: Dict[DialogueStrategyType, Type[DialogueStrategy]] = {
    DialogueStrategyType.RULE_BASED: RuleBasedStrategy,
    DialogueStrategyType.LLM: LLMStrategy,
}

def get_strategy(strategy_type: DialogueStrategyType) -> DialogueStrategy:
    """Factory function to get a strategy instance."""
    strategy_class = _strategies.get(strategy_type)
    if not strategy_class:
        raise ValueError(f"Unknown dialogue strategy: {strategy_type}")
    return strategy_class()

# --- Main Service Function ---

def generate_dialogue(request: DialogueRequest) -> DialogueResponse:
    """
    Generates a dialogue response using the specified strategy.
    """
    strategy = get_strategy(request.strategy)
    return strategy.generate(request)


# --- Old Placeholder Code (can be removed later) ---

class NPCRequest(BaseModel):
    request_type: str
    parameters: Dict[str, Any]

class NPCResponse(BaseModel):
    status: str
    data: Any

def process_npc_request(request: NPCRequest) -> NPCResponse:
    print(f"NPC AI received request: {request}")
    if request.request_type == "assign_quest_to_npc":
        return NPCResponse(status="success", data={"npc_id": "npc_bard_01", "quest_assigned": True})
    return NPCResponse(status="failure", data={"error": "Unknown request type"})

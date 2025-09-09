from pydantic import BaseModel
from typing import Dict, Any, Type, Optional
from enum import Enum
import abc
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .shared_models import GameTheme

# --- Request/Response Models ---

class DialogueStrategyType(str, Enum):
    RULE_BASED = "RULE_BASED"
    LLM = "LLM"

class DialogueRequest(BaseModel):
    npc_id: str
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

        # Default greeting
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
    """A strategy that uses a pre-trained conversational model from Hugging Face."""

    _model = None
    _tokenizer = None
    _chat_history = None

    def __init__(self):
        if LLMStrategy._model is None or LLMStrategy._tokenizer is None:
            print("LLMStrategy: Loading DialoGPT-medium model and tokenizer...")
            model_name = "microsoft/DialoGPT-medium"
            LLMStrategy._tokenizer = AutoTokenizer.from_pretrained(model_name)
            LLMStrategy._model = AutoModelForCausalLM.from_pretrained(model_name)
            print("LLMStrategy: Model and tokenizer loaded.")

    def generate(self, request: DialogueRequest) -> DialogueResponse:
        # Prepend a system prompt based on the theme to guide the LLM
        system_prompt = ""
        if request.theme:
            system_prompt = f"System: You are an NPC in a '{request.theme.setting or 'fantasy'}' world with a '{request.theme.tone or 'neutral'}' tone. The theme is '{request.theme.prompt}'. "

        full_prompt = system_prompt + request.player_prompt

        new_input_ids = self._tokenizer.encode(full_prompt + self._tokenizer.eos_token, return_tensors='pt')

        # For simplicity, we'll keep a short history. A real implementation would manage this per-conversation.
        bot_input_ids = torch.cat([self._chat_history, new_input_ids], dim=-1) if self._chat_history is not None else new_input_ids

        chat_history_ids = self._model.generate(
            bot_input_ids,
            max_length=1000,
            pad_token_id=self._tokenizer.eos_token_id
        )

        self._chat_history = chat_history_ids

        response_text = self._tokenizer.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

        if not response_text:
            response_text = "..."

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

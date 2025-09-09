from pydantic import BaseModel
from typing import Dict, Any, Type
from enum import Enum
import abc
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# --- Request/Response Models ---

class DialogueStrategyType(str, Enum):
    RULE_BASED = "RULE_BASED"
    LLM = "LLM"

class DialogueRequest(BaseModel):
    npc_id: str
    player_prompt: str
    strategy: DialogueStrategyType = DialogueStrategyType.RULE_BASED

class DialogueResponse(BaseModel):
    npc_response: str

# --- Dialogue Generation Strategies ---

class DialogueStrategy(abc.ABC):
    """Abstract base class for all dialogue generation strategies."""
    @abc.abstractmethod
    def generate(self, request: DialogueRequest) -> DialogueResponse:
        pass

class RuleBasedStrategy(DialogueStrategy):
    """Generates dialogue based on simple keyword matching."""
    def generate(self, request: DialogueRequest) -> DialogueResponse:
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

class LLMStrategy(DialogueStrategy):
    """A strategy that uses a pre-trained conversational model from Hugging Face."""

    # Cache the model and tokenizer so they are not reloaded on every request.
    _model = None
    _tokenizer = None
    _chat_history_ids = None

    def __init__(self):
        if LLMStrategy._model is None or LLMStrategy._tokenizer is None:
            print("LLMStrategy: Loading DialoGPT-medium model and tokenizer for the first time...")
            model_name = "microsoft/DialoGPT-medium"
            LLMStrategy._tokenizer = AutoTokenizer.from_pretrained(model_name)
            LLMStrategy._model = AutoModelForCausalLM.from_pretrained(model_name)
            print("LLMStrategy: Model and tokenizer loaded.")

    def generate(self, request: DialogueRequest) -> DialogueResponse:
        prompt = request.player_prompt

        # 1. Encode the new user input, add the eos_token and return a tensor in PyTorch
        new_user_input_ids = self._tokenizer.encode(prompt + self._tokenizer.eos_token, return_tensors='pt')

        # 2. Append the new user input tokens to the chat history
        bot_input_ids = torch.cat([self._chat_history_ids, new_user_input_ids], dim=-1) if self._chat_history_ids is not None else new_user_input_ids

        # 3. Generate a response while limiting the total chat history to 1000 tokens
        self._chat_history_ids = self._model.generate(
            bot_input_ids,
            max_length=1000,
            pad_token_id=self._tokenizer.eos_token_id
        )

        # 4. Decode the last bot reply and return it
        response_text = self._tokenizer.decode(self._chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)

        if not response_text:
            response_text = "I... I don't know what to say."

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

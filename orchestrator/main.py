from fastapi import FastAPI
from .puzzles import Puzzle
from .difficulty import PlayerEvent, DifficultySettings
from .hints import HintRequest, Hint
from .assistive_ai import AssistiveAIRequest, AssistiveAIResponse, process_player_request
import uuid

app = FastAPI()

# In-memory storage for player events and difficulty settings for simplicity
player_events: list[PlayerEvent] = []
current_difficulty_settings = DifficultySettings()

@app.get("/")
async def root():
    return {"message": "Hello from the ChronoVerse AI Orchestrator!"}

@app.post("/generate_puzzle", response_model=Puzzle)
async def generate_puzzle(context: dict):
    """
    Generates a puzzle based on the provided context.
    For now, it returns a hardcoded riddle puzzle.
    """
    puzzle_id = str(uuid.uuid4())
    puzzle = Puzzle(
        id=puzzle_id,
        type="riddle_lock",
        description="I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?",
        components={
            "riddle": "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?",
            "options": ["A map", "A dream", "A book", "A reflection"]
        },
        solution="A map",
        difficulty="easy"
    )
    return puzzle

@app.post("/player_event")
async def player_event(event: PlayerEvent):
    """
    Receives a player event and stores it.
    In a real application, this would trigger the difficulty adjustment logic.
    """
    print(f"Received player event: {event}")
    player_events.append(event)
    # Here you would add logic to analyze events and adjust difficulty
    return {"status": "event received"}

@app.get("/difficulty_settings", response_model=DifficultySettings)
async def get_difficulty_settings():
    """
    Returns the current difficulty settings.
    """
    return current_difficulty_settings

@app.post("/get_hint", response_model=Hint)
async def get_hint(request: HintRequest):
    """
    Generates a hint based on the player's context.
    For now, it returns a hardcoded hint.
    """
    print(f"Received hint request for player {request.player_id} with context: {request.context}")
    # In a real application, an AI model would generate a hint based on the context.
    hint = Hint(
        hint_text="Perhaps you should check the old library for clues.",
        hint_type="text"
    )
    return hint

@app.post("/assistive_ai_command", response_model=AssistiveAIResponse)
async def assistive_ai_command(request: AssistiveAIRequest):
    """
    Receives a command for the In-Game Assistive AI and processes it.
    """
    return process_player_request(request)

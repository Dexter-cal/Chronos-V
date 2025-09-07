from fastapi import FastAPI
from .puzzles import Puzzle
from .difficulty import PlayerEvent, DifficultySettings
from .hints import HintRequest, Hint
from .physics_ai import PhysicsQueryRequest, PhysicsQueryResponse, process_physics_query
from .animation_ai import AnimationRequest, AnimationResponse, process_animation_request
from .particles_ai import ParticleEffectRequest, ParticleEffectResponse, process_particle_effect_request
from .rocco_ai import HighLevelGoal, WorldState, orchestrate_goal, execute_command_sequence, AIResponse
from .map_location_ai import MapDataRequest, MapData, generate_map_data
from .world_builder_ai import generate_basic_map
from typing import List
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

@app.post("/physics_query", response_model=PhysicsQueryResponse)
async def physics_query(request: PhysicsQueryRequest):
    """
    Receives a physics query and passes it to the Physics AI for processing.
    """
    return process_physics_query(request)

@app.post("/generate_animation", response_model=AnimationResponse)
async def generate_animation(request: AnimationRequest):
    """
    Receives an animation request and passes it to the Animation AI for processing.
    """
    return process_animation_request(request)

@app.post("/generate_particle_effect", response_model=ParticleEffectResponse)
async def generate_particle_effect(request: ParticleEffectRequest):
    """
    Receives a particle effect request and passes it to the Particles AI for processing.
    """
    return process_particle_effect_request(request)

@app.post("/trigger_rocco_goal", response_model=List[AIResponse])
async def trigger_rocco_goal(goal: HighLevelGoal):
    """
    Triggers the Rocco AI to orchestrate a high-level goal.
    """
    # For now, we'll use a default world state.
    world_state = WorldState()

    # 1. Rocco generates a sequence of commands based on the goal
    commands = orchestrate_goal(goal, world_state)

    # 2. Rocco executes the commands and gets responses
    responses = execute_command_sequence(commands)

    return responses

@app.post("/get_map_data", response_model=MapData)
async def get_map_data(request: MapDataRequest):
    """
    Receives a request for map data and passes it to the Map & Location AI for processing.
    """
    return generate_map_data(request)

@app.get("/generate_map")
async def generate_map_endpoint(width: int = 20, height: int = 10):
    """
    Generates and returns a basic 2D map.
    """
    game_map = generate_basic_map(width, height)
    return {"map": game_map}

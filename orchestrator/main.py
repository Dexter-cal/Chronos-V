from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .puzzles import Puzzle
from .difficulty import PlayerEvent, DifficultySettings
from .hints import HintRequest, Hint
from .physics_ai import PhysicsQueryRequest, PhysicsQueryResponse, process_physics_query
from .animation_ai import AnimationRequest, AnimationResponse, process_animation_request
from .particles_ai import ParticleEffectRequest, ParticleEffectResponse, process_particle_effect_request
from .rocco_ai import HighLevelGoal, WorldState, orchestrate_goal, execute_command_sequence, AIResponse
from .map_location_ai import MapDataRequest, MapData, generate_map_data
from .npc_ai import DialogueRequest, DialogueResponse, generate_dialogue
from .quest_ai import Quest, generate_quest
from . import quest_manager
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

@app.post("/generate_dialogue", response_model=DialogueResponse)
async def generate_dialogue_endpoint(request: DialogueRequest):
    """
    Receives a player prompt and returns a generated NPC dialogue response.
    """
    return generate_dialogue(request)

@app.post("/quests/generate", response_model=Quest)
async def generate_quest_endpoint(player_level: int = 1):
    """
    Generates a new procedural quest and adds it to the quest manager.
    """
    new_quest = generate_quest(player_level)
    quest_manager.add_quest(new_quest)
    return new_quest

@app.get("/quests/{quest_id}", response_model=Quest)
async def get_quest_status_endpoint(quest_id: str):
    quest = quest_manager.get_quest_status(quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    return quest

@app.post("/quests/{quest_id}/accept", response_model=Quest)
async def accept_quest_endpoint(quest_id: str):
    quest = quest_manager.accept_quest(quest_id)
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found or cannot be accepted.")
    return quest

class ObjectiveProgressRequest(BaseModel):
    objective_id: str
    progress_amount: int

@app.post("/quests/{quest_id}/progress", response_model=Quest)
async def update_quest_progress_endpoint(quest_id: str, progress: ObjectiveProgressRequest):
    quest = quest_manager.update_objective_progress(
        quest_id, progress.objective_id, progress.progress_amount
    )
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found or not in progress.")
    return quest

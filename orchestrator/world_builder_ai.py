from pydantic import BaseModel
from typing import Dict, Any

# Placeholder for World Builder AI models and logic
# In a real implementation, this module would use procedural generation algorithms.

class WorldBuilderRequest(BaseModel):
    request_type: str
    parameters: Dict[str, Any]

class WorldBuilderResponse(BaseModel):
    status: str
    data: Any

def process_world_builder_request(request: WorldBuilderRequest) -> WorldBuilderResponse:
    print(f"World Builder AI received request: {request}")
    # Placeholder logic
    if request.request_type == "verify_or_create_location":
        return WorldBuilderResponse(status="success", data={"location_id": "dungeon_01", "status": "created"})
    return WorldBuilderResponse(status="failure", data={"error": "Unknown request type"})

import random

def generate_basic_map(width: int, height: int) -> list[list[str]]:
    """
    Generates a simple 2D map with basic terrain.
    '~' = water
    '.' = plains
    '^' = mountain
    """
    terrain = ['~', '.', '^']
    # Add more plains than other types to make it look more natural
    weights = [0.1, 0.8, 0.1]

    game_map = []
    for y in range(height):
        row = []
        for x in range(width):
            # Choose a terrain type based on the weights
            chosen_terrain = random.choices(terrain, weights)[0]
            row.append(chosen_terrain)
        game_map.append(row)

    return game_map

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import numpy as np
import noise
import random

def generate_basic_map(width: int, height: int, scale: float = 25.0, octaves: int = 4, persistence: float = 0.5, lacunarity: float = 2.0) -> list[list[str]]:
    """
    Generates a 2D map using Perlin noise for more natural terrain.
    """
    world = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            world[y][x] = noise.pnoise2(y / scale, x / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity, repeatx=width, repeaty=height, base=42)

    terrain_map = { -1.0: '~', -0.2: '~', 0.0: '#', 0.4: '.', 0.7: '*', 1.0: '^' }
    game_map = []
    for y in range(height):
        row = []
        for x in range(width):
            value = world[y][x]
            terrain_symbol = '~'
            for threshold, symbol in terrain_map.items():
                if value <= threshold:
                    terrain_symbol = symbol
                    break
            row.append(terrain_symbol)
        game_map.append(row)
    return game_map

def place_themed_locations(game_map: list[list[str]], locations: List[str]) -> tuple[list[list[str]], dict]:
    """
    Places themed locations on the map in suitable, non-water locations.
    Returns the modified map and a dictionary mapping location names to coordinates.
    """
    placed_locations = {}
    height = len(game_map)
    width = len(game_map[0])

    # Find all possible land tiles for placement
    land_tiles = []
    for y in range(height):
        for x in range(width):
            if game_map[y][x] not in ['~']: # Can't place on water
                land_tiles.append((y, x))

    random.shuffle(land_tiles)

    for location_name in locations:
        if not land_tiles:
            break # No more suitable tiles to place locations

        y, x = land_tiles.pop()
        game_map[y][x] = 'L' # 'L' for Location
        placed_locations[location_name] = {"y": y, "x": x}

    return game_map, placed_locations

# (Keep the old placeholder models and function for now)
class WorldBuilderRequest(BaseModel):
    request_type: str
    parameters: Dict[str, Any]
class WorldBuilderResponse(BaseModel):
    status: str
    data: Any
def process_world_builder_request(request: WorldBuilderRequest) -> WorldBuilderResponse:
    if request.request_type == "verify_or_create_location":
        return WorldBuilderResponse(status="success", data={"location_id": "dungeon_01", "status": "created"})
    return WorldBuilderResponse(status="failure", data={"error": "Unknown request type"})

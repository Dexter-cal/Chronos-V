from pydantic import BaseModel
from typing import Dict, Any
import numpy as np
import noise

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

def generate_basic_map(width: int, height: int, scale: float = 25.0, octaves: int = 4, persistence: float = 0.5, lacunarity: float = 2.0) -> list[list[str]]:
    """
    Generates a 2D map using Perlin noise for more natural terrain.
    """
    # Generate a 2D numpy array of zeros
    world = np.zeros((height, width))

    # Generate Perlin noise
    for y in range(height):
        for x in range(width):
            world[y][x] = noise.pnoise2(y / scale,
                                        x / scale,
                                        octaves=octaves,
                                        persistence=persistence,
                                        lacunarity=lacunarity,
                                        repeatx=width,
                                        repeaty=height,
                                        base=42) # Using a base for reproducibility

    # Define terrain thresholds and their corresponding symbols
    terrain_map = {
        -1.0: ('~', 'Deep Water'),
        -0.2: ('~', 'Shallow Water'),
         0.0: ('#', 'Beach'),
         0.4: ('.', 'Plains'),
         0.7: ('*', 'Forest'),
         1.0: ('^', 'Mountain')
    }

    # Convert the noise map to a terrain map
    game_map = []
    for y in range(height):
        row = []
        for x in range(width):
            value = world[y][x]
            terrain_symbol = '~' # Default to water
            for threshold, (symbol, _) in terrain_map.items():
                if value <= threshold:
                    terrain_symbol = symbol
                    break
            row.append(terrain_symbol)
        game_map.append(row)

    return game_map

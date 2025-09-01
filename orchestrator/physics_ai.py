from pydantic import BaseModel
from typing import Dict, Any, List

class PhysicsQueryRequest(BaseModel):
    """
    Represents a request to the Physics AI to query the state of the physics world.
    """
    query_type: str  # e.g., "is_area_clear", "get_surface_material"
    parameters: Dict[str, Any]

class PhysicsQueryResponse(BaseModel):
    """
    Represents a response from the Physics AI to a physics query.
    """
    query_type: str
    data: Any
    success: bool = True
    status: str # "success" or "failure"

class Vector3(BaseModel):
    """
    A simple Pydantic model to represent a 3D vector.
    """
    x: float
    y: float
    z: float

# --- Hardcoded World Data for Rule-Based Logic ---
# In a real implementation, this data would come from the World State managed by Rocco AI.
OBSTACLES = [
    {"center": Vector3(x=5, y=0, z=5), "size": Vector3(x=2, y=2, z=2)},
    {"center": Vector3(x=-10, y=0, z=15), "size": Vector3(x=5, y=10, z=5)},
]

# --- Core Physics AI Logic ---
def process_physics_query(request: PhysicsQueryRequest) -> PhysicsQueryResponse:
    """
    Processes a physics query using simple, rule-based logic.
    """
    print(f"Received physics query: {request}")

    if request.query_type == "is_area_clear":
        query_pos = Vector3(**request.parameters["position"])
        is_clear = True
        for obstacle in OBSTACLES:
            # Simple AABB collision check
            if (abs(query_pos.x - obstacle["center"].x) * 2 < (2 + obstacle["size"].x) and
                abs(query_pos.y - obstacle["center"].y) * 2 < (2 + obstacle["size"].y) and
                abs(query_pos.z - obstacle["center"].z) * 2 < (2 + obstacle["size"].z)):
                is_clear = False
                break
        result = is_clear

    elif request.query_type == "get_surface_material":
        # Placeholder logic: return "grass" if y=0, else "air"
        query_pos = Vector3(**request.parameters["position"])
        result = "grass" if query_pos.y == 0 else "air"

    elif request.query_type == "calculate_trajectory":
        # Placeholder logic: return a simple linear trajectory
        start = Vector3(**request.parameters["start"])
        end = Vector3(**request.parameters["end"])
        result = [start, end]

    elif request.query_type == "validate_quest_physics":
        # Placeholder logic: always return True
        result = True

    else:
        return PhysicsQueryResponse(
            query_type=request.query_type,
            data={"error": "Unknown query type"},
            success=False,
            status="failure"
        )

    return PhysicsQueryResponse(
        query_type=request.query_type,
        data=result,
        success=True,
        status="success"
    )

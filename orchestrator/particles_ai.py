from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class ParticleSystemParameters(BaseModel):
    """
    Represents the parameters for a Godot particle system (GPUParticles3D).
    (Simplified placeholder)
    """
    amount: int = 100
    lifetime: float = 2.0
    explosiveness: float = 0.8
    # ... other parameters like color, velocity, emission_shape, etc.

class ParticleEffectRequest(BaseModel):
    """
    Represents a request to the Particles AI to generate a particle effect.
    """
    effect_type: str  # e.g., "campfire", "rain", "fireball"
    context: Dict[str, Any] = {}

class ParticleEffectResponse(BaseModel):
    """
    Represents a response from the Particles AI with the generated effect parameters.
    """
    effect_type: str
    parameters: ParticleSystemParameters

# --- Core Particles AI Logic ---
def process_particle_effect_request(request: ParticleEffectRequest) -> ParticleEffectResponse:
    """
    Processes a particle effect request using simple, rule-based logic.
    """
    print(f"Received particle effect request: {request}")

    params = ParticleSystemParameters()

    if request.effect_type == "campfire":
        params.amount = 200
        params.lifetime = 2.5
        params.explosiveness = 0.6
        # In a real implementation, we would also set color ramps, velocity, etc.
    elif request.effect_type == "rain":
        params.amount = 4000
        params.lifetime = 10.0
        params.explosiveness = 0.0
    elif request.effect_type == "fireball":
        params.amount = 500
        params.lifetime = 0.8
        params.explosiveness = 1.0
    else:
        # Default particle effect
        params.amount = 100
        params.lifetime = 1.0
        params.explosiveness = 0.5

    return ParticleEffectResponse(
        effect_type=request.effect_type,
        parameters=params
    )

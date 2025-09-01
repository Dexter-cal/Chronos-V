from pydantic import BaseModel
from typing import Dict, Any, List

# Import the process functions from the other AI modules
from . import narrative_ai, world_builder_ai, npc_ai, physics_ai, animation_ai, particles_ai

class HighLevelGoal(BaseModel):
    """
    Represents a high-level goal for Rocco to achieve.
    """
    goal_type: str  # e.g., "generate_new_quest", "populate_region"
    parameters: Dict[str, Any]

class AICommand(BaseModel):
    """
    Represents a command from Rocco to another AI module.
    """
    target_module: str  # e.g., "NarrativeAI", "WorldBuilderAI"
    command: str
    payload: Dict[str, Any]

class AIResponse(BaseModel):
    """
    Represents a generic response from an AI module to Rocco.
    """
    source_module: str
    status: str  # e.g., "success", "failure"
    data: Any

class WorldState(BaseModel):
    """
    Represents Rocco's high-level understanding of the game world.
    (Simplified placeholder)
    """
    story_progress: float = 0.0
    player_level: int = 1
    key_npc_states: Dict[str, str] = {}

# --- Rocco's Core Logic ---
def orchestrate_goal(goal: HighLevelGoal, world_state: WorldState) -> List[AICommand]:
    """
    Takes a high-level goal and generates a sequence of commands for other AI modules.
    This is a rule-based implementation of the orchestration logic.
    """
    print(f"Rocco AI is orchestrating goal: {goal.goal_type}")
    commands = []

    if goal.goal_type == "generate_new_quest":
        quest_difficulty = "easy" if world_state.player_level < 5 else "medium"

        commands.append(AICommand(
            target_module="NarrativeAI",
            command="generate_quest_concept",
            payload={"player_level": world_state.player_level, "difficulty": quest_difficulty}
        ))
        commands.append(AICommand(
            target_module="WorldBuilderAI",
            command="verify_or_create_location",
            payload={"location_type": "dungeon", "difficulty": quest_difficulty}
        ))
        commands.append(AICommand(
            target_module="NPCAI",
            command="assign_quest_to_npc",
            payload={"quest_difficulty": quest_difficulty, "location": "placeholder_dungeon_entrance"}
        ))
        commands.append(AICommand(
            target_module="PhysicsAI",
            command="validate_quest_physics",
            payload={"quest_objectives": ["find_item", "defeat_boss"]}
        ))
    elif goal.goal_type == "populate_region":
        # Placeholder for another workflow
        commands.append(AICommand(
            target_module="WorldBuilderAI",
            command="get_region_data",
            payload={"region_name": goal.parameters.get("region_name")}
        ))
        commands.append(AICommand(
            target_module="NPCAI",
            command="populate_with_npcs",
            payload={"region_data": "placeholder"}
        ))

    print(f"Rocco AI generated {len(commands)} commands for goal '{goal.goal_type}'.")
    return commands

def execute_command_sequence(commands: List[AICommand]) -> List[AIResponse]:
    """
    Executes a sequence of AI commands and collects the responses.
    """
    print(f"Rocco AI is executing a sequence of {len(commands)} commands.")
    responses = []

    # Map target module names to their process functions
    module_map = {
        "NarrativeAI": narrative_ai.process_narrative_request,
        "WorldBuilderAI": world_builder_ai.process_world_builder_request,
        "NPCAI": npc_ai.process_npc_request,
        "PhysicsAI": physics_ai.process_physics_query,
        "AnimationAI": animation_ai.process_animation_request,
        "ParticlesAI": particles_ai.process_particle_effect_request,
    }

    for command in commands:
        try:
            if command.target_module in module_map:
                # This is a simplified way to handle requests.
                # In a real implementation, we would need to construct the correct
                # request model for each module. For now, we pass the payload directly.
                request_model = None
                if command.target_module == "NarrativeAI":
                    request_model = narrative_ai.NarrativeRequest(request_type=command.command, parameters=command.payload)
                elif command.target_module == "WorldBuilderAI":
                    request_model = world_builder_ai.WorldBuilderRequest(request_type=command.command, parameters=command.payload)
                elif command.target_module == "NPCAI":
                    request_model = npc_ai.NPCRequest(request_type=command.command, parameters=command.payload)
                elif command.target_module == "PhysicsAI":
                    request_model = physics_ai.PhysicsQueryRequest(query_type=command.command, parameters=command.payload)
                elif command.target_module == "AnimationAI":
                    request_model = animation_ai.AnimationRequest(**command.payload)
                elif command.target_module == "ParticlesAI":
                    request_model = particles_ai.ParticleEffectRequest(effect_type=command.command, context=command.payload)

                if request_model:
                    response = module_map[command.target_module](request_model)
                    responses.append(AIResponse(
                        source_module=command.target_module,
                        status=response.status,
                        data=response.data
                    ))
            else:
                print(f"Unknown target module: {command.target_module}")
                responses.append(AIResponse(
                    source_module=command.target_module,
                    status="failure",
                    data={"error": "Unknown target module"}
                ))
        except Exception as e:
            print(f"Error executing command for module {command.target_module}: {e}")
            responses.append(AIResponse(
                source_module=command.target_module,
                status="failure",
                data={"error": str(e)}
            ))

    print("Rocco AI finished executing command sequence.")
    return responses

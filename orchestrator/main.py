from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from .puzzles import Puzzle
from .difficulty import PlayerEvent, DifficultySettings
from .hints import HintRequest, Hint
from .physics_ai import PhysicsQueryRequest, PhysicsQueryResponse, process_physics_query
from .animation_ai import AnimationRequest, AnimationResponse, process_animation_request
from .particles_ai import ParticleEffectRequest, ParticleEffectResponse, process_particle_effect_request
from .rocco_ai import HighLevelGoal, WorldState, orchestrate_goal, execute_command_sequence, AIResponse
from .map_location_ai import MapDataRequest, MapData, generate_map_data
from . import badfiles_generator
from . import security_scanner
from typing import List
import uuid
import os
import shutil

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


GENERATOR_MAP = {
    "xxe": (badfiles_generator.generate_xxe_file, "xxe.xml"),
    "billion_laughs": (badfiles_generator.generate_billion_laughs_file, "billion_laughs.xml"),
    "quadratic_blowup": (badfiles_generator.generate_quadratic_blowup_file, "quadratic_blowup.xml"),
    "zip_traversal": (badfiles_generator.create_archive_with_traversal, "traversal.zip"),
    "zip_bomb": (badfiles_generator.create_compressed_archive_bomb, "bomb.zip"),
    "gz_bomb": (badfiles_generator.create_gzipped_bomb, "bomb.gz"),
    "svg": (badfiles_generator.generate_malicious_svg, "malicious.svg"),
    "double_extension": (badfiles_generator.generate_file_with_double_extension, "file.txt.exe"),
    "file_in_parent": (badfiles_generator.generate_file_in_parent_directory, "file_in_parent.txt"),
    "csv_injection": (badfiles_generator.generate_csv_formula_injection, "formula_injection.csv"),
    "gifar": (badfiles_generator.generate_gifar, "gifar.gif"),
    "json_deserialization": (badfiles_generator.generate_json_deserialization_payload, "payload.json"),
    "pdf_js": (badfiles_generator.generate_pdf_with_js, "pdf_with_js.pdf"),
    "dde": (badfiles_generator.generate_dde_payload, "dde.csv"),
    "pdf_zip_polyglot": (badfiles_generator.generate_pdf_zip_polyglot, "polyglot.pdf"),
    "docx": (badfiles_generator.generate_malicious_docx, "malicious.docx"),
    "xls": (badfiles_generator.generate_malicious_xls, "malicious.xls"),
    "pickle": (badfiles_generator.generate_pickle_payload, "payload.pkl"),
    "tar_traversal": (badfiles_generator.generate_tar_traversal, "traversal.tar"),
    "yaml": (badfiles_generator.generate_yaml_payload, "payload.yaml"),
}

@app.get("/generate/{filetype}")
async def generate_file(filetype: str):
    """
    Generates a malicious file of the specified type and returns it.
    """
    if filetype not in GENERATOR_MAP:
        return {"error": "Invalid file type"}

    generator_func, filename = GENERATOR_MAP[filetype]

    # Ensure the output directory exists
    output_dir = "generated_files"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    generator_func(filepath)

    return FileResponse(filepath, media_type='application/octet-stream', filename=filename)


def run_all_scanners(filepath):
    """
    Runs all available scanners on a given file and aggregates the results.
    """
    results = []
    filename = os.path.basename(filepath)

    if filename.endswith(".xml"):
        results.append(security_scanner.scan_xml_for_xxe(filepath))
        results.append(security_scanner.scan_xml_for_billion_laughs(filepath))
    elif filename.endswith(".zip"):
        results.append(security_scanner.scan_zip_for_traversal(filepath))
        results.append(security_scanner.scan_zip_for_bomb(filepath))
    elif filename.endswith(".json"):
        results.append(security_scanner.scan_json_for_deserialization(filepath))
    elif filename.endswith(".pdf"):
        results.append(security_scanner.scan_pdf_for_js(filepath))
        results.append(security_scanner.scan_for_pdf_zip_polyglot(filepath))
    elif filename.endswith(".csv"):
        results.append(security_scanner.scan_csv_for_dde(filepath))
    elif filename.endswith(".docx"):
        results.append(security_scanner.scan_docx_for_links(filepath))
    elif filename.endswith(".xls"):
        results.append(security_scanner.scan_xls_for_formulas(filepath))
    elif filename.endswith(".pkl"):
        results.append(security_scanner.scan_pickle_for_rce(filepath))
    elif filename.endswith(".tar"):
        results.append(security_scanner.scan_tar_for_traversal(filepath))
    elif filename.endswith(".yaml"):
        results.append(security_scanner.scan_yaml_for_deserialization(filepath))

    vulnerabilities = [res for res in results if res and res["status"] == "vulnerable"]
    return vulnerabilities if vulnerabilities else [{"status": "clean", "details": "No vulnerabilities detected."}]

@app.post("/scan")
async def scan_file_endpoint(file: UploadFile = File(...)):
    """
    Receives a file, saves it temporarily, and then scans it for vulnerabilities.
    """
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    filepath = os.path.join(temp_dir, file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    scan_results = run_all_scanners(filepath)

    # Clean up the temporary file
    os.remove(filepath)

    return {"filename": file.filename, "scan_results": scan_results}

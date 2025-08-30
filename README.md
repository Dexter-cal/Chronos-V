# ChronoVerse

This is the root directory for the ChronoVerse project, an AI-driven game engine.

## Project Structure

*   `/godot`: This directory contains the Godot project for the game client. This is where all game scenes, scripts, and assets will be located.
*   `/orchestrator`: This directory contains the Python-based AI orchestrator server. It uses FastAPI to coordinate the various AI modules and manage the game state.

## Getting Started

1.  **Run the AI Orchestrator:**
    ```bash
    cd orchestrator
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```
2.  **Open the Godot project:**
    *   Open the Godot editor.
    *   Import the `godot/project.godot` file.
    *   Run the project from the editor.

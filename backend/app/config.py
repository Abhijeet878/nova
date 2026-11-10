"""
CONFIG.PY — Central Configuration Loader
=========================================
WHAT IT DOES:
    Reads settings from the .env file and makes them available
    to every other file in the project.

WHY IT EXISTS:
    Instead of hardcoding "qwen2.5:3b" or "http://localhost:11434"
    in 10 different files, we define them ONCE here. If you want
    to switch to a different model (e.g., llama3.2:3b), you only
    change the .env file — nothing else.

FOR JUDGES:
    "Our configuration is centralized. Switching the underlying
    LLM model requires changing a single environment variable,
    not modifying any source code."
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()

# ─── LLM Configuration ──────────────────────────────────────
# These control which AI model we use and where it's running.
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ─── Server Configuration ───────────────────────────────────
API_PORT: int = int(os.getenv("API_PORT", "8080"))
UI_PORT: int = int(os.getenv("UI_PORT", "7860"))

# ─── Agent Behavior ─────────────────────────────────────────
# MAX_RETRIES: How many times the Recovery Engine retries a failed step
# MAX_AGENT_ITERATIONS: Safety cap on ReAct loop iterations (prevents infinite loops)
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
MAX_AGENT_ITERATIONS: int = int(os.getenv("MAX_AGENT_ITERATIONS", "15"))
VERBOSE: bool = os.getenv("VERBOSE", "true").lower() == "true"

# ─── File Paths ──────────────────────────────────────────────
# WORKSPACE_DIR: Where agents read input files from
# OUTPUTS_DIR:   Where agents save their generated reports/results
PROJECT_ROOT = Path(__file__).parent.parent.parent  # autopilot-ai/
WORKSPACE_DIR: Path = Path(os.getenv("WORKSPACE_DIR", str(PROJECT_ROOT / "workspace")))
OUTPUTS_DIR: Path = Path(os.getenv("OUTPUTS_DIR", str(PROJECT_ROOT / "outputs")))

# Ensure directories exist
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

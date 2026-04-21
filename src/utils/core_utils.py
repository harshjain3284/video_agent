import os
import re
from src.config import ASSETS_DIR

def format_aspect_ratio(ratio_str: str, target_model_type: str = "veo"):
    """
    Standardizes aspect ratio strings for specific model requirements.
    - gemini: 16-9
    - veo / imagen: 16:9
    """
    # Extract the numbers (e.g., from "YouTube (16:9)")
    matches = re.findall(r"(\d+):(\d+)", ratio_str)
    if matches:
        w, h = matches[0]
        if target_model_type == "gemini":
            return f"{w}-{h}"
        return f"{w}:{h}"
    return "16:9" # Safety fallback

def ensure_session_dir(session_id: str):
    """Creates and returns the path for a specific session's assets."""
    path = os.path.join(ASSETS_DIR, session_id)
    os.makedirs(path, exist_ok=True)
    return path

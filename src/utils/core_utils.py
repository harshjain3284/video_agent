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

def retry_with_backoff(fn, retries=3, initial_delay=5, backoff_factor=2, error_codes=["429", "503", "high demand", "quota"]):
    """
    Executes a function and retries on specific AI-related errors.
    """
    import time
    delay = initial_delay
    for i in range(retries + 1):
        try:
            return fn()
        except Exception as e:
            err_msg = str(e).lower()
            if any(code in err_msg for code in error_codes) and i < retries:
                print(f"   ⏳ Attempt {i+1} failed ({err_msg[:50]}...). Retrying in {delay}s...")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                raise e

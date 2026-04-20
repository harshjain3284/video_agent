import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (Set these in a .env file)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Video Settings
VIDEO_FPS = 24
SCENE_DURATION = 5  # seconds per scene
OUTPUT_DIR = "output"
ASSETS_DIR = "assets"

# Image Models (FLUX is default for "Real" look)
IMAGE_MODELS = {
    "Nano Banana (Fast)": "gemini-2.5-flash-image",
    "Nano Banana 2 (3.1 Flash)": "gemini-3.1-flash-image-preview",
    "Nano Banana Pro (Gemini 3)": "gemini-3-pro-image-preview",
    "Imagen 4.0 (Ultra High Quality)": "imagen-4.0-generate-001",
    "FLUX (Hyper-Realistic)": "black-forest-labs/FLUX.1-schnell",
}
DEFAULT_MODEL = "Nano Banana (Fast)"

# Video Models
VIDEO_MODELS = {
    "Veo 3.1 (Cinematic Video)": "veo-3.1-generate-preview",
    "Veo 3.1 (Fast Video)": "veo-3.1-fast-generate-preview",
    "MoviePy (Standard Fades)": "moviepy-static",
}
DEFAULT_VIDEO_MODEL = "Veo 3.1 (Cinematic Video)"



# Video Aspect Ratios
ASPECT_RATIOS = {
    "YouTube (16:9)": {"ratio": "16:9", "width": 1024, "height": 576},
    "Phone / Reels (9:16)": {"ratio": "9:16", "width": 576, "height": 1024},
    "Instagram / Square (1:1)": {"ratio": "1:1", "width": 1024, "height": 1024}
}
DEFAULT_ASPECT_RATIO = "YouTube (16:9)"

# Helper to clean model IDs and handle API-specific formatting
def format_aspect_ratio(ratio_str: str, target_model_type: str = "veo"):
    """
    Standardizes aspect ratio strings for specific model requirements.
    - gemini: 16-9
    - veo: 16:9
    """
    # Extract the numbers regardless of if it came as "16:9" or "YouTube (16:9)"
    import re
    matches = re.findall(r"(\d+):(\d+)", ratio_str)
    if matches:
        w, h = matches[0]
        if target_model_type == "gemini":
            return f"{w}-{h}"
        return f"{w}:{h}"
    return "16:9" # Safety fallback

def ensure_session_dir(session_id):
    path = os.path.join(ASSETS_DIR, session_id)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

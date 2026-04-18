import os
from dotenv import load_dotenv

load_dotenv()

# API Keys (Set these in a .env file)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# Video Settings
VIDEO_FPS = 24
SCENE_DURATION = 5  # seconds per scene
OUTPUT_DIR = "output"
ASSETS_DIR = "assets"

# Image Models (FLUX is default for "Real" look)
IMAGE_MODELS = {
    "FLUX (Hyper-Realistic)": "black-forest-labs/FLUX.1-schnell",
    "SDXL (Cinematic)": "stabilityai/stable-diffusion-xl-base-1.0",
    "Realistic Vision": "SG_161222/Realistic_Vision_V5.1",
    "OpenJourney": "prompthero/openjourney",
    "DreamShaper": "Lykon/DreamShaper_8",
    "Absolute Reality": "Lykon/AbsoluteReality_V1.8.1",
    "Pollinations (Free Fallback)": "pollinations"
}
DEFAULT_MODEL = "FLUX (Hyper-Realistic)"



# Video Aspect Ratios
ASPECT_RATIOS = {
    "YouTube (16:9)": {"ratio": "16:9", "width": 1024, "height": 576},
    "Phone / Reels (9:16)": {"ratio": "9:16", "width": 576, "height": 1024},
    "Instagram / Square (1:1)": {"ratio": "1:1", "width": 1024, "height": 1024}
}
DEFAULT_ASPECT_RATIO = "YouTube (16:9)"

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

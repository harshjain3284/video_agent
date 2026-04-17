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

# Image Models (Open Source)
IMAGE_MODELS = {
    "SD_1.5": "runwayml/stable-diffusion-v1-5",
    "SDXL": "stabilityai/stable-diffusion-xl-base-1.0",
    "FLUX": "black-forest-labs/FLUX.1-schnell"
}
DEFAULT_MODEL = "FLUX"  # Changed to FLUX for best quality

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

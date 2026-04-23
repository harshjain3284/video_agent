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

# Image Generation Models (Actual Creators)
IMAGE_MODELS = {
    "Nano Banana (Fast)": "gemini-2.5-flash-image",
    "Nano Banana 2 (3.1 Flash)": "gemini-3.1-flash-image-preview",
    "Nano Banana Pro (Gemini 3)": "gemini-3-pro-image-preview",
    "Imagen 4.0 (Ultra High Quality)": "imagen-4.0-generate-001",
    "FLUX (Hyper-Realistic)": "black-forest-labs/FLUX.1-schnell",
}
DEFAULT_MODEL = "Nano Banana (Fast)"

# Vision Analysis Models (Image Understanders for Motion)
VISION_MODELS = {
    "Gemma 4 Dense (31B Elite)": "gemma-4-31b-it",
    "Gemma 4 MoE (26B Specialist)": "gemma-4-26b-a4b-it",
    "Gemini 3.1 Flash Lite (Standard)": "gemini-3.1-flash-lite-preview",
    "Gemini 2.0 Flash (Secondary)": "gemini-2.0-flash",
}
DEFAULT_VISION_MODEL = "Gemma 4 Dense (31B Elite)"

# Video Models
VIDEO_MODELS = {
    "Veo 3.1 (Cinematic Video)": "veo-3.1-generate-preview",
    "Veo 3.1 (Fast Video)": "veo-3.1-fast-generate-preview",
    "MoviePy (Standard Fades)": "moviepy-static",
}
DEFAULT_VIDEO_MODEL = "Veo 3.1 (Cinematic Video)"
 
# Voice Settings
VOICE_LANGUAGES = {
    "English (US)": {"lang": "English", "voice": "en-US-AvaNeural"},
    "Hindi (India)": {"lang": "Hindi", "voice": "hi-IN-MadhurNeural"},
    "Spanish (Spain)": {"lang": "Spanish", "voice": "es-ES-ElviraNeural"},
    "French (France)": {"lang": "French", "voice": "fr-FR-DeniseNeural"},
    "Bengali (India)": {"lang": "Bengali", "voice": "bn-IN-TanishaaNeural"}
}
DEFAULT_VOICE_LANGUAGE = "Hindi (India)"



# Video Aspect Ratios
ASPECT_RATIOS = {
    "YouTube (16:9)": {"ratio": "16:9", "width": 1024, "height": 576},
    "Phone / Reels (9:16)": {"ratio": "9:16", "width": 576, "height": 1024},
    # "Instagram / Square (1:1)": {"ratio": "1:1", "width": 1024, "height": 1024}
}
DEFAULT_ASPECT_RATIO = "YouTube (16:9)"

# --- Estimated Production Costs (USD) ---
COSTS = {
    "image": {
        "gemini": 0.005,    # Standard Gemini multimodal images
        "imagen": 0.030,    # High-quality Imagen generation
        "default": 0.010
    },
    "video_per_sec": {
        "veo": 0.10,        # $0.10 per second of high-end AI Video
        "default": 0.05
    },
    "llm_per_1k": {
        "gemini": 0.0001,
        "groq": 0.0,        # Assuming free tier
    }
}

# --- Strategic Content Configs ---
BRAND_STYLES = {
    "consultease.app": "Modern Indian corporate office, clean blue and white tones, professional Indian expert in formal attire, realistic lighting, sharp 8k textures.",
    "consultease.professionals": "Dynamic professional setting in a premium Bangalore or Mumbai office interior, professional Indian experts, realistic and sharp focus.",
    "default": "Authentic professional Indian setting, photorealistic, cinematic shot on 35mm lens."
}

STRATEGIC_CONFIGS = {
    "categories": [
        "Income Tax", "Tenant / Landlord", "Professional Growth", 
        "Employment Disputes", "Online Fraud", "GST", 
        "Domestic Violence", "Property"
    ],
    "post_types": ["Hook", "Relatable", "Authority", "Scenario"],
    "hook_types": ["Pain", "Contrarian"]
}

# Mapping Post Type to specific voice vibes (using Edge-TTS voices)
STRATEGIC_VOICES = {
    "Authority": "hi-IN-MadhurNeural",  # Authoritative Male
    "Relatable": "hi-IN-AnanyaNeural",  # Softer Female
    "Hook": "hi-IN-AnanyaNeural",      # Energetic
    "Scenario": "hi-IN-MadhurNeural"
}

# Ensure base directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

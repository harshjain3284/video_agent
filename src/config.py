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

# --- 🎯 MASTER MODEL REGISTRY ---
# This is the single source of truth for every model used in the pipeline.
MODEL_REGISTRY = {
    # 1. Narrative & Strategy (Groq)
    "script_writer": "llama-3.3-70b-versatile",
    "character_designer": "llama-3.1-8b-instant",
    "shot_architect": "llama-3.3-70b-versatile",

    # 2. Image Production (Google/HF)
    "image_primary": "imagen-4.0-generate-001",
    "image_standard": "gemini-3.1-flash-image-preview",
    "image_fast": "gemini-2.5-flash-image",
    "image_fallback": "black-forest-labs/FLUX.1-schnell",
    
    # 3. Identity & Vision Analysis (Google)
    "identity_anchor": "gemini-3.1-flash-lite-preview",
    "identity_backup_1": "gemma-4-31b-it",
    "identity_backup_2": "gemini-2.0-flash",

    # 4. Video Motion (Google Veo)
    "video_cinematic": "veo-3.1-generate-preview",
    "video_fast": "veo-3.1-fast-generate-preview",
}

# UI Display Mappings (Referencing the Registry)
IMAGE_MODELS = {
    "Imagen 4.0 (Ultra)": MODEL_REGISTRY["image_primary"],
    "Gemini 3.1 (Standard)": MODEL_REGISTRY["image_standard"],
    "Gemini 2.5 (Fast)": MODEL_REGISTRY["image_fast"],
    "FLUX (Realistic)": MODEL_REGISTRY["image_fallback"],
}
DEFAULT_MODEL = "Gemini 3.1 (Standard)"

VIDEO_MODELS = {
    "Veo 3.1 (Cinematic)": MODEL_REGISTRY["video_cinematic"],
    "Veo 3.1 (Fast)": MODEL_REGISTRY["video_fast"],
}
DEFAULT_VIDEO_MODEL = "Veo 3.1 (Cinematic)"
 
# Voice Settings
VOICE_LANGUAGES = {
    "English (US)": {"lang": "English", "male": "en-US-AndrewNeural", "female": "en-US-AvaNeural"},
    "Hindi (India)": {"lang": "Hindi", "male": "hi-IN-MadhurNeural", "female": "hi-IN-SwaraNeural"},
    "Spanish (Spain)": {"lang": "Spanish", "male": "es-ES-AlvaroNeural", "female": "es-ES-ElviraNeural"},
    "French (France)": {"lang": "French", "male": "fr-FR-HenriNeural", "female": "fr-FR-DeniseNeural"},
    "Bengali (India)": {"lang": "Bengali", "male": "bn-IN-BashkarNeural", "female": "bn-IN-TanishaaNeural"}
}
DEFAULT_VOICE_LANGUAGE = "Hindi (India)"
DEFAULT_VOICE_GENDER = "Female"




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
    "Relatable": "hi-IN-SwaraNeural",  # Softer Female
    "Hook": "hi-IN-SwaraNeural",      # Energetic
    "Scenario": "hi-IN-MadhurNeural"
}

# Ensure base directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

import os
from dotenv import load_dotenv

# 1. ENVIRONMENT & ACCESS
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 2. GLOBAL PRODUCTION SETTINGS
VIDEO_FPS = 24
OUTPUT_DIR = "output"
ASSETS_DIR = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# 3. THE ELITE MODEL REGISTRY
MODEL_REGISTRY = {
    # Intelligence & Orchestration
    "elite_director": "llama-3.3-70b-versatile",
    
    # Visual Production
    "image_pro": "imagen-4.0-generate-001",
    "image_standard": "gemini-2.5-flash-image",
    "video_pro": "veo-3.1-generate-preview",
    
    # Analysis & Quality Control
    "quality_inspector": "models/gemini-3.1-pro-preview",
    "identity_anchor": "gemini-3.1-flash-lite-preview",
}

# --- UI MAPPINGS (For app.py) ---
IMAGE_MODELS = {
    "Imagen 4.0 (Elite)": MODEL_REGISTRY["image_pro"],
    "Gemini 2.0 (Standard)": MODEL_REGISTRY["image_standard"],
}
DEFAULT_MODEL = "Imagen 4.0 (Elite)"

VIDEO_MODELS = {
    "Veo 3.1 (Cinematic)": MODEL_REGISTRY["video_pro"],
}
DEFAULT_VIDEO_MODEL = "Veo 3.1 (Cinematic)"

# 4. BRAND DNA: CONSULTEASE
# These tokens are injected into every visual prompt for consistency.
BRAND_STYLES = {
    "app": "Authentic Indian corporate professional, sharp business attire, natural skin tones, standard modern Indian office background with glass walls and plants, professional soft office lighting, 8k photorealistic.",
    "professionals": "Realistic Indian professional expert, formal business wear, modern corporate office interior in Bangalore/Mumbai, natural daylight, professional depth of field, sharp focus on face.",
    "default": "Authentic Indian professional looking directly at camera, natural office setting, no holograms, no futuristic lights, photorealistic, cinematic shot on 35mm lens."
}

# 5. VOICE & NARRATION
DEFAULT_VOICE_LANGUAGE = "Hindi (India)"
DEFAULT_VOICE_GENDER = "Female"

VOICE_LANGUAGES = {
    "Hindi (India)": {"lang": "Hindi", "male": "hi-IN-MadhurNeural", "female": "hi-IN-SwaraNeural"},
    "English (US)": {"lang": "English", "male": "en-US-AndrewNeural", "female": "en-US-AvaNeural"},
}

# Mapping Post Type to specific voice vibes (using Edge-TTS voices)
STRATEGIC_VOICES = {
    "Authority": "hi-IN-MadhurNeural",
    "Relatable": "hi-IN-SwaraNeural",
    "Hook": "hi-IN-SwaraNeural",
    "Scenario": "hi-IN-MadhurNeural"
}

# 6. RESOLUTION & RATIOS
ASPECT_RATIOS = {
    "Phone / Reels (9:16)": {"ratio": "9:16", "width": 576, "height": 1024},
    "YouTube (16:9)": {"ratio": "16:9", "width": 1024, "height": 576},
}
DEFAULT_ASPECT_RATIO = "Phone / Reels (9:16)"

# 7. COST CALCULATOR (USD)
COSTS = {
    "image": {"imagen": 0.030, "gemini": 0.005, "default": 0.010},
    "video_per_sec": {"veo": 0.10, "default": 0.05},
    "llm_per_1k": {"gemini": 0.0001, "groq": 0.0}
}

# 8. METADATA OPTIONS
STRATEGIC_CONFIGS = {
    "categories": [
        "Income Tax", "Tenant / Landlord", "Professional Growth", 
        "Employment Disputes", "Online Fraud", "GST", 
        "Domestic Violence", "Property"
    ],
    "post_types": ["Hook", "Relatable", "Authority", "Scenario"],
    "hook_types": ["Pain", "Contrarian", "Benefit", "Curiosity"]
}

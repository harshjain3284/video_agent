import os
import time
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import InferenceClient
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR, HF_API_TOKEN, IMAGE_MODELS, DEFAULT_MODEL
from src.utils.image_utils import get_pollinations_image

def generate_scene_image(scene, token, model_id, session_id, width, height):
    """Orchestrates multi-model generation with a stable fallback sequence."""
    scene_id = scene.get("id", "??")
    print(f"🎬 Producing Visual: Scene {scene_id} ({width}x{height})")
    
    # Priority List: 1. User Choice, 2. SDXL, 3. OpenJourney, 4. Pollinations (Final Boss)
    fallbacks = [model_id, "stabilityai/stable-diffusion-xl-base-1.0", "prompthero/openjourney"]
    
    # Attempt Primary & secondary fallbacks
    # If the user selected 'pollinations', we skip the HF attempts first
    if model_id != "pollinations":
        for mid in fallbacks:
            try:
                client = InferenceClient(model=mid, token=token)
                image = client.text_to_image(scene.get("visual_prompt", "cinematic"), width=width, height=height)
                path = os.path.join(ASSETS_DIR, session_id, f"scene_{scene_id}.png")
                image.save(path)
                scene["image_path"] = path
                return scene
            except Exception as e:
                print(f"   ⚠️ {mid} failed: {str(e)[:50]}")
                time.sleep(1)

    # FINAL BOSS: Pollinations.ai (No Token Required, High Stability)
    print(f"   🚀 Final Fallback: Pollinations.ai (Unlimited Access)")
    img = get_pollinations_image(scene.get("visual_prompt", "cinematic"), width, height)
    if img:
        path = os.path.join(ASSETS_DIR, session_id, f"scene_{scene_id}.png")
        img.save(path)
        scene["image_path"] = path

    return scene

def generator_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Generator (Modular)] ---")
    token = HF_API_TOKEN.strip().strip('"').strip("'") if HF_API_TOKEN else None
    
    # Use selected model from state, otherwise fallback to default
    model_id = state.get("model_id") or IMAGE_MODELS.get(DEFAULT_MODEL, "stabilityai/stable-diffusion-xl-base-1.0")
    width, height = state.get("resolution", (1024, 1024))
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        state["scenes"] = list(executor.map(lambda s: generate_scene_image(s, token, model_id, state["session_id"], width, height), state["scenes"]))
    
    return state

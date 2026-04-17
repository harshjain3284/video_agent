import os
import time
from concurrent.futures import ThreadPoolExecutor
from huggingface_hub import InferenceClient
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR, HF_API_TOKEN, IMAGE_MODELS, DEFAULT_MODEL

def generate_scene_image(scene, token, model_id, session_id):
    """Helper to generate a single scene image with fallback logic."""
    print(f"🎨 Artist: Starting Scene {scene['id']}...")
    fallbacks = [model_id, "runwayml/stable-diffusion-v1-5", "CompVis/stable-diffusion-v1-4"]
    
    for mid in fallbacks:
        try:
            client = InferenceClient(model=mid, token=token)
            image = client.text_to_image(scene["visual_prompt"])
            path = os.path.join(ASSETS_DIR, session_id, f"scene_{scene['id']}.png")
            image.save(path)
            scene["image_path"] = path
            print(f"✅ Scene {scene['id']} complete (via {mid})")
            return scene
        except Exception as e:
            print(f"❌ Scene {scene['id']} failed on {mid}: {str(e)[:50]}")
            if "503" in str(e):
                time.sleep(10) # Simple backoff
    return scene

def generator_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Parallel Scene Visuals] ---")
    token = HF_API_TOKEN.strip().strip('"').strip("'") if HF_API_TOKEN else None
    model_id = IMAGE_MODELS.get(DEFAULT_MODEL, "runwayml/stable-diffusion-v1-5")
    
    with ThreadPoolExecutor() as executor:
        # Launch generation for ALL scenes at once
        results = list(executor.map(lambda s: generate_scene_image(s, token, model_id, state["session_id"]), state["scenes"]))
    
    state["scenes"] = results
    return state

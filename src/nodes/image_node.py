import os
import time
import random
import traceback
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, COSTS, BRAND_STYLES
from src.prompts import DEFAULT_IMAGE_PROMPT, IMAGE_PROMPT_PREFIX
from src.utils.core_utils import format_aspect_ratio, ensure_session_dir, retry_with_backoff

def generate_image_asset(scene: dict, api_key: str, model_id: str, session_id: str, global_aspect_ratio: str, audit_log: list):
    """Generates an image for a scene with Full Developer Trace logging."""
    if not api_key: return None
    scene_id = scene.get("id", "unknown")
    output_dir = ensure_session_dir(session_id)
    path = os.path.join(output_dir, f"scene_{scene_id}.png")
    
    # --- IDEMPOTENCY CHECK ---
    if os.path.exists(path) and os.path.getsize(path) > 0:
        scene.update({"image_path": path})
        return scene

    visual_content = scene.get("prompt") or scene.get("visual_prompt") or DEFAULT_IMAGE_PROMPT
    prefix = IMAGE_PROMPT_PREFIX.replace("{ASPECT_RATIO}", global_aspect_ratio)
    prompt = prefix + visual_content
    ratio_imagen = format_aspect_ratio(global_aspect_ratio, "imagen")

    client = genai.Client(api_key=api_key)
    
    def _call_api():
        if "gemini" in model_id.lower():
            response = client.models.generate_content(
                model=model_id, 
                contents=prompt,
                config=genai_types.GenerateContentConfig(response_modalities=['IMAGE'])
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    with open(path, "wb") as f: f.write(part.inline_data.data)
                    scene.update({"image_path": path, "image_model": f"Google {model_id}", "image_cost": COSTS["image"].get("gemini", 0.01)})
                    audit_log.append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "node": f"Image Gen: Scene {scene_id}",
                        "status": "Success",
                        "model": model_id,
                        "details": f"Generated: {path}"
                    })
                    return scene
        else:
            response = client.models.generate_images(
                model=model_id, 
                prompt=prompt,
                config=genai_types.GenerateImagesConfig(
                    number_of_images=1, 
                    aspect_ratio=ratio_imagen,
                    person_generation="allow_adult"
                ),
            )
            if response.generated_images:
                with open(path, "wb") as f: f.write(response.generated_images[0].image.image_bytes)
                scene.update({"image_path": path, "image_model": f"Google {model_id}", "image_cost": COSTS["image"].get("imagen", 0.03)})
                audit_log.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "node": f"Image Gen: Scene {scene_id}",
                    "status": "Success",
                    "model": model_id,
                    "details": f"Generated: {path}"
                })
                return scene
        return None

    try:
        return retry_with_backoff(_call_api, retries=2)
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ [DEVELOPER ERROR] Image Gen Scene {scene_id}:\n{error_trace}")
        audit_log.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "node": f"Image Gen: Scene {scene_id}",
            "status": "Failed (Dev Trace)",
            "model": model_id,
            "details": str(e),
            "trace": error_trace
        })
        return None

def image_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Image Generator (Dev Audit Mode)] ---")
    if "audit_log" not in state: state["audit_log"] = []
    session_id = state["session_id"]
    api_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    model_id = state.get("model_id") or "gemini-3.1-flash-image-preview"
    global_aspect_ratio = state.get("aspect_ratio", "16:9")
    uploaded_image_path = state.get("uploaded_image_path")
    
    scenes = state.get("scenes", [])
    results = []
    for i, s in enumerate(scenes):
        if i == 0 and uploaded_image_path and os.path.exists(uploaded_image_path):
            s.update({"image_path": uploaded_image_path, "image_model": "User Uploaded"})
            results.append(s)
        else:
            res = generate_image_asset(s, api_key, model_id, session_id, global_aspect_ratio, state["audit_log"])
            results.append(res if res else s)
            time.sleep(1.2)
    state["scenes"] = results
    return state
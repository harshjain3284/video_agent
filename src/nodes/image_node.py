import os
import time
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, COSTS, BRAND_STYLES
from src.prompts import DEFAULT_IMAGE_PROMPT, IMAGE_PROMPT_PREFIX
from src.utils.core_utils import format_aspect_ratio, ensure_session_dir

def generate_image_asset(scene: dict, api_key: str, model_id: str, session_id: str, global_aspect_ratio: str, retries=2):
    if not api_key: return None
    scene_id = scene.get("id", "unknown")
    visual_content = scene.get("prompt") or scene.get("visual_prompt") or DEFAULT_IMAGE_PROMPT
    prefix = IMAGE_PROMPT_PREFIX.replace("{ASPECT_RATIO}", global_aspect_ratio)
    prompt = prefix + visual_content
    ratio_imagen = format_aspect_ratio(global_aspect_ratio, "imagen")
    output_dir = ensure_session_dir(session_id)
    path = os.path.join(output_dir, f"scene_{scene_id}.png")

    client = genai.Client(api_key=api_key)
    
    for i in range(retries + 1):
        try:
            if "gemini" in model_id.lower():
                response = client.models.generate_content(
                    model=model_id, contents=prompt,
                    config=genai_types.GenerateContentConfig(response_modalities=['IMAGE'])
                )
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        with open(path, "wb") as f: f.write(part.inline_data.data)
                        scene.update({"image_path": path, "image_model": f"Google {model_id}", "image_cost": COSTS["image"].get("gemini", 0.01)})
                        return scene
            else:
                response = client.models.generate_images(
                    model=model_id, prompt=prompt,
                    config=genai_types.GenerateImagesConfig(number_of_images=1, aspect_ratio=ratio_imagen),
                )
                if response.generated_images:
                    with open(path, "wb") as f: f.write(response.generated_images[0].image.image_bytes)
                    scene.update({"image_path": path, "image_model": f"Google {model_id}", "image_cost": COSTS["image"].get("imagen", 0.03)})
                    return scene
        except Exception as e:
            if "503" in str(e) and i < retries:
                print(f"   ⚠️ Scene {scene_id}: Gemini Busy (503). Retrying in 3s...")
                time.sleep(3)
                continue
            print(f"   ❌ Scene {scene_id} Error: {str(e)[:100]}")
            break
    return None

def image_node(state: AgentState) -> AgentState:
    print("--- [Node: Image Generator] ---")
    session_id = state["session_id"]
    api_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    model_id = state.get("model_id") or "gemini-2.5-flash-image"
    global_aspect_ratio = state.get("aspect_ratio", "16:9")
    uploaded_image_path = state.get("uploaded_image_path")
    
    brand_key = state.get("brand_page", "default")
    brand_style = BRAND_STYLES.get(brand_key, BRAND_STYLES["default"])
    for s in state.get("scenes", []):
        if "visual_prompt" in s and brand_style[:15].lower() not in s["visual_prompt"].lower():
            s["visual_prompt"] = f"{s['visual_prompt']}. Style: {brand_style}"

    from concurrent.futures import ThreadPoolExecutor
    print(f"   🖼️  Generating {len(state.get('scenes', []))} images in parallel (max 2)...")
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        for i, s in enumerate(state.get("scenes", [])):
            if i == 0 and uploaded_image_path and os.path.exists(uploaded_image_path):
                s.update({"image_path": uploaded_image_path, "image_model": "User Uploaded"})
                futures.append((i, None, s))
            else:
                f = executor.submit(generate_image_asset, s, api_key, model_id, session_id, global_aspect_ratio)
                futures.append((i, f, s))
        
        results = [None] * len(futures)
        for idx, f, original_s in futures:
            if f:
                res = f.result()
                results[idx] = res if res else original_s
            else:
                results[idx] = original_s
        
        state["scenes"] = results

    return state
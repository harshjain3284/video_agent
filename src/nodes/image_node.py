import os
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, COSTS
from src.utils.core_utils import format_aspect_ratio, ensure_session_dir

def generate_image_asset(scene: dict, api_key: str, model_id: str, session_id: str, global_aspect_ratio: str):
    if not api_key:
        print("❌ Gemini API Key missing.")
        return None

    scene_id = scene.get("id", "unknown")
    # Strong prompt reinforcement at the start
    prompt = f"[Target Aspect Ratio: {global_aspect_ratio}] " + (scene.get("prompt") or scene.get("visual_prompt") or "High quality cinematic scene.")
    
    # 1. Standardize aspect ratio format
    ratio_gemini = format_aspect_ratio(global_aspect_ratio, "gemini")
    ratio_imagen = format_aspect_ratio(global_aspect_ratio, "imagen")
    
    output_dir = ensure_session_dir(session_id)
    path = os.path.join(output_dir, f"scene_{scene_id}.png")

    try:
        client = genai.Client(api_key=api_key)
        
        # ─── BRANCH A: Gemini Native Image (gemini-2.5, Nano Banana, etc.) ───
        if "gemini" in model_id.lower():
            print(f"🌟 [Gemini Mode] Scene {scene_id}: model={model_id}")
            response = client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_modalities=['IMAGE']
                )
            )
            # Safe extraction of image bytes
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    with open(path, "wb") as f:
                        f.write(part.inline_data.data)
                    scene["image_path"] = path
                    scene["image_model"] = f"Google {model_id}"
                    
                    # Track Cost
                    price = COSTS["image"].get("gemini", 0.01)
                    scene["image_cost"] = price
                    return scene

        # ─── BRANCH B: Imagen Specialized (imagen-3.0, imagen-4.0) ───────────
        else:
            print(f"🌟 [Imagen Mode] Scene {scene_id}: model={model_id}, ratio={ratio_imagen}")
            response = client.models.generate_images(
                model=model_id,
                prompt=prompt,
                config=genai_types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=ratio_imagen
                ),
            )
            if response.generated_images:
                img_bytes = response.generated_images[0].image.image_bytes
                with open(path, "wb") as f:
                    f.write(img_bytes)
                
                scene["image_path"] = path
                scene["image_model"] = f"Google {model_id}"
                
                # Track Cost
                price = COSTS["image"].get("imagen", 0.03)
                scene["image_cost"] = price
                return scene

    except Exception as e:
        print(f"❌ Scene {scene_id}: Tool Execution Error -> {str(e)[:150]}")
        return None

def image_node(state: AgentState) -> AgentState:
    print("--- [Node: Image Generator (Asset Creation)] ---")
    session_id = state["session_id"]
    api_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    model_id = state.get("model_id") or "gemini-2.5-flash-image"
    global_aspect_ratio = state.get("aspect_ratio", "16:9")
    uploaded_image_path = state.get("uploaded_image_path")

    new_scenes = []
    for i, s in enumerate(state.get("scenes", [])):
        # Skip generation if user provided an image
        if i == 0 and uploaded_image_path and os.path.exists(uploaded_image_path):
            print(f"   📂 [Image Provided] Using uploaded file for Scene {s.get('id', i)}...")
            s["image_path"] = uploaded_image_path
            s["image_model"] = "User Uploaded"
            new_scenes.append(s)
            continue
            
        res = generate_image_asset(s, api_key, model_id, session_id, global_aspect_ratio)
        if res:
            new_scenes.append(res)
        else:
            new_scenes.append(s)

    state["scenes"] = new_scenes
    return state
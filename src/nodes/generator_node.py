import os
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR, GEMINI_API_KEY, format_aspect_ratio

# --- MCP Tool Definition: native_image_gen ---
# Schema:
# - prompt: str (required)
# - aspect_ratio: str ["16-9", "9-16", "1-1"]
# - path: str (output path)

def generate_image_asset(scene: dict, api_key: str, model_id: str, session_id: str, global_aspect_ratio: str):
    """
    MCP-Compliant Tool for Google Imagen / Gemini Image Generation.
    Eliminates scope errors and config mismatches.
    """
    if not api_key:
        print("   ❌ MCP Error: Gemini API Key missing.")
        return None

    prompt = scene.get("visual_prompt")
    scene_id = scene.get("id", "??")
    path = os.path.join(ASSETS_DIR, session_id, f"scene_{scene_id}.png")

    try:
        client = genai.Client(api_key=api_key)
        
        # 1. MCP Standard: Input Normalization
        # Use our centralized config formatter
        ratio = format_aspect_ratio(global_aspect_ratio, target_model_type="gemini")
        
        # ─── Tool Branch A: Gemini Native Image (Nano Banana) ──────────
        if "gemini" in model_id.lower():
            print(f"   🌟 [MCP Tool: Gemini Image] Scene {scene_id} ({ratio})...")
            response = client.models.generate_content(
                model=model_id,
                contents=prompt,
                config={
                    'response_modalities': ['IMAGE']
                }
            )
            # Safe extraction
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    with open(path, "wb") as f:
                        f.write(part.inline_data.data)
                    scene["image_path"] = path
                    scene["image_model"] = f"Google {model_id}"
                    scene["aspect_ratio"] = ratio
                    return scene

        # ─── Tool Branch B: Imagen 3/4 ─────────────────────────────
        else:
            print(f"   🌟 [MCP Tool: Imagen] Scene {scene_id} ({ratio})...")
            response = client.models.generate_images(
                model=model_id,
                prompt=prompt,
                config=genai_types.GenerateImagesConfig(
                    number_of_images=1,
                    aspect_ratio=ratio.replace("-", ":"), # Imagen prefers colon
                    include_rai_reasoning=True,
                )
            )
            if response.generated_images:
                img_bytes = response.generated_images[0].image.image_bytes
                with open(path, "wb") as f:
                    f.write(img_bytes)
                scene["image_path"] = path
                scene["image_model"] = f"Google {model_id}"
                scene["aspect_ratio"] = ratio
                return scene

    except Exception as e:
        print(f"   ❌ [MCP Tool: Image] Error: {str(e)[:150]}")
    
    return None

def generator_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Generator (MCP Compliant)] ---")
    session_id = state["session_id"]
    api_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    model_id = state.get("model_id")
    global_aspect_ratio = state.get("aspect_ratio", "16:9")
    uploaded_image_path = state.get("uploaded_image_path")

    # Map scenes with correct parameters to avoid scope errors
    new_scenes = []
    for i, s in enumerate(state["scenes"]):
        # NEW: Skip generation if user provided an image for the first scene
        if i == 0 and uploaded_image_path and os.path.exists(uploaded_image_path):
            print(f"   📂 [MCP Tool: Image] Using uploaded reference for Scene {s.get('id')}...")
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

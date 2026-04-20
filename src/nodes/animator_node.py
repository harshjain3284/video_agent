import os
import time
import shutil
from concurrent.futures import ThreadPoolExecutor
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR, GEMINI_API_KEY, format_aspect_ratio

# --- MCP Tool Definition: generate_veo_video ---
# Schema: 
# - image_path: str (required)
# - prompt: str (required)
# - duration: int [5, 10]
# - aspect_ratio: str ["16:9", "9:16", "1:1"]

def generate_veo_video(scene: dict, api_key: str, model_id: str, session_id: str, aspect_ratio: str):
    """
    MCP-Compliant Tool for Google Veo Motion Generation.
    Includes strict validation to prevent 400 errors.
    """
    if not api_key:
        print("   ❌ MCP Error: API Key missing.")
        return None
    
    # 1. Resource Validation
    image_path = scene.get("image_path")
    scene_id = scene.get("id", "??")
    output_path = os.path.join(ASSETS_DIR, session_id, f"ai_motion_{scene_id}.mp4")

    if not image_path or not os.path.exists(image_path):
        print(f"   ❌ MCP Error: Resource not found at {image_path}")
        return None

    try:
        client = genai.Client(api_key=api_key)
        actual_model = model_id if model_id else "veo-3.1-generate-preview"
        
        # 2. Strict Input Normalization (The MCP Way)
        ratio = format_aspect_ratio(aspect_ratio, target_model_type="veo")
        mcp_duration = 5 # Force 5s for preview stability
        
        print(f"   🎬 [MCP Tool: Veo] Executing for Scene {scene_id} ({ratio}, {mcp_duration}s)...")
        
        # 3. Execution (With Auto-Retry for strict duration bounds)
        veo_image = genai_types.Image.from_file(location=image_path)
        
        try:
            operation = client.models.generate_videos(
                model=actual_model,
                prompt=scene.get("motion_prompt", "high quality cinematic motion"),
                image=veo_image,
                config={
                    "durationSeconds": 5, # Explicitly 5
                    "aspectRatio": ratio,
                },
            )
        except Exception as e:
            msg = str(e).lower()
            if "bound" in msg or "parameter" in msg:
                 print(f"   ⚠️ MCP Warning: Defaulting to auto-config...")
                 operation = client.models.generate_videos(
                    model=actual_model,
                    prompt=scene.get("motion_prompt", "high quality cinematic motion"),
                    image=veo_image,
                )
            else:
                raise e
                raise e
        
        # Polling
        for i in range(30):
            if operation.done:
                break
            time.sleep(10)
            operation = client.operations.get(operation)
        
        if operation.done and operation.response and operation.response.generated_videos:
            video_obj = operation.response.generated_videos[0].video
            if video_obj.video_bytes:
                with open(output_path, "wb") as f:
                    f.write(video_obj.video_bytes)
            elif video_obj.uri:
                import urllib.request
                urllib.request.urlretrieve(video_obj.uri, output_path)
            
            scene["video_path"] = output_path
            scene["motion_model"] = f"Google {actual_model}"
            print(f"   ✅ [MCP Tool: Veo] Success: {output_path}")
            return scene
        
    except Exception as e:
        print(f"   ❌ [MCP Tool: Veo] Runtime Error: {str(e)[:150]}")
    
    return None

def animate_single_scene(scene: dict, session_id: str, gemini_key: str, video_model_id: str, aspect_ratio: str) -> dict:
    """Orchestrates motion generation with fallbacks."""
    # Try Google First
    result = generate_veo_video(scene, gemini_key, video_model_id, session_id, aspect_ratio)
    if result:
        return result
        
    # Fallback logic remained but kept simple for stability
    scene["motion_model"] = "Cinematic Zoom (Fallback)"
    scene["video_path"] = None 
    return scene

def animator_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Animator (MCP Compliant)] ---")
    session_id = state["session_id"]
    gemini_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    video_model_id = state.get("video_model_id")
    aspect_ratio = state.get("aspect_ratio", "16:9")

    # Use thread pool for parallel generation
    with ThreadPoolExecutor(max_workers=2) as executor:
        state["scenes"] = list(executor.map(
            lambda s: animate_single_scene(s, session_id, gemini_key, video_model_id, aspect_ratio), 
            state["scenes"]
        ))

    return state

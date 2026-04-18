import os
import time
import shutil
from concurrent.futures import ThreadPoolExecutor
from gradio_client import Client, handle_file
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR, HF_API_TOKEN

def animate_single_scene(scene: dict, session_id: str) -> dict:
    """Helper to animate a single scene with Authenticated Rotation through multiple Free Spaces."""
    image_path = scene.get("image_path")
    scene_id = scene.get("id", "unknown")
    
    if not image_path or not os.path.exists(image_path):
        return scene

    output_path = os.path.join(ASSETS_DIR, session_id, f"ai_motion_{scene_id}.mp4")
    token = HF_API_TOKEN.strip().strip('"').strip("'") if HF_API_TOKEN else None
    
    # MANUALLY VERIFIED IDs (Hugging Face Spaces 2026):
    spaces = [
        "Wan-AI/Wan2.1",                      # #1 Official Wan
        "Lightricks/LTX-2-3",                 # #2 Active LTX Engine
        "zai-org/CogVideoX-5B-Space",         # #3 Stable CogVideo
        "multimodalart/stable-video-diffusion",# #4 Stable SVD
        "Chunchunmaru95/Wan-AI-Wan2.1-I2V-14B-480P" # #5 Fast Wan Mirror
    ]





    
    print(f"🎬 Generating High-Quality AI Motion for Scene {scene_id}...")
    
    for space_id in spaces:
        try:
            print(f"   🚀 Authenticating with {space_id}...")
            client = Client(space_id, token=token)
            
            # WAN2.2 / HUNYUAN STYLE (New High Quality)
            if "Wan" in space_id or "Hunyuan" in space_id:
                result = client.predict(
                    input_video=None, 
                    input_image=handle_file(image_path),
                    prompt=scene.get("motion_prompt", "cinematic motion, high quality"),
                    api_name="/predict"
                )
            # SVD STYLE (Stable Fallback)
            else:
                result = client.predict(
                    image=handle_file(image_path),
                    seed=0,
                    randomize_seed=True,
                    motion_bucket_id=180, # Increased for more motion
                    fps_id=25,            # Increased to 25FPS for smoothness
                    api_name="/video"
                )

            
            if video_temp_path and isinstance(video_temp_path, str) and os.path.exists(video_temp_path):
                shutil.copy(video_temp_path, output_path)
                scene["video_path"] = output_path
                scene["motion_model"] = space_id # RECORD SUCCESSFUL SPACE
                print(f"✅ SUCCESS on {space_id} for Scene {scene_id}")
                return scene
            
        except Exception as e:
            msg = str(e)
            if "quota" in msg.lower():
                print(f"   ⚠️ {space_id} is OUT OF QUOTA. Shifting...")
                continue
            elif "401" in msg or "404" in msg:
                print(f"   ⚠️ {space_id} is unavailable or private. Shifting...")
                continue
            else:
                print(f"   ❌ {space_id} Error: {msg[:100]}...")
                continue

    print(f"⚠️ All video spaces exhausted for Scene {scene_id}. Using fallback.")
    scene["motion_model"] = "Cinematic Zoom (Local)" # RECORD FALLBACK
    scene["video_path"] = None 
    return scene




def animator_node(state: AgentState) -> AgentState:
    """Uses Public HF Spaces (Gradio) to turn static images into real moving videos."""
    print(f"--- [Node: Animator (Free AI Video via Gradio)] ---")
    
    session_id = state["session_id"]

    # Parallelize to avoid long wait times
    # Note: If hit with Space queues, this might still take some time
    with ThreadPoolExecutor(max_workers=2) as executor:
        list(executor.map(lambda s: animate_single_scene(s, session_id), state["scenes"]))

    return state



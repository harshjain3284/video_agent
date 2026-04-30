import os
import time
import traceback
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, COSTS, MODEL_REGISTRY
from src.utils.core_utils import ensure_session_dir, format_aspect_ratio, retry_with_backoff
from src.utils.veo_utils import (
    normalize_veo_aspect_ratio,
    wait_for_veo_operation,
    download_veo_video
)

def _prepare_veo_prompt(scene: dict, ratio: str) -> str:
    """Refines the motion prompt with layout hints for professional framing."""
    raw_motion = scene.get("motion_prompt", "Professional cinematic motion.")
    hint = "Cinematic vertical composition, optimized for mobile viewing. " if "9:16" in ratio else ""
    return f"{hint}{raw_motion}".strip()

def _generate_single_veo_clip(scene: dict, api_key: str, model_id: str, session_id: str, aspect_ratio: str) -> str:
    """Executes a single Veo generation with robust waiting and downloading."""
    scene_id = scene.get("id", "temp")
    output_dir = ensure_session_dir(session_id)
    output_path = os.path.join(output_dir, f"ai_motion_{scene_id}.mp4")

    # 1. Configuration
    ratio = normalize_veo_aspect_ratio(format_aspect_ratio(aspect_ratio, "veo"))
    duration = int(float(scene.get("duration", 4)))
    if duration not in [4, 6, 8]: # Clamp to official Veo durations
        duration = 4 if duration < 5 else (6 if duration < 7 else 8)
    
    prompt = _prepare_veo_prompt(scene, ratio)
    client = genai.Client(api_key=api_key)

    def _veo_call():
        image = genai_types.Image.from_file(location=scene.get("image_path"))
        operation = client.models.generate_videos(
            model=model_id, prompt=prompt, image=image,
            config=genai_types.GenerateVideosConfig(
                number_of_videos=1, duration_seconds=duration,
                aspect_ratio=ratio, person_generation="allow_adult"
            )
        )
        # Wait for the cloud to finish processing (up to 8 mins)
        operation = wait_for_veo_operation(client, operation, timeout_mins=8)
        if operation.done and download_veo_video(client, operation, output_path):
            return output_path
        return None

    return retry_with_backoff(_veo_call, retries=2)

def video_node(state: AgentState) -> AgentState:
    """
    ELITE VIDEO GENERATOR
    Converts static Expert images into cinematic talking-head clips using Google Veo.
    """
    print(f"--- [Node: Video Generator (Modular)] ---")
    api_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    if not api_key: return state

    model_id = state.get("video_model_id", MODEL_REGISTRY["video_pro"])
    aspect_ratio = state.get("aspect_ratio", "9:16")
    
    results = []
    for scene in state.get("scenes", []):
        scene_id = scene.get("id", "temp")
        
        # Idempotency: Skip if already generated
        if scene.get("video_path") and os.path.exists(scene["video_path"]):
            results.append(scene)
            continue

        print(f"   [Veo] Animating Scene {scene_id}...")
        try:
            video_path = _generate_single_veo_clip(scene, api_key, model_id, state["session_id"], aspect_ratio)
            if video_path:
                scene["video_path"] = video_path
                
                # Calculate Cost
                duration = float(scene.get("duration", 4.0))
                scene["video_cost"] = COSTS["video_per_sec"].get("veo", 0.10) * duration
                
                # LOG SUCCESS
                state["audit_log"].append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "node": f"Video Gen: Scene {scene_id}",
                    "status": "Success",
                    "model": model_id,
                    "details": f"Veo Clip Ready: {os.path.basename(video_path)}"
                })
                print(f"      [OK] Video ready: {os.path.basename(video_path)}")
        except Exception as e:
            import traceback
            print(f"   [CRITICAL DIAGNOSTIC] Video Gen failed for Scene {scene_id}!")
            traceback.print_exc()
            scene["video_path"] = None

        results.append(scene)
        time.sleep(5) # API cooling

    state["scenes"] = results
    return state
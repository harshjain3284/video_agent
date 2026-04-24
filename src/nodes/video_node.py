import os
import time
import traceback
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, COSTS
from src.utils.core_utils import ensure_session_dir, format_aspect_ratio, retry_with_backoff
from src.prompts import DEFAULT_MOTION_PROMPT
from src.utils.veo_utils import (
    normalize_veo_aspect_ratio,
    normalize_veo_duration,
    wait_for_veo_operation,
    download_veo_video
)

def _get_scene_prompt(scene: dict, ratio: str) -> str:
    """Combines motion analysis with structural hints for the specific aspect ratio."""
    raw_prompt = scene.get("prompt") or scene.get("motion_prompt") or DEFAULT_MOTION_PROMPT
    layout_hint = ""
    if "9:16" in ratio:
        layout_hint = "Cinematic vertical composition, optimized for mobile viewing, professional head and shoulders framing. "
    elif "16:9" in ratio:
        layout_hint = "Cinematic widescreen composition, professional landscape framing. "
    return f"{layout_hint}{str(raw_prompt).strip()}"

def generate_veo_video(
    scene: dict,
    api_key: str,
    model_id: str | None,
    session_id: str,
    aspect_ratio: str,
    audit_log: list
) -> dict | None:
    """Generates an AI Video chunk with high-resiliency settings and developer tracing."""
    scene_id = scene.get("id", "unknown")
    image_path = scene.get("image_path")
    if not api_key or not image_path or not os.path.exists(image_path): return None

    output_dir = ensure_session_dir(session_id)
    output_path = os.path.join(output_dir, f"ai_motion_{scene_id}.mp4")

    # --- IDEMPOTENCY CHECK ---
    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        scene.update({"video_path": output_path})
        return scene

    clean_ratio = format_aspect_ratio(aspect_ratio, "veo")
    ratio = normalize_veo_aspect_ratio(clean_ratio)
    duration = int(float(scene.get("duration", 4)))
    if duration not in [4, 6, 8]:
        duration = 4 if duration < 5 else (6 if duration < 7 else 8)
    
    prompt = _get_scene_prompt(scene, ratio)
    actual_model = model_id or "veo-3.1-generate-preview"

    def _call_veo():
        client = genai.Client(api_key=api_key)
        image = genai_types.Image.from_file(location=image_path)
        operation = client.models.generate_videos(
            model=actual_model,
            prompt=prompt,
            image=image,
            config=genai_types.GenerateVideosConfig(
                number_of_videos=1,
                duration_seconds=duration,
                aspect_ratio=ratio,
                person_generation="allow_adult",
            ),
        )
        operation = wait_for_veo_operation(client, operation, timeout_mins=8)
        if not operation.done: 
            raise TimeoutError(f"Veo server timed out after 8 minutes for Scene {scene_id}")

        if download_veo_video(client, operation, output_path):
            scene.update({
                "video_path": output_path,
                "motion_model": f"Google {actual_model}",
                "veo_duration": duration,
                "veo_aspect_ratio": ratio,
                "video_cost": COSTS["video_per_sec"].get("veo", 0.10) * duration
            })
            audit_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "node": f"Video Gen: Scene {scene_id}",
                "status": "Success",
                "model": actual_model,
                "details": f"Vertical ({ratio}) | {duration}s"
            })
            return scene
        raise ValueError("Video generated but download failed.")

    try:
        return retry_with_backoff(_call_veo, retries=3, initial_delay=10)
    except Exception as e:
        trace = traceback.format_exc()
        print(f"❌ [DEV ERROR] Video Gen Scene {scene_id}:\n{trace}")
        audit_log.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "node": f"Video Gen: Scene {scene_id}",
            "status": "Failed (Dev Trace)",
            "model": actual_model,
            "details": str(e),
            "trace": trace
        })
        scene["video_path"] = None
        return scene

def video_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Video Generator (Dev Audit Mode)] ---")
    if "audit_log" not in state: state["audit_log"] = []
    session_id = state["session_id"]
    gemini_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    video_model_id = state.get("video_model_id") or "veo-3.1-generate-preview"
    aspect_ratio = state.get("aspect_ratio", "16:9")

    scenes = state.get("scenes", [])
    results = []
    for s in scenes:
        scene_id = s.get("id", "unknown")
        print(f"   🎥 [Veo] Generating AI Video Motion for Scene {scene_id}...")
        res = generate_veo_video(s, gemini_key or "", video_model_id, session_id, aspect_ratio, state["audit_log"])
        if res and res.get("video_path"):
            print(f"      ✅ Video Segment Ready: {os.path.basename(res['video_path'])}")
        results.append(res if res else s)
        time.sleep(5.0) # Standard Cooling

    state["scenes"] = results
    return state
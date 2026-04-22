import os
import time
from concurrent.futures import ThreadPoolExecutor
from google import genai
from google.genai import types as genai_types

from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, COSTS
from src.utils.core_utils import ensure_session_dir, format_aspect_ratio
from src.prompts import DEFAULT_MOTION_PROMPT


from src.utils.veo_utils import (
    normalize_veo_aspect_ratio,
    normalize_veo_duration,
    wait_for_veo_operation,
    download_veo_video
)


def _get_scene_prompt(scene: dict) -> str:
    prompt = scene.get("prompt") or scene.get("motion_prompt")
    return str(prompt).strip() if prompt and str(prompt).strip() else DEFAULT_MOTION_PROMPT


def generate_veo_video(
    scene: dict,
    api_key: str,
    model_id: str | None,
    session_id: str,
    aspect_ratio: str,
) -> dict | None:
    scene_id = scene.get("id", "unknown")
    image_path = scene.get("image_path")

    if not api_key or not image_path or not os.path.exists(image_path):
        print(f"❌ Scene {scene_id}: Missing API Key or Image.")
        return None

    output_dir = ensure_session_dir(session_id)
    output_path = os.path.join(output_dir, f"ai_motion_{scene_id}.mp4")

    # Clean the ratio name (e.g., "Phone/Reels (9:16)" -> "9:16")
    clean_ratio = format_aspect_ratio(aspect_ratio, "veo")
    ratio = normalize_veo_aspect_ratio(clean_ratio)
    
    # DYNAMIC DURATION: Select the smallest Veo block that fits the target
    target_dur = float(scene.get("duration", 4))
    if target_dur <= 4: duration = 4
    elif target_dur <= 6: duration = 6
    else: duration = 8
    
    prompt = _get_scene_prompt(scene)
    actual_model = model_id or "veo-3.1-generate-preview"

    try:
        client = genai.Client(api_key=api_key)
        image = genai_types.Image.from_file(location=image_path)

        print(f"🎬 Scene {scene_id}: model={actual_model}, ratio={ratio}, duration={duration}s")

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

        # Polling and Downloading moved to Utils
        operation = wait_for_veo_operation(client, operation)
        if not operation.done:
            print(f"❌ Scene {scene_id}: Timeout.")
            return None

        if download_veo_video(client, operation, output_path):
            scene.update({
                "video_path": output_path,
                "motion_model": f"Google {actual_model}",
                "veo_duration": duration,
                "veo_aspect_ratio": ratio,
                "used_prompt": prompt,
                "video_cost": COSTS["video_per_sec"].get("veo", 0.10) * duration
            })
            print(f"✅ Scene {scene_id}: saved -> {output_path}")
            return scene

        return None

    except Exception as e:
        print(f"❌ Scene {scene_id}: Error -> {str(e)[:100]}")
        return None


def animate_single_scene(
    scene: dict,
    session_id: str,
    gemini_key: str | None,
    video_model_id: str | None,
    aspect_ratio: str,
) -> dict:
    """
    Try Veo first, then return fallback metadata if it fails.
    """
    result = generate_veo_video(
        scene=scene,
        api_key=gemini_key or "",
        model_id=video_model_id,
        session_id=session_id,
        aspect_ratio=aspect_ratio,
    )
    if result:
        return result

    scene["motion_model"] = "Cinematic Zoom (Fallback)"
    scene["video_path"] = None
    if "motion_error" not in scene:
        scene["motion_error"] = "Veo generation failed; fallback selected."
    return scene


def video_node(state: AgentState) -> AgentState:
    print("--- [Node: Video Generator (Veo 3.1)] ---")

    session_id = state["session_id"]
    gemini_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    video_model_id = state.get("video_model_id") or "veo-3.1-generate-preview"
    aspect_ratio = state.get("aspect_ratio", "16:9")

    scenes = state.get("scenes", [])
    if not scenes:
        print("⚠️ No scenes found in state.")
        return state

    # ─── CONTROLLED PARALLEL GENERATION (Speed + Safety) ───
    print(f"   🎬 Generating {len(scenes)} videos in parallel (max 2)...")
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(animate_single_scene, s, session_id, gemini_key, video_model_id, aspect_ratio): i for i, s in enumerate(scenes)}
        
        # Collect results in order
        results = [None] * len(scenes)
        for future in futures:
            idx = futures[future]
            results[idx] = future.result()
        
        state["scenes"] = results

    return state
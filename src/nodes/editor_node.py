import os
import math
import uuid
from moviepy import (
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
    AudioFileClip,
)
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR, COSTS
from src.utils.image_utils import draw_subtitles

def _apply_loop(clip, duration):
    """Simple loop for clips that are too short."""
    loops_needed = math.ceil(duration / clip.duration)
    repeated = concatenate_videoclips([clip] * loops_needed)
    return repeated.with_duration(duration)

def editor_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Final Editor (Simplification Mode)] ---")
    session_id = state["session_id"]
    scenes = state.get("scenes", [])
    width, height = state.get("resolution", (1280, 720))
    aspect_ratio = state.get("aspect_ratio", "16:9")
    
    final_clips = []
    total_bill = state.get("total_cost", 0.0)

    for i, scene in enumerate(scenes):
        ai_video_path = scene.get("video_path")
        image_path = scene.get("image_path")
        audio_path = scene.get("audio_path")
        per_scene_dur = float(scene.get("duration", 4))
        
        clip = None
        # 1. VIDEO SOURCE
        if ai_video_path and os.path.exists(ai_video_path):
            try:
                print(f"🎥 Shot {i+1} ({per_scene_dur}s)")
                clip = VideoFileClip(ai_video_path).resized((width, height))
                
                # Direct duration enforcement (Simple & Stable)
                if clip.duration < per_scene_dur:
                    clip = _apply_loop(clip, per_scene_dur)
                else:
                    clip = clip.with_duration(per_scene_dur)
            except Exception as e:
                print(f"   ⚠️ Video Error: {e}")

        # Fallback to Static Image
        if clip is None and image_path and os.path.exists(image_path):
            clip = ImageClip(image_path).with_duration(per_scene_dur).resized((width, height))

        if clip:
            # 2. AUDIO SYNC (Continuous, no silence)
            if audio_path and os.path.exists(audio_path):
                audio = AudioFileClip(audio_path)
                if audio.duration > per_scene_dur:
                    audio = audio.with_duration(per_scene_dur)
                clip = clip.with_audio(audio)
            
            # 3. SUBTITLES
            if state.get("enable_subtitles", True) and scene.get("narration"):
                clip = draw_subtitles(clip, scene["narration"], aspect_ratio)
            
            final_clips.append(clip)
        
        # Aggregate Cost
        total_bill += scene.get("image_cost", 0.0)
        total_bill += scene.get("video_cost", 0.0)

    # 4. FINAL ASYSEMBLY (Hard Cuts only)
    if final_clips:
        final_video = concatenate_videoclips(final_clips, method="compose")
        
        output_filename = f"ai_video_{session_id}.mp4"
        output_path = os.path.join("output", output_filename)
        os.makedirs("output", exist_ok=True)
        
        # Faster preset for Reels
        final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
        state["video_path"] = output_path
        
        # Cleanup
        for c in final_clips: c.close()
    
    state["total_cost"] = round(total_bill, 3)
    return state
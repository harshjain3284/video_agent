import os
import math
import traceback
from datetime import datetime
from moviepy import (
    VideoFileClip,
    concatenate_videoclips,
    AudioFileClip,
)
from src.state.agent_state import AgentState
from src.config import COSTS
from src.utils.image_utils import draw_subtitles

def _apply_loop(clip, duration):
    """Simple loop for clips that are too short."""
    loops_needed = math.ceil(duration / clip.duration)
    repeated = concatenate_videoclips([clip] * loops_needed)
    return repeated.with_duration(duration)

def editor_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Elite Editor (AI-Video Strict Mode & Dev Trace)] ---")
    if "audit_log" not in state: state["audit_log"] = []
    
    session_id = state["session_id"]
    scenes = state.get("scenes", [])
    width, height = state.get("resolution", (1280, 720))
    aspect_ratio = state.get("aspect_ratio", "16:9")
    
    final_clips = []
    total_bill = state.get("total_cost", 0.0)

    for i, scene in enumerate(scenes):
        ai_video_path = scene.get("video_path")
        audio_path = scene.get("audio_path")
        per_scene_dur = float(scene.get("duration", 4))
        
        # 🚨 STRICT RULE: Only include AI-Generated Motion Video.
        if ai_video_path and os.path.exists(ai_video_path):
            try:
                clip = VideoFileClip(ai_video_path).resized((width, height))
                
                if abs(clip.duration - per_scene_dur) > 0.5:
                    if clip.duration < per_scene_dur:
                        clip = _apply_loop(clip, per_scene_dur)
                    else:
                        clip = clip.with_duration(per_scene_dur)
                else:
                    clip = clip.with_duration(clip.duration)
                
                if audio_path and os.path.exists(audio_path):
                    audio = AudioFileClip(audio_path)
                    if audio.duration > per_scene_dur:
                        audio = audio.with_duration(per_scene_dur)
                    clip = clip.with_audio(audio)
                
                if state.get("enable_subtitles", True) and scene.get("narration"):
                    def _sub_renderer(get_frame, t):
                        frame = get_frame(t)
                        return draw_subtitles(frame, scene["narration"], (width, height), aspect_ratio)
                    clip = clip.transform(_sub_renderer, apply_to="video")
                
                final_clips.append(clip)
            except Exception as e:
                trace = traceback.format_exc()
                print(f"❌ [DEV ERROR] Editor Scene {i+1}:\n{trace}")
                state["audit_log"].append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "node": "Editor",
                    "status": "Scene Skipped (Trace)",
                    "model": "MoviePy",
                    "details": f"Failed to load video for Scene {i+1}: {e}",
                    "trace": trace
                })
        else:
            state["audit_log"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "node": "Editor",
                "status": "Scene Purged",
                "model": "Strict Filter",
                "details": f"Scene {i+1} has no AI-Video motion. Removing from final production."
            })

        total_bill += scene.get("image_cost", 0.0)
        total_bill += scene.get("video_cost", 0.0)

    # Final Compilation
    if final_clips:
        try:
            final_video = concatenate_videoclips(final_clips, method="compose")
            output_filename = f"ai_video_{session_id}.mp4"
            output_path = os.path.join("output", output_filename)
            os.makedirs("output", exist_ok=True)
            
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
            state["video_path"] = output_path
            
            for c in final_clips: c.close()
        except Exception as e:
            trace = traceback.format_exc()
            print(f"❌ [DEV ERROR] Final Assembly:\n{trace}")
            state["audit_log"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "node": "Final Assembly",
                "status": "Failed (Trace)",
                "model": "FFmpeg",
                "details": str(e),
                "trace": trace
            })
    
    state["total_cost"] = round(total_bill, 3)
    return state
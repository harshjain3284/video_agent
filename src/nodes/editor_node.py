import os
import math
import traceback
import re
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
    print(f"--- [Node: Elite Editor (Dual-Assembly Mode)] ---")
    if "audit_log" not in state: state["audit_log"] = []
    
    session_id = state["session_id"]
    scenes = state.get("scenes", [])
    width, height = state.get("resolution", (1280, 720))
    aspect_ratio = state.get("aspect_ratio", "16:9")
    os.makedirs("output", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def assemble_version(audio_key, voice_name):
        print(f"   [EDITOR] Assembling Version: {voice_name}...")
        final_clips = []
        for i, scene in enumerate(scenes):
            ai_video_path = scene.get("video_path")
            audio_path = scene.get(audio_key)
            per_scene_dur = float(scene.get("duration", 4))
            
            if ai_video_path and os.path.exists(ai_video_path):
                try:
                    clip = VideoFileClip(ai_video_path).resized((width, height))
                    if clip.duration < per_scene_dur:
                        clip = _apply_loop(clip, per_scene_dur)
                    else:
                        clip = clip.with_duration(per_scene_dur)

                    
                    if audio_path and os.path.exists(audio_path):
                        audio = AudioFileClip(audio_path)
                        if audio.duration > per_scene_dur:
                            audio = audio.with_duration(per_scene_dur)
                        clip = clip.with_audio(audio)
                    
                    if state.get("enable_subtitles", True) and scene.get("narration"):
                        def _sub_renderer(get_frame, t):
                            return draw_subtitles(get_frame(t), scene["narration"], (width, height), aspect_ratio)
                        clip = clip.transform(_sub_renderer, apply_to="video")
                    
                    final_clips.append(clip)
                except Exception as e:
                    print(f"      ⚠️ Failed Scene {i+1} for {voice_name}: {e}")
        
        if final_clips:
            try:
                final_v = concatenate_videoclips(final_clips, method="compose")
                filename = f"video_{voice_name}_{timestamp}.mp4"
                save_path = os.path.join("output", filename)
                final_v.write_videofile(save_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
                print(f"      ✅ Produced: {filename}")
                for c in final_clips: c.close()
                return save_path
            except Exception as e:
                print(f"      ❌ Assembly Failed for {voice_name}: {e}")
        return None

    # Version 1: Narrated (With Voice & Subtitles)
    path_narrated = assemble_version("audio_path", "Narrated")
    
    # Version 2: Pure Veo (Raw Video, No Narration, No Subtitles)
    # We pass a non-existent key to 'audio_key' and a flag to disable subs
    def assemble_pure_veo(voice_name):
        print(f"   [EDITOR] Assembling Version: {voice_name}...")
        final_clips = []
        for i, scene in enumerate(scenes):
            ai_video_path = scene.get("video_path")
            per_scene_dur = float(scene.get("duration", 4))
            if ai_video_path and os.path.exists(ai_video_path):
                try:
                    clip = VideoFileClip(ai_video_path).resized((width, height))
                    if clip.duration < per_scene_dur:
                        clip = _apply_loop(clip, per_scene_dur)
                    else:
                        clip = clip.with_duration(per_scene_dur)
                    
                    # OPTIONAL SUBTITLES: Added based on user preference
                    if state.get("enable_subtitles", True) and scene.get("narration"):
                        def _sub_renderer(get_frame, t):
                            return draw_subtitles(get_frame(t), scene["narration"], (width, height), aspect_ratio)
                        clip = clip.transform(_sub_renderer, apply_to="video")
                        
                    # NO AUDIO ADDED
                    final_clips.append(clip)

                except Exception as e:
                    print(f"      ⚠️ Failed Scene {i+1} for {voice_name}: {e}")
        
        if final_clips:
            try:
                final_v = concatenate_videoclips(final_clips, method="compose")
                filename = f"video_{voice_name}_{timestamp}.mp4"
                save_path = os.path.join("output", filename)
                final_v.write_videofile(save_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
                print(f"      ✅ Produced: {filename}")
                for c in final_clips: c.close()
                return save_path
            except Exception as e:
                print(f"      ❌ Assembly Failed for {voice_name}: {e}")
        return None

    path_pure = assemble_pure_veo("PureVeo")
    
    state["video_path"] = path_narrated or path_pure
    state["total_cost"] = round(state.get("total_cost", 0.0), 3)
    return state
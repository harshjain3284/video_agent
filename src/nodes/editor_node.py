import os
import math
import traceback
from datetime import datetime
from moviepy import VideoFileClip, concatenate_videoclips, AudioFileClip
from src.state.agent_state import AgentState
from src.utils.image_utils import draw_subtitles

def _apply_loop(clip, duration):
    """Seamlessly loops a clip to fill the required duration."""
    loops_needed = math.ceil(duration / clip.duration)
    repeated = concatenate_videoclips([clip] * loops_needed)
    return repeated.with_duration(duration)

def _prepare_clip(scene: dict, size: tuple, ratio: str, include_audio: bool = True, include_subs: bool = True) -> VideoFileClip:
    """Surgically prepares a single scene clip with trimming, resizing, and audio sync."""
    video_path = scene.get("video_path")
    if not video_path or not os.path.exists(video_path): return None

    # 1. Load and Resize
    clip = VideoFileClip(video_path).resized(size)
    
    # 2. Apply AI Inspector Trimming
    trim_s = float(scene.get("trim_start", 0.0))
    trim_e = float(scene.get("trim_end", clip.duration))
    if trim_s < trim_e <= clip.duration:
        clip = clip.subclipped(trim_s, trim_e)

    # 3. Match Duration
    target_dur = float(scene.get("duration", 4.0))
    clip = _apply_loop(clip, target_dur) if clip.duration < target_dur else clip.with_duration(target_dur)

    # 4. Attach Audio
    audio_path = scene.get("audio_path")
    if include_audio and audio_path and os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        clip = clip.with_audio(audio.with_duration(clip.duration))

    # 5. Render Subtitles
    if include_subs and scene.get("narration"):
        def _render(get_frame, t):
            return draw_subtitles(get_frame(t), scene["narration"], size, ratio)
        clip = clip.transform(_render, apply_to="video")

    return clip

def editor_node(state: AgentState) -> AgentState:
    """
    ELITE EDITOR
    Finalizes the video production with high-fidelity assembly and clean hard-cuts.
    """
    print(f"--- [Node: Elite Editor (Modular)] ---")
    scenes = state.get("scenes", [])
    if not scenes: return state

    width, height = state.get("resolution", (576, 1024))
    ratio = state.get("aspect_ratio", "9:16")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _assemble(name: str, has_audio: bool, has_subs: bool):
        print(f"   [Editor] Assembling Version: {name}...")
        clips = []
        for s in scenes:
            try:
                c = _prepare_clip(s, (width, height), ratio, has_audio, has_subs)
                if c: clips.append(c)
            except Exception as e:
                print(f"      [WARNING] Failed Scene {s.get('id')}: {e}")

        if not clips: return None

        try:
            final = concatenate_videoclips(clips, method="chain")
            out_path = os.path.join("output", f"consultease_{name}_{timestamp}.mp4")
            final.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
            for c in clips: c.close()
            return out_path
        except Exception as e:
            print(f"      [ERROR] Assembly Failed: {e}")
            return None

    # Run Dual-Assembly
    state["video_path"] = _assemble("Narrated", True, state.get("enable_subtitles", True))
    _assemble("Clean", False, False) # Background assembly for raw cuts

    # Calculate Grand Total for Receipt
    total_img = sum(s.get("image_cost", 0.0) for s in scenes)
    total_vid = sum(s.get("video_cost", 0.0) for s in scenes)
    state["total_cost"] = round(total_img + total_vid, 3)

    # LOG SUCCESS
    state["audit_log"].append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "node": "Elite Editor",
        "status": "Complete",
        "model": "MoviePy / FFMPEG",
        "details": f"Dual-Assembly finished. Main Output: {os.path.basename(state['video_path'] or 'None')}"
    })

    return state
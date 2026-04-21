import os
import PIL.Image
import numpy as np

# ---------------------------------------------------------------
# MoviePy 2.x compatible imports — NO 'moviepy.editor' namespace
# ---------------------------------------------------------------
from moviepy import (
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
    AudioFileClip,
)
import moviepy.video.fx as vfx

# Fix for Pillow 10+ (ANTIALIAS was removed)
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from src.state.agent_state import AgentState
from src.config import VIDEO_FPS, OUTPUT_DIR, ASSETS_DIR
from src.utils.core_utils import ensure_session_dir
from src.utils.video_utils import calculate_scene_duration, apply_random_motion
from src.utils.image_utils import draw_subtitles, generate_placeholder


def _apply_loop(clip, duration):
    """Safely loop a clip to the target duration using MoviePy 2.x."""
    if clip.duration <= 0:
        return clip
    loops_needed = int(duration / clip.duration) + 1
    repeated = concatenate_videoclips([clip] * loops_needed)
    return repeated.with_duration(duration)


def _apply_fadein(clip, duration=1.0):
    """Safely apply a fade-in using MoviePy 2.x CrossFadeIn effect."""
    try:
        return clip.with_effects([vfx.CrossFadeIn(duration)])
    except Exception:
        # Silently skip fade if the effect is still incompatible
        return clip


def editor_node(state: AgentState) -> AgentState:
    print("--- [Node: Final Editor (AI-Video Aware)] ---")
    width, height = state.get("resolution", (1024, 1024))
    total_target = state.get("total_duration", 20)

    scenes = state.get("scenes", [])
    if not scenes:
        print("⚠️ Processor: No scenes to process.")
        return state

    per_scene_dur_equal = calculate_scene_duration(
        total_target, len(scenes), state.get("enable_transitions", True)
    )
    clips = []

    for i, scene in enumerate(state["scenes"]):
        per_scene_dur = float(scene.get("duration", per_scene_dur_equal))

        image_path    = scene.get("image_path")
        ai_video_path = scene.get("video_path")
        audio_path    = scene.get("audio_path")
        narration     = scene.get("narration", "")

        # ── 1. VISUAL SOURCE ──────────────────────────────────────
        clip = None
        
        # Priority A: AI-Generated Motion
        if ai_video_path and os.path.exists(ai_video_path):
            try:
                print(f"🎥 Using AI Motion — Scene {i+1}")
                clip = VideoFileClip(ai_video_path).resized((width, height))
                if clip.duration < per_scene_dur:
                    clip = _apply_loop(clip, per_scene_dur)
                else:
                    clip = clip.with_duration(per_scene_dur)
            except Exception as e:
                print(f"⚠️ AI Video error (Scene {i+1}): {e}")
                clip = None

        # Priority B: Static Image + Zoom Fallback
        if not clip and image_path and os.path.exists(image_path):
            print(f"🖼️  Using Image Fallback — Scene {i+1}")
            img   = PIL.Image.open(image_path).convert("RGB").resize((width, height))
            frame = np.array(img)
            if state.get("enable_subtitles") and narration:
                frame = draw_subtitles(frame, narration, (width, height))

            clip = ImageClip(frame).with_duration(per_scene_dur)
            clip = apply_random_motion(clip)

            fallback_path = os.path.join(ensure_session_dir(state["session_id"]), f"fallback_motion_{i+1}.mp4")
            clip.write_videofile(fallback_path, fps=VIDEO_FPS, codec="libx264", audio_codec="aac", logger=None)
            scene["video_path"] = fallback_path

        # Priority C: Emergency Placeholder
        if not clip:
            print(f"⬛ Using Placeholder — Scene {i+1}")
            frame = generate_placeholder(width, height, i + 1)
            clip  = ImageClip(frame).with_duration(per_scene_dur)
            scene["video_path"] = None

        # ── 2. AUDIO SYNC ─────────────────────────────────────────
        # Double-check: only add gTTS if the user enabled it AND the file exists
        if state.get("enable_voiceover", True) and audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            if audio.duration > per_scene_dur:
                audio = audio.with_duration(per_scene_dur)
            clip = clip.with_audio(audio)
        else:
            if not state.get("enable_voiceover", True):
                print(f"   🔇 Keeping original video audio for Scene {i+1}")

        # ── 3. TRANSITIONS ────────────────────────────────────────
        if state.get("enable_transitions") and i > 0:
            clip = _apply_fadein(clip, 1.0)

        clips.append(clip)

    # ── 4. ASSEMBLE FINAL VIDEO ───────────────────────────────────
    if clips:
        final_video = concatenate_videoclips(clips, method="compose")
        final_video = final_video.with_duration(min(total_target, final_video.duration))

        output_path = os.path.join(
            OUTPUT_DIR, f"ai_video_{state['session_id']}.mp4"
        )
        final_video.write_videofile(
            output_path, fps=VIDEO_FPS,
            codec="libx264", audio_codec="aac", threads=4
        )
        state["video_path"] = output_path

    # ─── FINAL ACCOUNTING: Calculate total production cost ───
    total_bill = 0.0
    for scene in state.get("scenes", []):
        total_bill += scene.get("image_cost", 0.0)
        total_bill += scene.get("video_cost", 0.0)
    
    state["total_cost"] = round(total_bill, 3)
    print(f"💰 Total Production Cost: ${state['total_cost']}")

    return state

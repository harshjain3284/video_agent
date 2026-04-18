import os
import PIL.Image
import numpy as np
from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips, AudioFileClip

# Fix for Pillow 10+
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from src.state.agent_state import AgentState
from src.config import VIDEO_FPS, OUTPUT_DIR, ASSETS_DIR
from src.utils.video_utils import calculate_scene_duration, apply_random_motion
from src.utils.image_utils import draw_subtitles, generate_placeholder

def processor_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Processor (AI-Video Aware)] ---")
    width, height = state.get("resolution", (1024, 1024))
    total_target = state.get("total_duration", 20)
    
    per_scene_dur_equal = calculate_scene_duration(total_target, len(state["scenes"]), state.get("enable_transitions", True))
    clips = []
    
    for i, scene in enumerate(state["scenes"]):
        # USE DYNAMIC DURATION FROM PARSER
        per_scene_dur = scene.get("duration", per_scene_dur_equal)
        
        image_path = scene.get("image_path")
        # THIS IS THE REAL AI VIDEO PRODUCED BY THE ANIMATOR
        ai_video_path = scene.get("video_path") 
        audio_path = scene.get("audio_path")
        narration = scene.get("narration", "")
        
        # 1. VISUAL SOURCE: Check for AI Video First
        if ai_video_path and os.path.exists(ai_video_path):
            print(f"🎥 Using AI-Generated Motion for Scene {i+1} ({per_scene_dur}s)")
            # Load and loop the video if it's shorter than the target duration
            clip = VideoFileClip(ai_video_path).resize((width, height))
            if clip.duration < per_scene_dur:
                clip = clip.loop(duration=per_scene_dur)
            else:
                clip = clip.set_duration(per_scene_dur)

        elif image_path and os.path.exists(image_path):
            print(f"🖼️ Using Static Image + Fallback Motion for Scene {i+1} ({per_scene_dur}s)")
            img = PIL.Image.open(image_path).convert("RGB").resize((width, height))
            frame = np.array(img)
            if state.get("enable_subtitles") and narration:
                frame = draw_subtitles(frame, narration, (width, height))
            
            # Create the motion clip
            clip = ImageClip(frame).set_duration(per_scene_dur)
            clip = apply_random_motion(clip)
            
            # SAVE the fallback video so UI can preview it
            fallback_path = os.path.join(ASSETS_DIR, state["session_id"], f"fallback_motion_{i+1}.mp4")
            clip.write_videofile(fallback_path, fps=VIDEO_FPS, codec="libx264", audio_codec="aac", logger=None)
            scene["video_path"] = fallback_path
        else:
            frame = generate_placeholder(width, height, i + 1)
            clip = ImageClip(frame).set_duration(per_scene_dur)
            scene["video_path"] = None


        # 2. AUDIO SYNC
        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            clip = clip.set_audio(audio.set_duration(per_scene_dur) if audio.duration > per_scene_dur else audio)
        
        if state.get("enable_transitions") and i > 0:
            clip = clip.crossfadein(1.0)
        clips.append(clip)
    
    if clips:
        padding = -1.0 if state.get("enable_transitions") else 0
        final_video = concatenate_videoclips(clips, method="compose", padding=padding).set_duration(total_target)
        
        output_path = os.path.join(OUTPUT_DIR, f"ai_video_{state['session_id']}.mp4")
        final_video.write_videofile(output_path, fps=VIDEO_FPS, codec="libx264", audio_codec="aac", threads=4)
        state["video_path"] = output_path
        
    return state

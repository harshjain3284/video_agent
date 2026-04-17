import os
import PIL.Image

# Fix for Pillow 10+ metadata in MoviePy
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from src.state.agent_state import AgentState
from src.config import VIDEO_FPS, OUTPUT_DIR
from src.utils.video_utils import apply_random_motion, calculate_scene_duration
from src.utils.image_utils import draw_subtitles, generate_placeholder

def processor_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Processor (Modular)] ---")
    width, height = state.get("resolution", (1024, 1024))
    total_target = state.get("total_duration", 20)
    
    per_scene_dur = calculate_scene_duration(total_target, len(state["scenes"]), state.get("enable_transitions", True))
    clips = []
    
    for i, scene in enumerate(state["scenes"]):
        image_path = scene.get("image_path")
        audio_path = scene.get("audio_path")
        narration = scene.get("narration", "")
        
        # 1. Visual Source
        if image_path and os.path.exists(image_path):
            img = PIL.Image.open(image_path).convert("RGB").resize((width, height))
            frame = np.array(img)
        else:
            frame = generate_placeholder(width, height, i + 1)

        # 2. Add Subtitles & Create Clip
        if state.get("enable_subtitles") and narration:
            frame = draw_subtitles(frame, narration, (width, height))
            
        clip = ImageClip(frame).set_duration(per_scene_dur)

        # 3. Audio & Motion Sync
        if audio_path and os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            clip = clip.set_audio(audio.set_duration(per_scene_dur) if audio.duration > per_scene_dur else audio)
        
        clip = apply_random_motion(clip)
        if state.get("enable_transitions") and i > 0:
            clip = clip.crossfadein(1.0)
        clips.append(clip)
    
    if clips:
        padding = -1.0 if state.get("enable_transitions") else 0
        final_video = concatenate_videoclips(clips, method="compose", padding=padding).set_duration(total_target)
        
        output_path = os.path.join(OUTPUT_DIR, f"final_{state['session_id']}.mp4")
        final_video.write_videofile(output_path, fps=VIDEO_FPS, codec="libx264", audio_codec="aac", threads=4)
        state["video_path"] = output_path
        
    return state

import numpy as np # Added back for placeholder

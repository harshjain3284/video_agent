import os
import subprocess
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import PIL.Image  # Handle newer Pillow versions for MoviePy
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from src.state.agent_state import AgentState
from src.config import VIDEO_FPS, SCENE_DURATION, OUTPUT_DIR

def apply_ken_burns(clip):
    """
    Applies a slow zoom-in effect to a static image clip.
    This effectively uses FFmpeg filters via MoviePy's resize method.
    """
    return clip.resize(lambda t: 1 + 0.02 * t)

def processor_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Processor (Rendering with FFmpeg)] ---")
    clips = []
    
    for i, scene in enumerate(state["scenes"]):
        image_path = scene.get("image_path")
        audio_path = scene.get("audio_path")
        
        if image_path and os.path.exists(image_path):
            print(f"Processing scene {scene['id']} with voiceover...")
            
            # Load image
            clip = ImageClip(image_path)
            
            # Load and set audio (if exists)
            if audio_path and os.path.exists(audio_path):
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                clip = clip.set_duration(duration)
                clip = clip.set_audio(audio_clip)
            else:
                clip = clip.set_duration(SCENE_DURATION)
                
            clip = apply_ken_burns(clip)
            clips.append(clip)
    
    if clips:
        print(f"Stitching {len(clips)} clips with synchronized audio...")
        final_video = concatenate_videoclips(clips, method="compose")
        
        output_path = os.path.join(OUTPUT_DIR, f"final_video_{state['session_id']}.mp4")
        
        # 3. Final Render (Powered by FFmpeg)
        # MoviePy executes FFmpeg commands under the hood
        print("Rendering final multimedia file via FFmpeg...")
        final_video.write_videofile(
            output_path, 
            fps=VIDEO_FPS, 
            codec="libx264", 
            audio_codec="aac" if state.get("audio_path") else None,
            threads=4, 
            preset="medium"
        )
        
        state["video_path"] = output_path
    else:
        state["error"] = "No clips were generated to stitch."
    
    return state

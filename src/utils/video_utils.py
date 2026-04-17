import random
from moviepy.editor import VideoClip

def apply_random_motion(clip):
    """Applies randomized cinematic zoom effects."""
    motion_type = random.choice(["zoom_in", "zoom_out"])
    duration = clip.duration
    
    if motion_type == "zoom_in":
        return clip.resize(lambda t: 1 + 0.04 * (t / duration))
    else:
        return clip.resize(lambda t: 1.04 - 0.04 * (t / duration))

def calculate_scene_duration(total_duration, num_scenes, enable_transitions):
    """Calculates per-scene duration accounting for transition overlaps."""
    trans_dur = 1.0 if enable_transitions else 0
    if num_scenes > 1 and enable_transitions:
        return (total_duration + (num_scenes - 1) * trans_dur) / num_scenes
    return total_duration / num_scenes

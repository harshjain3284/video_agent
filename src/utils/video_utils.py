import random
import numpy as np
import PIL.Image

# ---------------------------------------------------------------
# Video Utilities - Cleaned of legacy zoom/pan fallbacks
# ---------------------------------------------------------------

def calculate_scene_duration(total_duration, num_scenes, enable_transitions):
    """Calculates per-scene duration accounting for transition overlaps."""
    trans_dur = 1.0 if enable_transitions else 0
    if num_scenes > 1 and enable_transitions:
        return (total_duration + (num_scenes - 1) * trans_dur) / num_scenes
    return total_duration / num_scenes

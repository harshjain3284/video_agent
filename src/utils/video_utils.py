import random
import numpy as np
import PIL.Image

# ---------------------------------------------------------------
# MoviePy 2.x compatible — uses only 'fl_image' for frame ops
# ---------------------------------------------------------------

def apply_random_motion(clip):
    """Applies randomized cinematic Ken-Burns zoom using fl_image (MoviePy 2.x)."""
    motion_type = random.choice(["zoom_in", "zoom_out"])
    duration = clip.duration
    w, h = clip.w, clip.h

    if motion_type == "zoom_in":
        def zoom_in(get_frame, t):
            frame = get_frame(t)
            scale = 1 + 0.04 * (t / duration)
            new_w, new_h = int(w * scale), int(h * scale)
            img = PIL.Image.fromarray(frame).resize((new_w, new_h), PIL.Image.LANCZOS)
            # Center-crop back to original size
            left = (new_w - w) // 2
            top  = (new_h - h) // 2
            return np.array(img.crop((left, top, left + w, top + h)))
        return clip.transform(zoom_in, apply_to="video")
    else:
        def zoom_out(get_frame, t):
            frame = get_frame(t)
            scale = 1.04 - 0.04 * (t / duration)
            scale = max(scale, 1.0)   # never shrink below original size
            new_w, new_h = int(w * scale), int(h * scale)
            img = PIL.Image.fromarray(frame).resize((new_w, new_h), PIL.Image.LANCZOS)
            left = (new_w - w) // 2
            top  = (new_h - h) // 2
            return np.array(img.crop((left, top, left + w, top + h)))
        return clip.transform(zoom_out, apply_to="video")


def calculate_scene_duration(total_duration, num_scenes, enable_transitions):
    """Calculates per-scene duration accounting for transition overlaps."""
    trans_dur = 1.0 if enable_transitions else 0
    if num_scenes > 1 and enable_transitions:
        return (total_duration + (num_scenes - 1) * trans_dur) / num_scenes
    return total_duration / num_scenes

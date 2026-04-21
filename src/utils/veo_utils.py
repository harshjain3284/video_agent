import time
import os
from google.genai import types as genai_types

def normalize_veo_aspect_ratio(aspect_ratio: str) -> str:
    """Veo 3.1 supports only 16:9 and 9:16."""
    if "9:16" in aspect_ratio or "9/16" in aspect_ratio:
        return "9:16"
    if "16:9" in aspect_ratio or "16/9" in aspect_ratio:
        return "16:9"
    return "16:9"

def normalize_veo_duration(duration: int | None) -> int:
    """Veo 3.1 valid durations are 4, 6, 8."""
    if duration in {4, 6, 8}:
        return duration
    return 4

def wait_for_veo_operation(client, operation, timeout_mins=6):
    """Polls the Veo operation until completion or timeout."""
    max_polls = (timeout_mins * 60) // 10
    for _ in range(max_polls):
        if operation.done:
            return operation
        time.sleep(10)
        operation = client.operations.get(operation)
    return operation

def download_veo_video(client, operation, output_path):
    """Extracts, downloads, and saves the video from a completed operation."""
    response = getattr(operation, "response", None)
    if not response or not getattr(response, "generated_videos", None):
        return False

    generated_video = response.generated_videos[0]
    video_obj = generated_video.video

    client.files.download(file=video_obj)
    video_obj.save(output_path)
    return True

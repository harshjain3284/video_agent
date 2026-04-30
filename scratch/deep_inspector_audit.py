import os
import sys
import json
from google import genai
from google.genai import types as genai_types

# Manually add root to sys.path to avoid ModuleNotFoundError
sys.path.append(os.getcwd())

from src.config import GEMINI_API_KEY, MODEL_REGISTRY
from src.nodes.inspector_node import _inspect_single_video

def run_deep_inspector_audit():
    print("--- [DEEP AUDIT: Quality Inspector Output] ---")
    api_key = GEMINI_API_KEY.strip(' "\'')
    client = genai.Client(api_key=api_key)
    
    # Target a real video generated in your last session
    test_video = "assets/20260430_102847/ai_motion_2.mp4"
    
    if not os.path.exists(test_video):
        print("ERROR: Target video not found. Checking alternate session...")
        # Emergency fallback to find any video
        for root, dirs, files in os.walk("assets"):
            for file in files:
                if file.endswith(".mp4") and "ai_motion" in file:
                    test_video = os.path.join(root, file)
                    break
            if test_video.endswith(".mp4"): break

    if not os.path.exists(test_video):
        print("CRITICAL: No videos found in assets/ to inspect.")
        return

    print(f"Inspecting File: {test_video}")
    
    # Dynamic Duration Detection
    from moviepy.editor import VideoFileClip
    clip = VideoFileClip(test_video)
    actual_duration = clip.duration
    clip.close()
    print(f"Detected Duration: {actual_duration} seconds")

    scene = {
        "id": 2,
        "video_path": test_video,
        "narration": "Authentic Indian professional explaining corporate compliance.",
        "duration": actual_duration
    }
    
    try:
        # Run the actual production node logic
        analysis = _inspect_single_video(client, scene)
        
        print("\n" + "="*50)
        print("🎬 AI INSPECTOR REPORT")
        print("="*50)
        print(f"Quality Score: {analysis.get('quality_score', 0) * 100}%")
        print(f"Glitch Detected: {analysis.get('has_glitch', 'Unknown')}")
        print(f"Reasoning: {analysis.get('reason', 'N/A')}")
        
        print("\n" + "="*50)
        print("⏰ RECOMMENDED TIMELINE (The 'Bad' parts are trimmed out)")
        print("="*50)
        start = analysis.get('trim_start', 0.0)
        end = analysis.get('trim_end', 8.0)
        print(f"KEEP RANGE: {start}s to {end}s")
        print(f"TRIMMED OUT: {0.0}s-{start}s AND {end}s-8.0s")
        print("="*50)
        
    except Exception as e:
        print(f"INSPECTION FAILED: {e}")

if __name__ == "__main__":
    run_deep_inspector_audit()

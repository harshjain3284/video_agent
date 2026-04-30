import os
import json
from google import genai
from src.config import GEMINI_API_KEY, MODEL_REGISTRY
from src.nodes.inspector_node import _inspect_single_video

def test_inspector():
    print("--- [Diagnostic: Inspector Node Audit] ---")
    api_key = GEMINI_API_KEY.strip(' "\'')
    client = genai.Client(api_key=api_key)
    
    # Using the existing video from the last session
    test_video = "assets/20260430_102847/ai_motion_2.mp4"
    
    if not os.path.exists(test_video):
        print(f"ERROR: Test video {test_video} not found. Searching for another...")
        # Fallback to any mp4 in assets
        for root, dirs, files in os.walk("assets"):
            for file in files:
                if file.endswith(".mp4"):
                    test_video = os.path.join(root, file)
                    break
            if test_video.endswith(".mp4"): break

    print(f"Targeting Video: {test_video}")
    
    scene = {
        "id": 1,
        "video_path": test_video,
        "narration": "Testing the fixed inspector node."
    }
    
    try:
        print("Uploading to Gemini 3.1 Pro for inspection...")
        analysis = _inspect_single_video(client, scene)
        print("RESULT: Inspection Successful!")
        print(json.dumps(analysis, indent=2))
    except Exception as e:
        print(f"FAILED: Inspector still has issues: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_inspector()

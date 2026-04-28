import os
import sys
import uuid
from datetime import datetime

# Add the project root to sys.path
sys.path.append(os.getcwd())

from src.state.agent_state import AgentState
from src.nodes.parser_node import parser_node
from src.nodes.voice_node import voice_node
from src.config import DEFAULT_VOICE_LANGUAGE

def run_test(gender="Female"):
    print(f"Starting Voice Generation Pipeline Test (Hindi - {gender})...")
    
    # 1. Initialize State
    state: AgentState = {
        "input_text": "Income Tax Saving tips for FY 2024-25 in India",
        "session_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "scenes": [],
        "video_path": None,
        "audio_path": None,
        "current_node": "start",
        "error": None,
        "aspect_ratio": "16:9",
        "resolution": (1024, 576),
        "scene_count": 0,
        "scene_duration": 5,
        "enable_subtitles": True,
        "enable_voiceover": True,
        "enable_transitions": True,
        "total_duration": 20,
        "model_id": "Nano Banana (Fast)",
        "video_model_id": "Veo 3.1 (Cinematic Video)",
        "video_clips": [],
        "usage_stats": [],
        "total_cost": 0.0,
        "script": None,
        "character_description": None,
        "category": "Income Tax",
        "post_type": "Authority",
        "hook_type": "Pain",
        "brand_page": "consultease.app",
        "format": "Education",
        "visual_strategy": "narrator",
        "audit_log": [],
        "voice_language": "Hindi (India)",
        "voice_gender": gender,
        "session_seed": 42,
        "identity_dna": None
    }

    # 2. Run Parser Node (Generates Script, Scenes, Narration)
    print("\n--- Running Parser Node ---")
    state = parser_node(state)
    
    if state.get("error"):
        print(f"Parser Error: {state['error']}")
        return

    print(f"Script Generated (Hinglish): {state.get('script')[:100]}...")
    print(f"Scenes Generated: {len(state['scenes'])}")

    # 3. Run Voice Node (Generates Audio)
    print("\n--- Running Voice Node ---")
    state = voice_node(state)

    # 4. Verify Results
    print("\n--- Final Verification ---")
    all_success = True
    for i, scene in enumerate(state["scenes"]):
        audio_path = scene.get("audio_path")
        if audio_path and os.path.exists(audio_path):
            size = os.path.getsize(audio_path)
            print(f"Scene {i+1}: Audio generated at {audio_path} ({size} bytes)")
        else:
            print(f"Scene {i+1}: Audio FAILED to generate.")
            all_success = False

    if all_success:
        print("\nSUCCESS: Voice generation pipeline working correctly for Hindi using Edge-TTS!")
    else:
        print("\nFAILURE: Some scenes failed to generate voice.")
        for log in state.get("audit_log", []):
            if log.get("status") == "Total Failure":
                print(f"   Traceback: {log.get('trace')}")

if __name__ == "__main__":
    target_gender = sys.argv[1] if len(sys.argv) > 1 else "Female"
    run_test(gender=target_gender)

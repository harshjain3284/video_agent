import os
from gtts import gTTS
from concurrent.futures import ThreadPoolExecutor
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR

def generate_scene_audio(scene, session_id):
    """Helper to generate a single scene voiceover."""
    print(f"🎤 Voice: Starting Scene {scene['id']}...")
    narration = scene.get("narration")
    if narration:
        try:
            tts = gTTS(text=narration, lang='en')
            audio_path = os.path.join(ASSETS_DIR, session_id, f"voice_{scene['id']}.mp3")
            tts.save(audio_path)
            scene["audio_path"] = audio_path
            print(f"✅ Scene {scene['id']} audio complete")
        except Exception as e:
            print(f"❌ Voice Scene {scene['id']} Error: {e}")
    else:
        scene["audio_path"] = None
    return scene

def voice_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Parallel Scene Audio] ---")
    
    if not state.get("enable_voiceover", True):
        print("   🔇 Voiceover disabled by user. Skipping.")
        for scene in state["scenes"]:
            scene["audio_path"] = None
        return state

    with ThreadPoolExecutor() as executor:
        # Launch generation for ALL scene audio clips at once
        results = list(executor.map(lambda s: generate_scene_audio(s, state["session_id"]), state["scenes"]))
            
    state["scenes"] = results
    return state

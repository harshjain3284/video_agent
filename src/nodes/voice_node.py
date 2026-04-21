import os
import asyncio
import edge_tts
from concurrent.futures import ThreadPoolExecutor
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR

async def _save_edge_audio(text, path):
    """Internal helper to save neural speech."""
    # en-US-AvaNeural is a premium sounding female voice. 
    # Alternatives: en-US-AndrewNeural (Male), en-GB-SoniaNeural (UK Female)
    communicate = edge_tts.Communicate(text, "en-US-AvaNeural")
    await communicate.save(path)

def generate_scene_audio(scene, session_id):
    """Helper to generate a single scene voiceover using Neural TTS."""
    print(f"🎤 Neural Voice: Starting Scene {scene['id']}...")
    narration = scene.get("narration")
    if narration:
        try:
            audio_path = os.path.join(ASSETS_DIR, session_id, f"voice_{scene['id']}.mp3")
            # Run the asymmetric call in a bridge
            asyncio.run(_save_edge_audio(narration, audio_path))
            scene["audio_path"] = audio_path
            print(f"✅ Scene {scene['id']} neural audio complete")
        except Exception as e:
            print(f"❌ Voice Scene {scene['id']} Error: {e}")
    else:
        scene["audio_path"] = None
    return scene

def voice_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Voiceover Generation] ---")
    
    # 1. Check if user actually wants AI Voice
    enable_voice = state.get("enable_voiceover", True)
    print(f"   🔈 AI Voiceover Enabled: {enable_voice}")

    if not enable_voice:
        print("   🔇 User chose Pure Video Sound. Skipping gTTS.")
        for scene in state["scenes"]:
            scene["audio_path"] = None
        return state

    print(f"   🎙️ Generating speech for {len(state['scenes'])} scenes...")
    with ThreadPoolExecutor() as executor:
        # Launch generation for ALL scene audio clips at once
        results = list(executor.map(lambda s: generate_scene_audio(s, state["session_id"]), state["scenes"]))
            
    state["scenes"] = results
    return state

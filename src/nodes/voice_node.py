import os
import re
import asyncio
import edge_tts
from concurrent.futures import ThreadPoolExecutor
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR, DEFAULT_VOICE_LANGUAGE, VOICE_LANGUAGES, STRATEGIC_VOICES

async def _save_edge_audio(text, path, voice):
    """Internal helper to save neural speech."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)

def generate_scene_audio(scene, session_id, voice):
    """Helper to generate a single scene voiceover using Neural TTS."""
    print(f"🎤 Neural Voice: Starting Scene {scene['id']}...")
    raw_narration = scene.get("narration", "")
    # Strip SSML tags for Edge-TTS compatibility
    narration = re.sub(r'<[^>]*>', '', raw_narration).strip()
    if narration and any(c.isalnum() for c in narration):
        try:
            audio_path = os.path.join(ASSETS_DIR, session_id, f"voice_{scene['id']}.mp3")
            # Run the asymmetric call in a bridge
            asyncio.run(_save_edge_audio(narration, audio_path, voice))
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
    
    # Get the voice based on state or default
    lang_key = state.get("voice_language", DEFAULT_VOICE_LANGUAGE)
    voice = VOICE_LANGUAGES.get(lang_key, VOICE_LANGUAGES[DEFAULT_VOICE_LANGUAGE])["voice"]
    
    # Stratgeic Override for Hindi (to match brand personality)
    if "Hindi" in lang_key:
        post_type = state.get("post_type", "Authority")
        voice = STRATEGIC_VOICES.get(post_type, voice)
        
    print(f"   🗣️ Using Voice: {lang_key} ({voice})")

    with ThreadPoolExecutor() as executor:
        # Launch generation for ALL scene audio clips at once
        results = list(executor.map(lambda s: generate_scene_audio(s, state["session_id"], voice), state["scenes"]))
            
    state["scenes"] = results
    return state

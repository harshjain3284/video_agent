import os
import re
import asyncio
import edge_tts
import time
import traceback
from gtts import gTTS
from datetime import datetime
from src.state.agent_state import AgentState
from src.config import DEFAULT_VOICE_LANGUAGE, VOICE_LANGUAGES, STRATEGIC_VOICES, DEFAULT_VOICE_GENDER
from src.utils.core_utils import ensure_session_dir

def _clean_narration_text(text: str) -> str:
    """Removes non-speakable elements like brackets, stars, and complex symbols."""
    text = re.sub(r'\[.*?\]', '', text) # Remove [Brackets]
    text = re.sub(r'\*.*?\*', '', text) # Remove *Stars*
    # Keep only letters, numbers, spaces and essential punctuation (Hindi/Latin)
    text = re.sub(r'[^a-zA-Z0-9\u0900-\u097F\s.,?!]', ' ', text)
    return ' '.join(text.split()).strip()

async def _save_edge_audio(text: str, path: str, voice: str, rate: str):
    """Low-level Edge-TTS communicator."""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(path)

def _execute_tts_sync(text: str, path: str, voice: str, rate: str):
    """Bridge to handle async Edge-TTS in a synchronous pipeline."""
    try:
        # Windows-specific event loop policy for stability
        if os.name == 'nt':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_save_edge_audio(text, path, voice, rate))
        loop.close()
        return os.path.exists(path) and os.path.getsize(path) > 0
    except:
        return False

def _generate_audio_with_fallbacks(text: str, path: str, voice: str, is_hindi: bool) -> bool:
    """Robust fallback chain: 1. Neural Edge-TTS -> 2. System CLI -> 3. gTTS (Emergency)"""
    rate = "+20%" if is_hindi else "+10%"
    
    # 1. Primary: Edge-TTS (Neural)
    if _execute_tts_sync(text, path, voice, rate): return True
    
    # 2. Secondary: Edge-TTS CLI (Process Fallback)
    try:
        import subprocess
        subprocess.run(["edge-tts", "--voice", voice, "--text", text, "--write-media", path, "--rate", rate], 
                      check=True, capture_output=True)
        if os.path.exists(path) and os.path.getsize(path) > 0: return True
    except: pass

    # 3. Tertiary: gTTS (The Unstoppable Emergency Backup)
    try:
        tts = gTTS(text=text, lang='hi' if is_hindi else 'en')
        tts.save(path)
        return os.path.exists(path) and os.path.getsize(path) > 0
    except: pass
    
    return False

def voice_node(state: AgentState) -> AgentState:
    """
    ELITE VOICE GENERATOR (Self-Healing)
    Ensures every scene has high-energy narration using a robust fallback engine.
    """
    print(f"--- [Node: Voice Generator (Modular)] ---")
    if not state.get("enable_voiceover", True): return state

    # 1. Determine Voice Persona
    lang_key = state.get("voice_language", DEFAULT_VOICE_LANGUAGE)
    is_hindi = "Hindi" in lang_key
    voice_config = VOICE_LANGUAGES.get(lang_key, VOICE_LANGUAGES[DEFAULT_VOICE_LANGUAGE])
    
    # Prioritize strategic match for Consultease post types
    gender = state.get("voice_gender", DEFAULT_VOICE_GENDER)
    voice = voice_config.get(gender.lower(), voice_config.get("female"))
    if is_hindi and not state.get("voice_gender"):
        voice = STRATEGIC_VOICES.get(state.get("post_type", "Authority"), voice)

    # 2. Process Scenes
    output_dir = ensure_session_dir(state["session_id"])
    for s in state["scenes"]:
        audio_path = os.path.join(output_dir, f"voice_{s.get('id', 'temp')}.mp3")
        
        # Skip if already exists (Idempotency)
        if os.path.exists(audio_path):
            s["audio_path"] = audio_path
            continue

        clean_text = _clean_narration_text(s.get("narration", ""))
        if not clean_text: continue

        print(f"   [VOICE] Narrating Scene {s.get('id')}: {clean_text[:30]}...")
        if _generate_audio_with_fallbacks(clean_text, audio_path, voice, is_hindi):
            s["audio_path"] = audio_path
            
    return state

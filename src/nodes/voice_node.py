import os
import re
import asyncio
import edge_tts
import traceback
from datetime import datetime
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR, DEFAULT_VOICE_LANGUAGE, VOICE_LANGUAGES, STRATEGIC_VOICES
from src.utils.core_utils import ensure_session_dir, retry_with_backoff
import time

async def _save_edge_audio(text, path, voice, rate="+0%"):
    """Internal helper to save neural speech with specific rate."""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(path)

def generate_scene_audio(scene, session_id, voice, audit_log, is_hindi=False):
    """Self-Healing Voice Generator with Auto-Rate Fallback."""
    scene_id = scene.get("id", "unknown")
    output_dir = ensure_session_dir(session_id)
    audio_path = os.path.join(output_dir, f"voice_{scene_id}.mp3")
    
    if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
        scene["audio_path"] = audio_path
        return scene

    raw_narration = scene.get("narration", "")
    
    # 🧼 DEEP CLEANER: Remove all AI junk and non-essential symbols
    # We keep letters, numbers, spaces, dots, and commas. 
    clean_text = re.sub(r'\[.*?\]', '', raw_narration) # Remove [Brackets]
    clean_text = re.sub(r'\*.*?\*', '', clean_text)    # Remove *Stars*
    clean_text = re.sub(r'[^a-zA-Z0-9\u0900-\u097F\s.,]', ' ', clean_text) # Keep Devanagari + Latin + basic punct
    clean_text = ' '.join(clean_text.split()) # Remove double spaces
    
    if not clean_text or not any(c.isalnum() for c in clean_text):
        return scene

    def _call_tts(target_rate=None):
        # Fallback Logic: Try High Energy first, then move to Normal
        active_rate = target_rate if target_rate is not None else ("+10%" if is_hindi else "+0%")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_save_edge_audio(clean_text, audio_path, voice, rate=active_rate))
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                scene["audio_path"] = audio_path
                audit_log.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "node": f"Voice Gen {scene_id}",
                    "status": "Success",
                    "model": f"{voice} (Energy: {active_rate})",
                    "details": f"Cleaned: {clean_text[:60]}..."
                })
                return scene
            raise ValueError(f"No audio returned for rate {active_rate}")
        finally:
            loop.close()

    try:
        # ATTEMPT 1: High Energy (+10%)
        return _call_tts(target_rate="+10%" if is_hindi else "+0%")
    except Exception as e:
        try:
            # ATTEMPT 2: Normal Speed (+0%)
            print(f"⚠️ High-Energy failed for Scene {scene_id}. Retrying with Normal Speed...")
            return _call_tts(target_rate="+0%")
        except Exception as e2:
            trace = traceback.format_exc()
            print(f"❌ [DEV ERROR] Voice Gen Critical Failure:\n{trace}")
            audit_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "node": f"Voice Gen {scene_id}",
                "status": "Total Failure (Dev Trace)",
                "model": voice,
                "details": str(e2),
                "trace": trace
            })
            scene["audio_path"] = None
            return scene

def voice_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Voiceover Generator (Self-Healing Mode)] ---")
    if "audit_log" not in state: state["audit_log"] = []
    
    enable_voice = state.get("enable_voiceover", True)
    if not enable_voice: return state

    lang_key = state.get("voice_language", DEFAULT_VOICE_LANGUAGE)
    is_hindi = "Hindi" in lang_key
    voice_config = VOICE_LANGUAGES.get(lang_key, VOICE_LANGUAGES[DEFAULT_VOICE_LANGUAGE])
    voice = voice_config["voice"]
    
    if is_hindi:
        post_type = state.get("post_type", "Authority")
        voice = STRATEGIC_VOICES.get(post_type, voice)

    results = []
    for s in state["scenes"]:
        res = generate_scene_audio(s, state["session_id"], voice, state["audit_log"], is_hindi=is_hindi)
        results.append(res if res else s)
        time.sleep(1.8)
            
    state["scenes"] = results
    return state

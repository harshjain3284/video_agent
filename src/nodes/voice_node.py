import os
import re
import asyncio
import edge_tts
import traceback
from gtts import gTTS
from datetime import datetime
from src.state.agent_state import AgentState
from src.config import ASSETS_DIR, DEFAULT_VOICE_LANGUAGE, VOICE_LANGUAGES, STRATEGIC_VOICES, DEFAULT_VOICE_GENDER
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
    
    # SURGICAL CLEANER: Total focus on speakable text.
    clean_text = re.sub(r'\[.*?\]', '', raw_narration) # Remove [Brackets]
    clean_text = re.sub(r'\*.*?\*', '', clean_text)    # Remove *Stars*
    # Remove all complex symbols, keeping only letters, numbers, spaces and essential Hindi/Latin punctuation
    clean_text = re.sub(r'[^a-zA-Z0-9\u0900-\u097F\s.,?!]', ' ', clean_text)
    clean_text = ' '.join(clean_text.split()) # Remove double spaces
    
    if not clean_text or not any(c.isalnum() for c in clean_text):
        print(f"   [WARNING] Scene {scene_id} has no speakable narration. Skipping TTS.")
        return scene

    active_rate = "+10%" if is_hindi else "+0%"

    def _call_tts(target_rate=None):
        nonlocal active_rate
        if target_rate is not None:
            active_rate = target_rate
            
        print(f"   Scene {scene_id}: Generating TTS for [{clean_text[:40]}...]")
        
        # Defensive Wait to prevent server-side drops
        time.sleep(1.0)
        
        try:
            # Handle Loop safely for Streamlit/Anaconda
            if os.name == 'nt':
                try:
                    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
                except:
                    pass
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            if loop.is_running():
                import threading
                thread_exc = []
                def _run():
                    try:
                        asyncio.run(_save_edge_audio(clean_text, audio_path, voice, rate=active_rate))
                    except Exception as te:
                        thread_exc.append(te)
                
                t = threading.Thread(target=_run)
                t.start()
                t.join()
                
                if thread_exc:
                    raise thread_exc[0]
            else:
                loop.run_until_complete(_save_edge_audio(clean_text, audio_path, voice, rate=active_rate))

            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                scene["audio_path"] = audio_path
                audit_log.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "node": f"Voice Gen {scene_id}",
                    "status": "Success",
                    "model": f"{voice} (Energy: {active_rate})",
                    "details": f"Narration: {clean_text}"
                })
                return scene
            raise ValueError(f"No audio returned for rate {active_rate}")
        except Exception as e:
            raise e

    try:
        # ATTEMPT 1: High Energy
        return _call_tts(target_rate="+10%" if is_hindi else "+0%")
    except Exception as e:
        trace1 = traceback.format_exc()
        print(f"[ATTEMPT 1 FAILED] Scene {scene_id}:\n{trace1}")
        try:
            # ATTEMPT 2: Defensive Retry with Delay
            time.sleep(1.5)
            print(f"[RETRYING] Normal Speed (Attempt 2)...")
            return _call_tts(target_rate="+0%")
        except Exception as e2:
            trace2 = traceback.format_exc()
            print(f"[ATTEMPT 2 FAILED] Scene {scene_id}:\n{trace2}")
            try:
                # ATTEMPT 3: Deep Clean & Reset
                print(f"[RETRYING] Deep-Clean (Attempt 3)...")
                clean_text = re.sub(r'[^a-zA-Z\u0900-\u097F\s]', '', clean_text)
                time.sleep(2.0)
                return _call_tts(target_rate="+0%")
            except Exception as e3:
                trace3 = traceback.format_exc()
                print(f"[ATTEMPT 3 FAILED] Scene {scene_id}:\n{trace3}")
                try:
                    # ATTEMPT 4: System CLI Fallback (The Nuclear Option)
                    print(f"[FINAL FALLBACK] Using System CLI for Scene {scene_id}...")
                    import subprocess
                    cmd = ["edge-tts", "--voice", voice, "--text", clean_text, "--write-media", audio_path, "--rate", active_rate]
                    subprocess.run(cmd, check=True, capture_output=True)
                    
                    if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                        scene["audio_path"] = audio_path
                        print(f"      CLI Success!")
                        return scene
                    raise RuntimeError("CLI failed to create file.")
                except Exception as e4:
                    try:
                        # ATTEMPT 5: Google TTS (The Unstoppable Backup)
                        print(f"[EMERGENCY] Switching to Google Cloud TTS for Scene {scene_id}...")
                        from gtts import gTTS
                        tts = gTTS(text=clean_text, lang='hi' if is_hindi else 'en')
                        tts.save(audio_path)
                        
                        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 0:
                            scene["audio_path"] = audio_path
                            print(f"      Google TTS Success!")
                            return scene
                        raise RuntimeError("gTTS failed to create file.")
                    except Exception as e5:
                        trace = traceback.format_exc()
                        print(f" [TOTAL FATAL] All 5 Voice Engines failed:\n{trace}")
                        audit_log.append({"timestamp": datetime.now().strftime("%H:%M:%S"), "node": f"Voice Gen {scene_id}", "status": "Total Failure", "trace": trace})
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
    
    # 1. Determine base voice by gender
    gender = state.get("voice_gender", DEFAULT_VOICE_GENDER).lower()
    voice = voice_config.get(gender, voice_config.get("female")) # Fallback to female if gender invalid
    
    # 2. STRATEGIC OVERRIDE: Only if user hasn't explicitly set a gender preference 
    # (Optional: Or we can prioritize strategy. Let's prioritize user choice if present)
    if "voice_gender" not in state or not state["voice_gender"]:
        if is_hindi:
            post_type = state.get("post_type", "Authority")
            voice = STRATEGIC_VOICES.get(post_type, voice)

    results = []
    for s in state["scenes"]:
        scene_id = s.get("id", "unknown")
        print(f"   [VOICE] Generating best available narration for Scene {scene_id}...")
        res = generate_scene_audio(s, state["session_id"], voice, state["audit_log"], is_hindi=is_hindi)
        if res and res.get("audio_path"):
            s["audio_path"] = res["audio_path"]
        results.append(s)
        time.sleep(1.0)
    
    state["scenes"] = results
    return state

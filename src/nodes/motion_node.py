import os
import base64
import PIL.Image
import traceback
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, GROQ_API_KEY
from src.prompts import MOTION_PROMPT, DEFAULT_MOTION_PROMPT
from src.utils.core_utils import retry_with_backoff
import time

def motion_analyst_node(state: AgentState) -> AgentState:
    """Modular Motion Analyst: Using centralized prompts and Triple-Model Chain."""
    print(f"--- [Node: Motion Analyst (Modular Mode)] ---")
    if "audit_log" not in state: state["audit_log"] = []
    
    gemini_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    if not gemini_key: return state

    client = genai.Client(api_key=gemini_key)
    
    for scene in state.get("scenes", []):
        scene_id = scene.get('id', 'unknown')
        image_path = scene.get("image_path")
        if not image_path or not os.path.exists(image_path): continue
            
        # IDEMPOTENCY
        if scene.get("motion_prompt") and scene["motion_prompt"] != DEFAULT_MOTION_PROMPT: continue
            
        motion_desc = None
        # MODULAR: Using MOTION_PROMPT from src.prompts
        shot_type = scene.get("shot_type", "Close-up")
        prompt = MOTION_PROMPT.format(
            IMAGE_DESCRIPTION=f"An Indian professional in a {shot_type} shot.",
            NARRATION=str(scene.get("narration", ""))
        )
        # ADDED STRICT RULE: Locked Camera for Talking Heads
        prompt += "\nSTRICT RULE: The camera must remain COMPLETELY STATIONARY. No zooming in, no zooming out, no dolly, no panning. The frame must be locked. Only the subject's mouth, jaw, lips, and eyes should move to sync with the narration."


        success = False
        last_trace = ""
        print(f"   🎬 [Motion] Analyzing Image & Narration for Scene {scene_id}...")
        
        # CHAIN: Gemini 3.1 (Default) -> Gemma 4 -> Gemini 2.0
        for model_id in ["gemini-3.1-flash-lite-preview", "gemma-4-31b-it", "gemma-4-26b-a4b-it", "gemini-2.0-flash"]:
            try:
                print(f"      🔍 Attempting {model_id}...")
                response = client.models.generate_content(
                    model=model_id,
                    contents=[prompt, PIL.Image.open(image_path)]
                )
                motion_desc = response.text.strip()
                
                # CRITICAL: Save the motion prompt so the Video Node can use it!
                scene["motion_prompt"] = motion_desc
                
                print(f"      ✅ Motion Plan Ready: {motion_desc[:100]}...")

                state["audit_log"].append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "node": f"Motion Analyst: Scene {scene_id}",
                    "status": "Success",
                    "model": model_id,
                    "details": f"Motion Spec: {motion_desc[:200]}"
                })
                success = True
                break

            except Exception as e:
                last_trace = traceback.format_exc()
                print(f"⚠️ Model {model_id} failed. \n[ERROR]: {e}\n[TRACE]: {last_trace[:400]}...") # Printing first 400 chars of trace for each chain failure
                time.sleep(1)


        if not success:
            motion_desc = DEFAULT_MOTION_PROMPT
            state["audit_log"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "node": f"Motion Analyst: Scene {scene_id}",
                "status": "Failed",
                "model": "All Chain Failed",
                "details": "Using global default prompt.",
                "trace": last_trace
            })

        scene["motion_prompt"] = motion_desc
        time.sleep(1.2)

    return state
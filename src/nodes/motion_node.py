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
    """Gemma 4 Vision Node with LOUD developer tracing for all fallbacks."""
    print(f"--- [Node: Motion Analyst (Dev Clear-Trace Mode)] ---")
    if "audit_log" not in state: state["audit_log"] = []
    
    gemini_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    if not gemini_key: return state

    client = genai.Client(api_key=gemini_key)
    
    for scene in state.get("scenes", []):
        scene_id = scene.get('id', 'unknown')
        image_path = scene.get("image_path")
        if not image_path or not os.path.exists(image_path): continue
            
        # --- IDEMPOTENCY CHECK ---
        if scene.get("motion_prompt") and scene["motion_prompt"] != DEFAULT_MOTION_PROMPT: continue
            
        motion_desc = None
        scene_narration = str(scene.get("narration", ""))
        shot_type = scene.get("shot_type", "Close-up")
        
        prompt = MOTION_PROMPT.format(
            IMAGE_DESCRIPTION=f"An Indian professional in a {shot_type} shot.",
            NARRATION=scene_narration
        )

        success = False
        last_trace = ""
        # --- CHAIN: GEMMA 4 31B -> GEMMA 4 26B -> GEMINI 3.1 ---
        for model_id in ["gemma-4-31b-it", "gemma-4-26b-a4b-it", "gemini-3.1-flash-lite-preview"]:
            try:
                print(f"🔍 [ATTEMPT] Analyzing Scene {scene_id} with {model_id}...")
                response = client.models.generate_content(
                    model=model_id,
                    contents=[prompt, PIL.Image.open(image_path)]
                )
                motion_desc = response.text.strip()
                state["audit_log"].append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "node": f"Motion Analyst: Scene {scene_id}",
                    "status": "Success",
                    "model": model_id,
                    "details": f"Vision Result: {motion_desc[:120]}..."
                })
                success = True
                print(f"✅ {model_id} Success!")
                break
            except Exception as e:
                last_trace = traceback.format_exc()
                # LOUD PRINTING: We now print every single failure immediately
                print(f"❌ [DEV TRACE] {model_id} FAILED for Scene {scene_id}:\n{last_trace}")
                time.sleep(1) # Extra cooling after a failure

        if not success:
            motion_desc = DEFAULT_MOTION_PROMPT
            state["audit_log"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "node": f"Motion Analyst: Scene {scene_id}",
                "status": "Critical Failure",
                "model": "All Models Failed",
                "details": "Using global default prompt.",
                "trace": last_trace
            })

        scene["motion_prompt"] = motion_desc
        time.sleep(1.5)

    return state
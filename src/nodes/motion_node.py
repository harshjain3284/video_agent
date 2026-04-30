import os
import PIL.Image
import traceback
import time
from datetime import datetime
from google import genai
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, MODEL_REGISTRY
from src.prompts import MOTION_PROMPT, DEFAULT_MOTION_PROMPT

def _analyze_single_motion(client, scene: dict, model_id: str) -> str:
    """Helper to perform the visual motion analysis using a specific model."""
    image_path = scene.get("image_path")
    if not image_path or not os.path.exists(image_path): return ""
    
    shot_type = scene.get("shot_type", "Close-up")
    prompt = MOTION_PROMPT.format(
        IMAGE_DESCRIPTION=f"An Indian professional in a {shot_type} shot.",
        NARRATION=str(scene.get("narration", ""))
    )
    
    # EXTRA LOCK: Ensuring the motion model respects the Stationary Camera rule
    prompt += "\nSTRICT RULE: The camera is LOCKED and STATIONARY. Only animate the subject's face/lips."

    response = client.models.generate_content(
        model=model_id,
        contents=[prompt, PIL.Image.open(image_path)]
    )
    return response.text.strip()

def motion_analyst_node(state: AgentState) -> AgentState:
    """
    ELITE MOTION ANALYST
    Analyzes the Expert's image and narration to create a precise motion plan for Veo.
    """
    print(f"--- [Node: Motion Analyst (Modular)] ---")
    api_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    if not api_key: return state

    client = genai.Client(api_key=api_key)
    
    for scene in state.get("scenes", []):
        scene_id = scene.get('id', 'temp')
        
        # Skip if already analyzed
        if scene.get("motion_prompt") and scene["motion_prompt"] != DEFAULT_MOTION_PROMPT: 
            continue
            
        print(f"   [Motion] Planning performance for Scene {scene_id}...")
        
        # Robust Chain: Try registry-defined models
        success = False
        chain = [MODEL_REGISTRY["identity_anchor"], MODEL_REGISTRY["quality_inspector"]]
        
        for model in chain:
            try:
                plan = _analyze_single_motion(client, scene, model)
                if plan:
                    scene["motion_prompt"] = plan
                    success = True
                    # LOG SUCCESS
                    state["audit_log"].append({
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "node": f"Motion Analyst: Scene {scene_id}",
                        "status": "Success",
                        "model": model,
                        "details": f"Motion Plan: {plan[:200]}..."
                    })
                    break
            except Exception as e:
                import traceback
                print(f"      [CRITICAL DIAGNOSTIC] Model {model} failed!")
                traceback.print_exc()
                time.sleep(1)

        if not success:
            print(f"      [WARNING] Using default motion for Scene {scene_id}")
            scene["motion_prompt"] = DEFAULT_MOTION_PROMPT
            
        time.sleep(1)

    return state
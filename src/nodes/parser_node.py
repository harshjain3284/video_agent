import json
import os
import time
import traceback
from datetime import datetime
from groq import Groq
from src.state.agent_state import AgentState
from src.config import GROQ_API_KEY, MODEL_REGISTRY
from src.prompts import ELITE_DIRECTOR_PROMPT

def _clean_json_extraction(text: str) -> str:
    """Surgically extracts JSON from a raw string response."""
    try:
        start_idx = min(text.find('['), text.find('{')) if '[' in text and '{' in text else (text.find('[') if '[' in text else text.find('{'))
        end_idx = max(text.rfind(']'), text.rfind('}')) if ']' in text and '}' in text else (text.rfind(']') if ']' in text else text.rfind('}'))
        if start_idx != -1 and end_idx != -1:
            return text[start_idx:end_idx+1]
    except:
        pass
    return text

def _call_director_ai(client: Groq, prompt: str) -> str:
    """Handles the robust communication with the Llama Director."""
    for i in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL_REGISTRY["elite_director"],
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return resp.choices[0].message.content
        except Exception as e:
            if i == 2: raise e
            time.sleep(2)
    return ""

def parser_node(state: AgentState) -> AgentState:
    """
    ELITE DIRECTOR NODE
    Consolidates Scripting, Character Design, and Shot Architecture into one intelligent call.
    """
    print(f"--- [Node: Elite Director (Modular)] ---")
    
    # 1. API Security Check
    api_key = GROQ_API_KEY.strip(' "\'') if GROQ_API_KEY else None
    if not api_key:
        state["error"] = "Missing Groq API Key"
        return state

    client = Groq(api_key=api_key)
    
    # 2. Build the Production Context
    selected_lang = state.get("voice_language", "Hindi (India)")
    if "Hindi" in selected_lang:
        # For India, we prefer natural Hinglish (Hindi + English terms) in Devanagari
        script_lang = "Natural Corporate Hinglish (Delhi/Mumbai style) using Devanagari script for Hindi words"
    else:
        script_lang = "Professional English (US/International style)"

    prompt = ELITE_DIRECTOR_PROMPT.format(
        INPUT_TEXT=state.get('input_text', "General Consulting"),
        CATEGORY=state.get("category", "Consulting"),
        POST_TYPE=state.get("post_type", "Authority"),
        TOTAL_DURATION=str(state.get("total_duration", 20)),
        LANGUAGE=script_lang
    )

    try:
        # 3. AI Manifest Generation
        print("   Director is calculating production manifest...")
        raw_response = _call_director_ai(client, prompt)
        clean_json = _clean_json_extraction(raw_response)
        data = json.loads(clean_json)

        # 4. Extract Global State
        char_desc = data.get("character_description", "A professional Consultease expert.")
        if isinstance(char_desc, dict):
            char_desc = ". ".join([f"{k}: {v}" for k, v in char_desc.items()])
        state["character_description"] = str(char_desc)
        
        state["script"] = data.get("script_summary", "")
        shots = data.get("shots", [])

        # 5. HARD MATH SAFEGUARD: Enforce total_duration strictly
        target_total = float(state.get("total_duration", 20))
        cumulative_duration = 0
        final_shots = []
        
        for shot in shots:
            shot_dur = float(shot.get("duration", 4.0))
            if cumulative_duration + shot_dur > target_total + 1: # Allow 1s margin
                print(f"   [Math Guard] Truncating shots to fit {target_total}s limit.")
                break
            
            # Enrich Shot Data
            if state["character_description"] not in shot["visual_prompt"]:
                 shot["visual_prompt"] = f"{state['character_description']}. {shot['visual_prompt']}"
            shot["image_path"] = None 
            
            final_shots.append(shot)
            cumulative_duration += shot_dur

        state["scenes"] = final_shots
        print(f"   [OK] Production Manifest Ready: {len(final_shots)} scenes ({cumulative_duration}s).")
        
        # Log Success
        if "audit_log" not in state: state["audit_log"] = []
        state["audit_log"].append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "node": "Director", "status": "Success", "model": MODEL_REGISTRY["elite_director"],
            "details": f"Generated {len(shots)} synchronized scenes."
        })

    except Exception as e:
        trace = traceback.format_exc()
        print(f" [CRITICAL ERROR] Director Node:\n{trace}")
        state["error"] = str(e)
    
    return state

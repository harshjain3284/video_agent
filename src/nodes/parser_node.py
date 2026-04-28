import json
import os
import re
import time
import traceback
from datetime import datetime
from groq import Groq
from src.state.agent_state import AgentState
from src.config import GROQ_API_KEY, DEFAULT_VOICE_LANGUAGE, VOICE_LANGUAGES, MODEL_REGISTRY
from src.prompts import SCRIPTWRITER_PROMPT, CHARACTER_PROMPT, SHOT_PARSER_PROMPT

def clean_json_response(text: str) -> str:
    """Extracts JSON from string."""
    try:
        start_idx = min(text.find('['), text.find('{')) if '[' in text and '{' in text else (text.find('[') if '[' in text else text.find('{'))
        end_idx = max(text.rfind(']'), text.rfind('}')) if ']' in text and '}' in text else (text.rfind(']') if ']' in text else text.rfind('}'))
        if start_idx != -1 and end_idx != -1:
            return text[start_idx:end_idx+1]
    except:
        pass
    return text

def call_groq_with_retry(client, model, messages, retries=3, delay=2, json_mode=False):
    """Robust Groq wrapper."""
    for i in range(retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"} if json_mode else None
            )
        except Exception as e:
            if i == retries - 1: raise e
            print(f"   Groq Attempt {i+1} failed ({e}). Retrying in {delay}s...")
            time.sleep(delay)

def parser_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Narrative Architect (Modular Mode)] ---")
    api_key = GROQ_API_KEY.strip(' "\'') if GROQ_API_KEY else None
    if not api_key: return state

    client = Groq(api_key=api_key)
    
    def _log_audit(stage, status, model, details, trace=None):
        if "audit_log" not in state: state["audit_log"] = []
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"), "node": f"Narrative: {stage}",
            "status": status, "model": model, "details": details
        }
        if trace: entry["trace"] = trace
        state["audit_log"].append(entry)

    # STAGE 1: SCRIPTWRITER
    print("   Stage 1: Scriptwright...")
    script_prompt = SCRIPTWRITER_PROMPT.format(
        INPUT_TEXT=state['input_text'] or "General Consulting",
        CATEGORY=state.get("category", "Consulting"),
        POST_TYPE=state.get("post_type", "Authority"),
        VOICE_LANGUAGE=state.get("voice_language", "Hindi (India)"),
        TOTAL_DURATION=str(state.get("total_duration", 20))
    )

    try:
        script_resp = call_groq_with_retry(client, MODEL_REGISTRY["script_writer"], [{"role": "user", "content": script_prompt}])
        state["script"] = script_resp.choices[0].message.content.strip()
        print(f"   Script Generated (Hinglish): {state['script'][:200]}...")
        _log_audit("Scriptwriter", "Success", "Llama-3.3-70b", f"Script: {state['script']}")
    except Exception as e:
        trace = traceback.format_exc(); print(f"[DEV ERROR] Scriptwriter:\n{trace}")
        _log_audit("Scriptwriter", "Failed", "Llama-3.3-70b", str(e), trace=trace)
        state["script"] = state['input_text'] or "Welcome."

    # STAGE 2: CHARACTER
    print("   Stage 2: Character...")
    char_prompt = CHARACTER_PROMPT.format(
        CATEGORY=state.get("category", "Consulting"),
        INPUT_TEXT=state['input_text'] or ""
    )
    
    try:
        char_resp = call_groq_with_retry(client, MODEL_REGISTRY["character_designer"], [{"role": "user", "content": char_prompt}])
        state["character_description"] = char_resp.choices[0].message.content.strip()
        print(f"   Visual Persona Ready: {state['character_description'][:100]}...")
        _log_audit("Character", "Success", "Llama-3.1-8b", f"Character: {state['character_description']}")

    except Exception as e:
        trace = traceback.format_exc(); print(f"[DEV ERROR] Character Gen:\n{trace}")
        _log_audit("Character", "Failed", "Llama-3.1-8b", str(e), trace=trace)
        state["character_description"] = "A professional consultant."


    # STAGE 3: SHOT ARCHITECT
    print("   Stage 3: Shot Architect...")
    shot_prompt = SHOT_PARSER_PROMPT.format(
        CHARACTER_DESC=state["character_description"],
        SCRIPT=state["script"],
        TOTAL_DURATION=str(state.get("total_duration", 20))
    )
    
    try:
        shot_resp = call_groq_with_retry(client, MODEL_REGISTRY["shot_architect"], [{"role": "user", "content": shot_prompt}], json_mode=True)
        response_content = clean_json_response(shot_resp.choices[0].message.content)
        _log_audit("Shot Architect", "Success", "Llama-3.3-70b", f"JSON: {response_content}")

        data = json.loads(response_content)
        
        shots = data.get("shots", []) if isinstance(data, dict) else []
        if not shots: raise ValueError("No shots parsed.")

        for shot in shots:
            shot["visual_prompt"] = f"{state['character_description']}. {shot.get('visual_prompt', '')}"
            if "image_path" not in shot: shot["image_path"] = None

        state["scenes"] = shots
        print(f"   Successfully paced {len(shots)} shots.")
    except Exception as e:
        trace = traceback.format_exc(); _log_audit("Shot Architect", "Failed", "Llama-3.3-70b", str(e), trace=trace)
        state["error"] = f"Parser failure: {str(e)}"
    
    return state

import json
import os
import re
import time
import traceback
from datetime import datetime
from groq import Groq
from src.state.agent_state import AgentState
from src.config import GROQ_API_KEY, DEFAULT_VOICE_LANGUAGE, VOICE_LANGUAGES
from src.prompts import SCRIPTWRITER_PROMPT, CHARACTER_PROMPT, SHOT_PARSER_PROMPT

def clean_json_response(text: str) -> str:
    """Extracts JSON from a string that might contain conversational filler."""
    try:
        start_idx = min(text.find('['), text.find('{')) if '[' in text and '{' in text else (text.find('[') if '[' in text else text.find('{'))
        end_idx = max(text.rfind(']'), text.rfind('}')) if ']' in text and '}' in text else (text.rfind(']') if ']' in text else text.rfind('}'))
        if start_idx != -1 and end_idx != -1:
            return text[start_idx:end_idx+1]
    except:
        pass
    return text

def call_groq_with_retry(client, model, messages, retries=3, delay=2, json_mode=False):
    """Robust Groq wrapper with automatic retries for connection issues."""
    for i in range(retries):
        try:
            return client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"} if json_mode else None
            )
        except Exception as e:
            if i == retries - 1: raise e
            print(f"   ⚠️ Groq Attempt {i+1} failed ({e}). Retrying in {delay}s...")
            time.sleep(delay)

def parser_node(state: AgentState) -> AgentState:
    print(f"--- [Node: The Multi-Stage Narrative Architect (Dev Audit)] ---")
    api_key = GROQ_API_KEY.strip(' "\'') if GROQ_API_KEY else None
    
    if not api_key:
        state["error"] = "Missing GROQ_API_KEY"
        return state

    client = Groq(api_key=api_key)
    
    def _log_audit(stage, status, model, details, trace=None):
        if "audit_log" not in state: state["audit_log"] = []
        entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "node": f"Narrative Architect: {stage}",
            "status": status,
            "model": model,
            "details": details
        }
        if trace: entry["trace"] = trace
        state["audit_log"].append(entry)

    # ─── STAGE 1: THE SCRIPTWRITER ───
    print("   ✍️  Stage 1: Writing Creative Script...")
    script_prompt = SCRIPTWRITER_PROMPT.replace("{INPUT_TEXT}", state['input_text'] or "General Consulting")
    script_prompt = script_prompt.replace("{CATEGORY}", state.get("category", "Consulting"))
    script_prompt = script_prompt.replace("{POST_TYPE}", state.get("post_type", "Authority"))
    script_prompt = script_prompt.replace("{HOOK_TYPE}", state.get("hook_type", "Pain"))
    script_prompt = script_prompt.replace("{VOICE_LANGUAGE}", state.get("voice_language", "English"))
    script_prompt = script_prompt.replace("{TOTAL_DURATION}", str(state.get("total_duration", 20)))
    
    try:
        script_resp = call_groq_with_retry(client, "llama-3.3-70b-versatile", [{"role": "user", "content": script_prompt}])
        state["script"] = script_resp.choices[0].message.content.strip()
        _log_audit("Scriptwriter", "Success", "Llama-3.3-70b", state["script"])
    except Exception as e:
        trace = traceback.format_exc()
        print(f"❌ [DEV ERROR] Scriptwriter:\n{trace}")
        _log_audit("Scriptwriter", "Failed", "Llama-3.3-70b", str(e), trace=trace)
        state["script"] = state['input_text'] or "Welcome to our professional services."

    # ─── STAGE 2: CHARACTER CONSISTENCY ───
    print("   👤 Stage 2: Designing Character Profile...")
    char_prompt = CHARACTER_PROMPT.replace("{CATEGORY}", state.get("category", "Consulting"))
    char_prompt = char_prompt.replace("{INPUT_TEXT}", state['input_text'] or "")
    
    try:
        char_resp = call_groq_with_retry(client, "llama-3.1-8b-instant", [{"role": "user", "content": char_prompt}])
        state["character_description"] = char_resp.choices[0].message.content.strip()
        _log_audit("Character Designer", "Success", "Llama-3.1-8b", state["character_description"])
    except Exception as e:
        trace = traceback.format_exc()
        print(f"❌ [DEV ERROR] Character Designer:\n{trace}")
        _log_audit("Character Designer", "Failed", "Llama-3.1-8b", str(e), trace=trace)
        state["character_description"] = "A professional consultant in a modern office."

    # ─── STAGE 3: THE SHOT ARCHITECT ───
    print("   🎬 Stage 3: Breaking into Dynamic Shots...")
    shot_prompt = SHOT_PARSER_PROMPT.replace("{CHARACTER_DESC}", state["character_description"])
    shot_prompt = shot_prompt.replace("{SCRIPT}", state["script"])
    shot_prompt = shot_prompt.replace("{TOTAL_DURATION}", str(state.get("total_duration", 20)))
    
    try:
        shot_resp = call_groq_with_retry(client, "llama-3.3-70b-versatile", [{"role": "user", "content": shot_prompt}], json_mode=True)
        response_content = clean_json_response(shot_resp.choices[0].message.content)
        _log_audit("Shot Architect", "Success", "Llama-3.3-70b", response_content)
        data = json.loads(response_content)
        
        shots = []
        if isinstance(data, dict):
            if "shots" in data: shots = data["shots"]
            else:
                for val in data.values():
                    if isinstance(val, list): shots = val; break
        
        if not shots: raise ValueError("No shots parsed.")

        for shot in shots:
            if "visual_prompt" in shot:
                char_key = state["character_description"][:15].lower()
                if char_key not in shot["visual_prompt"].lower():
                    shot["visual_prompt"] = f"{state['character_description']}. {shot['visual_prompt']}"
            if "image_path" not in shot: shot["image_path"] = None

        state["scenes"] = shots
        print(f"   🎞️ Successfully paced {len(shots)} shots.")
        
    except Exception as e:
        trace = traceback.format_exc()
        print(f"❌ [DEV ERROR] Shot Architect:\n{trace}")
        _log_audit("Shot Architect", "Failed", "Llama-3.3-70b", str(e), trace=trace)
        state["error"] = f"Failed to broke script into shots: {str(e)}"
    
    return state

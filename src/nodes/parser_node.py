import json
import os
from groq import Groq
from src.state.agent_state import AgentState
from src.config import GROQ_API_KEY

def parser_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Parser (Scriptwriter)] ---")
    session_id = state["session_id"]
    api_key = GROQ_API_KEY.strip(' "\'') if GROQ_API_KEY else None
    # Initialize cost tracking at the start of the project
    state["usage_stats"] = []
    state["total_cost"] = 0.0
    
    input_text = state["input_text"]
    uploaded_image_path = state.get("uploaded_image_path")
    
    # ─── SHORTCUT: If user uploaded an image, skip complex parsing ───
    if uploaded_image_path and os.path.exists(uploaded_image_path):
        print(f"   🚀 [Shortcut] Image detected! Skipping multi-scene breakdown.")
        state["scenes"] = [{
            "id": 1,
            "visual_prompt": "Using uploaded image", # Not used but kept for safety
            "motion_prompt": f"Based on user text: {input_text}",
            "voiceover": input_text[:500], # Use text as narration
            "duration": state.get("scene_duration", 4),
            "image_path": uploaded_image_path # Inject image now
        }]
        state["scene_count"] = 1
        return state

    if not api_key:
        print("   ❌ Error: GROQ_API_KEY missing.")
        state["error"] = "Missing GROQ_API_KEY"
        return state

    client = Groq(api_key=api_key)
    
    # Calculate target words per scene based on total duration
    per_scene_duration = state.get('scene_duration', 4)
    # Avg speech rate is ~2.2 words per second
    target_words = round(per_scene_duration * 2.2)
    
    # Using simple .replace() to avoid curly brace errors with .format()
    prompt = """
    Analyze the following text and break it down into EXACTLY {SCENE_COUNT} distinct visual scenes.
    
    CRITICAL INSTRUCTION: You MUST return EXACTLY {SCENE_COUNT} scenes. 
    If the text is short, create more detailed visual steps or break sentences into separate visual moments to reach exactly {SCENE_COUNT}. 
    Failure to provide exactly {SCENE_COUNT} scenes will break the system.

    Each scene MUST be EXACTLY {SCENE_DURATION} seconds long.

    For each scene, provide:
    1. A short description of the scene.
    2. A DETAILED visual prompt for an image generator. (Include: "Photorealistic, 8k, highly detailed, cinematic lighting, shot on 35mm lens, realistic textures").
    3. The narration text.
    4. "duration": Must be EXACTLY {SCENE_DURATION}.
    
    Text: "{INPUT_TEXT}"
    
    Return ONLY a JSON list of objects with the keys: "id", "description", "visual_prompt", "narration", "duration".
    Example: [{"id": 1, "description": "...", "visual_prompt": "...", "narration": "...", "duration": 4.5}]
    """
    
    prompt = prompt.replace("{SCENE_COUNT}", str(state['scene_count']))
    prompt = prompt.replace("{SCENE_DURATION}", str(per_scene_duration))
    prompt = prompt.replace("{TOTAL_DURATION}", str(state['total_duration']))
    prompt = prompt.replace("{INPUT_TEXT}", state['input_text'])


    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        response_content = completion.choices[0].message.content
        data = json.loads(response_content)
        
        # Extract the list from the JSON response safely
        scenes = []
        if isinstance(data, dict):
            if "scenes" in data and isinstance(data["scenes"], list):
                scenes = data["scenes"]
            else:
                # Try to find any list in the dictionary values
                for val in data.values():
                    if isinstance(val, list):
                        scenes = val
                        break
        elif isinstance(data, list):
            scenes = data

        # CRITICAL SAFETY check: If after all that, scenes is STILL not a list, 
        # force it to be an empty list so it doesn't crash the next steps.
        if not isinstance(scenes, list):
            scenes = []

        # Ensure consistency
        for scene in scenes:
            if "image_path" not in scene:
                scene["image_path"] = None

        state["scenes"] = scenes
        print(f"Successfully parsed {len(scenes)} scenes using Groq.")
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        state["error"] = f"Failed to parse scenes: {str(e)}"
    
    return state

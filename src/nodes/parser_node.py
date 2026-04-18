import json
from groq import Groq
from src.state.agent_state import AgentState
from src.config import GROQ_API_KEY

def parser_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Parser (using Groq)] ---")
    
    if not GROQ_API_KEY:
        state["error"] = "GROQ_API_KEY not found in environment."
        return state

    client = Groq(api_key=GROQ_API_KEY)
    
    # Calculate target words per scene based on total duration
    per_scene_duration = state['total_duration'] / state['scene_count']
    # Avg speech rate is ~2.2 words per second
    target_words = round(per_scene_duration * 2.2)
    
    # Using simple .replace() to avoid curly brace errors with .format()
    prompt = """
    Analyze the following text and break it down into EXACTLY {SCENE_COUNT} distinct visual scenes for a short video.
    The TOTAL video must be EXACTLY {TOTAL_DURATION} seconds long.
    
    CRITICAL: You must assign a "duration" in seconds to EACH scene based on how long it takes to narrate and the visual importance.
    The SUM of all "duration" values MUST EQUAL {TOTAL_DURATION}.
    
    For each scene, provide:
    1. A short description of the scene.
    2. A DETAILED visual prompt for an image generator. (Include: "Photorealistic, 8k, highly detailed, cinematic lighting, shot on 35mm lens, realistic textures").
    3. The narration text.
    4. "duration": How many seconds this scene should last (e.g., 3.5).
    
    Text: "{INPUT_TEXT}"
    
    Return ONLY a JSON list of objects with the keys: "id", "description", "visual_prompt", "narration", "duration".
    Example: [{"id": 1, "description": "...", "visual_prompt": "...", "narration": "...", "duration": 4.5}]
    """
    
    prompt = prompt.replace("{SCENE_COUNT}", str(state['scene_count']))
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
        
        # Extract the list from the JSON response
        if isinstance(data, dict):
            if "scenes" in data:
                scenes = data["scenes"]
            else:
                scenes = list(data.values())[0] if data else []
        elif isinstance(data, list):
            scenes = data
        else:
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

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
    The total video must be {TOTAL_DURATION} seconds long.
    
    CRITICAL: For EACH scene, write a "narration" that is APPROXIMATELY {TARGET_WORDS} words long. 
    This is necessary so the voiceover fits into {PER_SCENE_DUR} seconds per scene.
    
    For each scene, provide:
    1. A short description of the scene.
    2. A detailed visual prompt for an image generator (Stable Diffusion).
    3. The narration text.
    
    Text: "{INPUT_TEXT}"
    
    Return ONLY a JSON list of objects with the keys: "id", "description", "visual_prompt", "narration".
    Example: [{"id": 1, "description": "...", "visual_prompt": "...", "narration": "..."}]
    """
    
    prompt = prompt.replace("{SCENE_COUNT}", str(state['scene_count']))
    prompt = prompt.replace("{TOTAL_DURATION}", str(state['total_duration']))
    prompt = prompt.replace("{TARGET_WORDS}", str(target_words))
    prompt = prompt.replace("{PER_SCENE_DUR}", str(round(per_scene_duration, 1)))
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

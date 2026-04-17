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
    
    # Use triple quotes for the template and replace placeholders manually 
    # to avoid f-string issues with user-provided text containing curly braces.
    prompt_template = """
    Analyze the following text and break it down into 3-5 distinct visual scenes for a short video.
    For each scene, provide:
    1. A short description of the scene.
    2. A detailed visual prompt for an image generator (Stable Diffusion).
    
    Text: "{INPUT_TEXT}"
    
    Return ONLY a JSON list of objects with the keys: "id", "description", "visual_prompt", "narration".
    Example: [{"id": 1, "description": "...", "visual_prompt": "...", "narration": "This is what the voiceover will say for this scene."}]
    """
    
    prompt = prompt_template.replace("{INPUT_TEXT}", state['input_text'])

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        response_content = completion.choices[0].message.content
        data = json.loads(response_content)
        
        # Groq might return a wrapper object, extract the list
        if isinstance(data, dict) and "scenes" in data:
            scenes = data["scenes"]
        elif isinstance(data, list):
            scenes = data
        else:
            # Fallback if the model returns a slightly different JSON structure
            scenes = list(data.values())[0] if isinstance(data, dict) else []

        # Ensure every scene has the required keys
        for scene in scenes:
            if "image_path" not in scene:
                scene["image_path"] = None

        state["scenes"] = scenes
        print(f"Successfully parsed {len(scenes)} scenes using Groq.")
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        state["error"] = f"Failed to parse scenes: {str(e)}"
    
    return state

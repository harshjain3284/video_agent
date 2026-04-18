import os
import base64
from groq import Groq
from src.state.agent_state import AgentState
from src.config import GROQ_API_KEY

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def motion_analyst_node(state: AgentState) -> AgentState:
    """Analyzes images + script to generate contextual motion prompts."""
    print(f"--- [Node: Motion Analyst] ---")
    
    client = Groq(api_key=GROQ_API_KEY)
    
    for scene in state["scenes"]:
        image_path = scene.get("image_path")
        if not image_path or not os.path.exists(image_path):
            continue
            
        base64_image = encode_image(image_path)
        
        # Analyze image + script for dynamic motion
        prompt = f"""
        Look at this generated image and the scene script: "{scene['narration']}"
        Avoid generalities. Describe specific movement based on the people/objects visible.
        Example: "The person on the left slowly waves while the background city lights flicker."
        """
        
        try:
            completion = client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                temperature=0.7,
                max_tokens=50
            )
            
            motion_desc = completion.choices[0].message.content.strip()
            scene["motion_prompt"] = motion_desc
            print(f"🎬 Motion Prompt (Scene {scene['id']}): {motion_desc}")
            
        except Exception as e:
            print(f"⚠️ Motion Analysis failed for scene {scene['id']}: {e}")
            scene["motion_prompt"] = "Gentle cinematic movement and soft camera zoom."

    return state

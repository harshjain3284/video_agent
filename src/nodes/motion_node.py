import os
import base64
import PIL.Image
from google import genai
from google.genai import types as genai_types
from groq import Groq
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, GROQ_API_KEY

def motion_analyst_node(state: AgentState) -> AgentState:
    """Uses Gemini Vision to analyze image + text for exact motion prompts."""
    print(f"--- [Node: Motion Analyst (Gemini Vision)] ---")
    
    gemini_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    groq_key = GROQ_API_KEY.strip(' "\'') if GROQ_API_KEY else None
    
    if not gemini_key and not groq_key:
        print("   ❌ Error: No API keys found for Motion Analysis.")
        return state

    gemini_client = genai.Client(api_key=gemini_key) if gemini_key else None
    groq_client = Groq(api_key=groq_key) if groq_key else None
    
    for scene in state.get("scenes", []):
        image_path = scene.get("image_path")
        if not image_path or not os.path.exists(image_path):
            continue
            
        motion_desc = None
        prompt = f"Analyze this image and this script: '{state['input_text']}'. Describe a short, cinematic 4-second motion for this scene. Focus only on movement, no intro text."

        # --- TRY GEMINI FIRST (With Fix) ---
        if gemini_client:
            try:
                # FIX: Use gemini-1.5-flash for maximum regional compatibility (404 fix)
                img = PIL.Image.open(image_path)
                response = gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=[prompt, img]
                )
                motion_desc = response.text.strip()
                print(f"🎬 Gemini Motion (Scene {scene.get('id')}): {motion_desc[:50]}...")
            except Exception as e:
                print(f"⚠️ Gemini Motion failed: {str(e)[:50]}")

        # --- TRY GROQ AS FALLBACK ---
        if not motion_desc and groq_client:
            try:
                print(f"🧠 Trying Groq Vision Fallback (Scene {scene.get('id')})...")
                from io import BytesIO
                temp_img = PIL.Image.open(image_path)
                temp_img.thumbnail((512, 512))
                buffered = BytesIO()
                temp_img.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
                
                chat_completion = groq_client.chat.completions.create(
                    messages=[{
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                        ]
                    }],
                    model="llama-3.2-11b-vision-preview",
                )
                motion_desc = chat_completion.choices[0].message.content.strip()
                print(f"🎬 Groq Motion (Scene {scene.get('id')}): {motion_desc[:50]}...")
            except Exception as e:
                print(f"⚠️ Groq Motion failed: {str(e)[:50]}")

        # --- FINAL FALLBACK ---
        scene["motion_prompt"] = motion_desc or "Cinematic movement, slow zoom, high quality motion."

    return state

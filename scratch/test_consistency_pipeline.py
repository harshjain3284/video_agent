import os
import json
from src.nodes.parser_node import parser_node
from src.nodes.image_node import image_node
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, GROQ_API_KEY

def run_consistency_test():
    print("STARTING CONSISTENCY PIPELINE TEST...")
    
    # 1. Setup Initial State
    # We use a 30s duration to force at least 3 unique image generations
    state = AgentState(
        input_text="A professional Indian lawyer in a modern Delhi office explaining the benefits of GST for small businesses.",
        session_id=f"test_consistency_{int(os.time.time())}" if hasattr(os, 'time') else "test_consistency_v1",
        total_duration=30,
        category="GST",
        post_type="Authority",
        aspect_ratio="16:9",
        model_id="gemini-3.1-flash-image-preview" # Using our standard model
    )
    
    # Ensure session id is a string
    import time
    state["session_id"] = f"test_{int(time.time())}"

    # 2. RUN PARSER (The Brain)
    print("\nSTEP 1: Running Narrative Architect (Parser)...")
    state = parser_node(state)
    
    if not state.get("scenes"):
        print("Error: Parser failed to generate scenes.")
        return

    print(f"Parser complete. Planned {len(state['scenes'])} shots.")
    print(f"Character DNA: {state.get('character_description', 'None')[:100]}...")

    # 3. RUN IMAGE GENERATOR (The Artist)
    # This will now use our new Visual Referencing logic!
    print("\nSTEP 2: Running Image Generator with Visual Referencing...")
    state = image_node(state)

    # 4. RESULTS
    print("\nTEST COMPLETE. Checking consistency results:")
    unique_images = set()
    for i, scene in enumerate(state["scenes"]):
        img_path = scene.get("image_path")
        if img_path:
            unique_images.add(img_path)
            print(f"Shot {i+1} ({scene.get('shot_type')}): {os.path.basename(img_path)}")
    
    print(f"\nSUMMARY:")
    print(f"Total Shots: {len(state['scenes'])}")
    print(f"Unique Images Created: {len(unique_images)}")
    print(f"Folder: {state['session_id']}")
    print("\nCHECK YOUR ASSETS FOLDER to verify the face, clothes, and background are identical!")

if __name__ == "__main__":
    if not GEMINI_API_KEY or not GROQ_API_KEY:
        print("❌ ERROR: Missing API Keys in .env file.")
    else:
        run_consistency_test()

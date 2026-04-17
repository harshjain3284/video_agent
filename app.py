import streamlit as st
import os
import uuid
import time
from datetime import datetime

# --- UI Setup (Must be first) ---
st.set_page_config(page_title="Cinematic AI Video Agent", layout="wide", page_icon="🎬")

# Import singleton AFTER page config
from src.workflow import agent_workflow
from src.config import ASPECT_RATIOS, ASSETS_DIR, IMAGE_MODELS, DEFAULT_MODEL
from src.utils.ui_utils import apply_custom_styles, display_scene_grid

apply_custom_styles()

st.title("🎬 Multi-Agent Video Production")

# --- Control Panel ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Model Selection
    selected_model_name = st.selectbox("Image Model", list(IMAGE_MODELS.keys()), index=0)
    selected_model_id = IMAGE_MODELS[selected_model_name]
    
    st.divider()
    selected_format = st.selectbox("Format", list(ASPECT_RATIOS.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        scene_count = st.slider("Scenes", 3, 10, 5)
        enable_subs = st.checkbox("Subtitles", value=True)
    with col2:
        total_duration = st.slider("Duration (s)", 10, 60, 20)
        enable_trans = st.checkbox("Fades", value=True)

input_text = st.text_area("Your Script", placeholder="Type your story here...", height=100)

if st.button("🚀 Start Production Pipeline"):
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(os.path.join(ASSETS_DIR, session_id), exist_ok=True)
    
    res = ASPECT_RATIOS[selected_format]
    state = {
        "input_text": input_text,
        "session_id": session_id,
        "scenes": [],
        "video_path": None,
        "error": None,
        "resolution": (res["width"], res["height"]),
        "scene_count": scene_count,
        "enable_subtitles": enable_subs,
        "enable_transitions": enable_trans,
        "total_duration": total_duration,
        "model_id": selected_model_id # Pass selected model
    }

    with st.container():
        prog_bar = st.progress(0)
        status = st.status("🎬 Processing...", expanded=True)
        
        # --- EXECUTION LOOP ---
        try:
            for event in agent_workflow.app.stream(state):
                for node_name, node_state in event.items():
                    if node_name == "parser":
                        status.write("🎥 **Scriptwriter**: Analyzing script and structuring scenes...")
                        st.json(node_state.get("scenes", []))
                        prog_bar.progress(30)
                        
                    elif node_name == "assets":
                        status.write("🎨 **Studio**: Assets generated. Reviewing...")
                        display_scene_grid(node_state["scenes"])
                        prog_bar.progress(70)
                        
                    elif node_name == "processor":
                        status.write("🎬 **Director**: Final render complete!")
                        prog_bar.progress(100)
                        
                        if node_state.get("video_path"):
                            st.divider()
                            st.write("### 🚀 Final Video")
                            # Read as bytes to force local load
                            with open(node_state["video_path"], "rb") as f:
                                st.video(f.read())
                            st.download_button("📥 Download MP4", open(node_state["video_path"], "rb"), f"video_{session_id}.mp4")
            
            status.update(label="✅ Production Complete!", state="complete")
        except Exception as e:
            st.error(f"❌ Error during execution: {e}")

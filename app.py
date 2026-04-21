import streamlit as st
import os
import uuid
import time
from datetime import datetime

# --- UI Setup (Must be first) ---
st.set_page_config(page_title="Cinematic AI Video Agent", layout="wide", page_icon="🎬")

# Import singleton AFTER page config
from src.workflow import agent_workflow
from src.config import ASPECT_RATIOS, ASSETS_DIR, IMAGE_MODELS, DEFAULT_MODEL, VIDEO_MODELS
from src.utils.ui_utils import apply_custom_styles, display_scene_grid, display_production_bill

apply_custom_styles()

st.title("🎬 Multi-Agent Video Production")

# --- Control Panel ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Model Selection
    selected_model_name = st.selectbox("Image Model", list(IMAGE_MODELS.keys()), index=0)
    selected_model_id = IMAGE_MODELS[selected_model_name]
    
    selected_video_model_name = st.selectbox("Video Model", list(VIDEO_MODELS.keys()), index=0)
    selected_video_model_id = VIDEO_MODELS[selected_video_model_name]
    
    st.divider()
    selected_format = st.selectbox("Format", list(ASPECT_RATIOS.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        scene_count = st.slider("Scenes", 1, 10, 1)
        enable_subs = st.checkbox("Subtitles", value=True)
    with col2:
        scene_duration = st.selectbox("Secs per Scene", [4, 6, 8], index=0, help="Veo AI only supports 4, 6, or 8 seconds per clip.")
        enable_voice = st.checkbox("AI Voiceover", value=True)
        enable_trans = st.checkbox("Fades", value=True)
    
    total_calc_duration = scene_count * scene_duration
    st.info(f"⏱️ **Total Video Length**: {total_calc_duration} seconds")

input_text = st.text_area("Your Script", placeholder="Type your story here...", height=100)
uploaded_file = st.file_uploader("🎨 Optional: Upload a Reference Image (Skip AI Image Gen)", type=["png", "jpg", "jpeg"])

if st.button("🚀 Start Production Pipeline"):
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(ASSETS_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    uploaded_image_path = None
    if uploaded_file:
        uploaded_image_path = os.path.join(session_dir, "uploaded_ref.png")
        with open(uploaded_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    
    res = ASPECT_RATIOS[selected_format]
    state = {
        "input_text": input_text,
        "session_id": session_id,
        "scenes": [],
        "video_path": None,
        "error": None,
        "resolution": (res["width"], res["height"]),
        "aspect_ratio": selected_format,
        "scene_count": 1 if uploaded_image_path else scene_count,
        "uploaded_image_path": uploaded_image_path, # NEW
        "enable_subtitles": enable_subs,
        "enable_voiceover": enable_voice,
        "enable_transitions": enable_trans,
        "total_duration": total_calc_duration,
        "scene_duration": scene_duration,
        "model_id": selected_model_id,
        "video_model_id": selected_video_model_id
    }

    with st.container():
        prog_bar = st.progress(0)
        status = st.status("🎬 Processing...", expanded=True)
        grid_placeholder = st.empty() # Placeholder for live grid updates
        
        # --- EXECUTION LOOP ---
        try:
            for event in agent_workflow.app.stream(state):
                for node_name, node_state in event.items():
                    if node_name == "parser":
                        status.write("🎥 **Scriptwriter**: Analyzing script and structuring scenes...")
                        st.json(node_state.get("scenes", []))
                        prog_bar.progress(30)
                        
                    elif node_name == "image_generator":
                        status.write("🎨 **Studio**: Assets generated. Reviewing...")
                        with grid_placeholder:
                            display_scene_grid(node_state["scenes"])
                        prog_bar.progress(60)

                    elif node_name == "motion_analyst":
                        status.write("🧠 **AI Analyst**: Studying scenes to plan realistic motion...")
                        with grid_placeholder:
                            display_scene_grid(node_state["scenes"])
                        prog_bar.progress(75)

                    elif node_name == "video_generator":
                        status.write("🎬 **Video Gen**: Generating real AI motion segments. This takes a moment...")
                        with grid_placeholder:
                            display_scene_grid(node_state["scenes"])
                        prog_bar.progress(90)
                        
                    elif node_name == "final_editor":
                        status.write("🎞️ **Final Editor**: Render and assembly complete!")
                        prog_bar.progress(100)

                        
                        if node_state.get("video_path"):
                            st.divider()
                            col_vid, col_cost = st.columns([2, 1])
                            with col_vid:
                                st.write("### 🚀 Final Video")
                                with open(node_state["video_path"], "rb") as f:
                                    st.video(f.read())
                                st.download_button("📥 Download MP4", open(node_state["video_path"], "rb"), f"video_{session_id}.mp4")
                            
                            with col_cost:
                                # Calculate Breakdown for the Premium Bill
                                img_total = sum(s.get('image_cost', 0.0) for s in node_state.get('scenes', []))
                                vid_total = sum(s.get('video_cost', 0.0) for s in node_state.get('scenes', []))
                                total_cost = node_state.get('total_cost', 0.0)
                                
                                # Use an expander to keep the UI clean and attractive
                                with st.expander("💰 View Production Receipt", expanded=False):
                                    display_production_bill(total_cost, img_total, vid_total)
            
            status.update(label="✅ Production Complete!", state="complete")
        except Exception as e:
            st.error(f"❌ Error during execution: {e}")

import streamlit as st
import os

def apply_custom_styles():
    """Removes all complex themes and reverts to a clean, simple light interface."""
    st.markdown("""
        <style>
        /* EXTREMELY STRICT size limits for small screens */
        .stImage > img, .stVideo video, div[data-testid="stVideo"] > video { 
            max-height: 200px !important; 
            width: auto !important; 
            max-width: 100% !important;
            margin: 0 auto; 
            display: block;
            object-fit: contain;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        
        /* Simple spacing for result cards */
        .scene-card { 
            border: 1px solid #ddd; 
            padding: 10px; 
            border-radius: 8px; 
            margin-bottom: 15px; 
        }
        
        /* Ensure the main container doesn't stretch too wide */
        .main .block-container {
            max-width: 900px;
        }
        </style>
    """, unsafe_allow_html=True)

def display_scene_grid(scenes):
    """Simple grid for reviewing generated assets, including motion prompts and AI video chunks."""
    st.write("### 📹 Production Preview")
    num_scenes = len(scenes)
    cols_per_row = 3
    rows = (num_scenes + (cols_per_row - 1)) // cols_per_row
    
    for r in range(rows):
        cols = st.columns(cols_per_row)
        for c in range(cols_per_row):
            idx = r * cols_per_row + c
            if idx < num_scenes:
                scene = scenes[idx]
                with cols[c]:
                    # Scene Header
                    duration = scene.get("duration", 0)
                    st.markdown(f"**Scene {idx + 1} ({duration}s)**")

                    
                    # 1. VISUAL (Video chunk if exists, else static image)
                    if scene.get("video_path") and os.path.exists(scene["video_path"]):
                        st.info("✨ AI Motion")
                        st.video(scene["video_path"])
                    elif scene.get("image_path"):
                        st.image(scene["image_path"], width=200)

                    # Show Model Labels
                    img_model = scene.get("image_model", "Unknown")
                    mot_model = scene.get("motion_model", "Pending...")
                    st.caption(f"🖼️ Image: {img_model}")
                    st.caption(f"🧬 Motion: {mot_model}")
                    
                    # 2. AUDIO
                    if scene.get("audio_path"):
                        st.audio(scene["audio_path"], format="audio/mp3")
                    
                    # 3. MOTION PROMPT
                    if scene.get("motion_prompt"):
                        with st.expander("📝 Motion Plan"):
                            st.caption(scene["motion_prompt"])


import streamlit as st

def apply_custom_styles():
    """Removes all complex themes and reverts to a clean, simple light interface."""
    st.markdown("""
        <style>
        /* EXTREMELY STRICT size limits for small screens */
        .stImage > img, .stVideo video, div[data-testid="stVideo"] > video { 
            max-height: 300px !important; 
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
    """Simple 3-column grid for reviewing generated assets."""
    st.write("### 🎬 Asset Preview")
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
                    st.markdown(f"**Scene {idx + 1}**")
                    if scene.get("image_path"):
                        st.image(scene["image_path"], use_column_width=False)
                    if scene.get("audio_path"):
                        st.audio(scene["audio_path"], format="audio/mp3")

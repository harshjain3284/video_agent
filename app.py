import streamlit as st
import os
import uuid
import json
import time
from datetime import datetime

# --- UI Setup (Must be first) ---
st.set_page_config(page_title="Elite Cinematic AI Video Agent", layout="wide", page_icon="🎬")

from src.workflow import agent_workflow
from src.config import (
    ASPECT_RATIOS, ASSETS_DIR, IMAGE_MODELS, DEFAULT_MODEL, 
    VIDEO_MODELS, VOICE_LANGUAGES, DEFAULT_VOICE_LANGUAGE,
    STRATEGIC_CONFIGS, BRAND_STYLES
)
from src.utils.ui_utils import apply_custom_styles, display_scene_grid, display_production_bill
from src.nodes.parser_node import parser_node

apply_custom_styles()

st.title("🎬 Multi-Agent Video Production: Elite Edition")

# --- Persistent State Management ---
if "agent_state" not in st.session_state:
    st.session_state.agent_state = None
if "workflow_step" not in st.session_state:
    st.session_state.workflow_step = "idle"

# --- Control Panel ---
with st.sidebar:
    st.header("⚙️ Production Settings")
    
    selected_model_name = st.selectbox("Image Model", list(IMAGE_MODELS.keys()), index=0)
    selected_model_id = IMAGE_MODELS[selected_model_name]
    
    selected_video_model_name = st.selectbox("Video Model", list(VIDEO_MODELS.keys()), index=0)
    selected_video_model_id = VIDEO_MODELS[selected_video_model_name]
    
    st.divider()
    selected_lang = st.selectbox("Voiceover Language", list(VOICE_LANGUAGES.keys()), index=list(VOICE_LANGUAGES.keys()).index(DEFAULT_VOICE_LANGUAGE))
    selected_format = st.selectbox("Format", list(ASPECT_RATIOS.keys()))
    
    col1, col2 = st.columns(2)
    with col1:
        total_duration = st.slider("Total Video Length (Seconds)", 5, 45, 20)
        enable_subs = st.checkbox("Subtitles", value=True)
    with col2:
        st.write("") # Layout spacer
        st.write("🤖 **AI Director is ON**")
        enable_voice = st.checkbox("AI Voice", value=True)
        enable_trans = st.checkbox("Fades", value=True)

    with st.expander("📊 Content Creative Strategy", expanded=True):
        brand_page = st.selectbox("Brand / Page", list(BRAND_STYLES.keys()))
        category = st.selectbox("Category", STRATEGIC_CONFIGS["categories"])
        post_type = st.selectbox("Post Type", STRATEGIC_CONFIGS["post_types"])
        hook_type = st.selectbox("Hook Type", STRATEGIC_CONFIGS["hook_types"])
        enable_review = st.checkbox("Pause for Script Review", value=True)
    
    st.info(f"⏱️ **Target Length**: {total_duration} seconds (AI will decide the number of shots)")

# --- Stage 1: The Idea Input ---
if st.session_state.workflow_step == "idle":
    input_text = st.text_area("What's your Idea?", placeholder="e.g. Talk about why freelancers fail at GST compliance...", height=100)
    uploaded_file = st.file_uploader("🎨 Optional: Reference Image", type=["png", "jpg", "jpeg"])

    if st.button("🚀 Start Narrative Architect"):
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        res = ASPECT_RATIOS[selected_format]
        
        # Initialize State
        initial_state = {
            "input_text": input_text,
            "session_id": session_id,
            "scenes": [],
            "video_path": None,
            "error": None,
            "resolution": (res["width"], res["height"]),
            "aspect_ratio": selected_format,
            "scene_count": 6, # Fallback hint for AI
            "uploaded_image_path": None,
            "enable_subtitles": enable_subs,
            "enable_voiceover": enable_voice,
            "enable_transitions": enable_trans,
            "total_duration": total_duration,
            "scene_duration": 4.0, # Handled dynamically by AI now
            "model_id": selected_model_id,
            "video_model_id": selected_video_model_id,
            "voice_language": selected_lang,
            "brand_page": brand_page,
            "category": category,
            "post_type": post_type,
            "hook_type": hook_type,
            "audit_log": [],
            "identity_dna": None
        }

        with st.status("✍️  Narrative Architect is writing your story...") as status:
            final_state = parser_node(initial_state)
            st.session_state.agent_state = final_state
            if enable_review:
                st.session_state.workflow_step = "review"
                st.rerun()
            else:
                st.session_state.workflow_step = "generate"
                st.rerun()

# --- Stage 2: Human Review ---
elif st.session_state.workflow_step == "review":
    st.header("📝 Strategy & Script Review")
    state = st.session_state.agent_state
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("High-Impact Script")
        state["script"] = st.text_area("Narrative Script (SSML supported)", value=state.get("script", ""), height=250)
    with col_b:
        st.subheader("Visual Persona")
        state["character_description"] = st.text_area("Global Character Profile", value=state.get("character_description", ""), height=100)
        st.info("💡 Changes here will apply to all generated shots.")

    st.subheader("🎞️ Shot Breakdown")
    for i, shot in enumerate(state.get("scenes", [])):
        with st.expander(f"Shot {shot['id']}: {shot.get('shot_type', 'Action')}", expanded=False):


            c1, c2, c3 = st.columns([1, 2, 1])
            shot["narration"] = c1.text_area(f"Narration {i}", value=shot.get("narration", ""), label_visibility="collapsed")
            shot["visual_prompt"] = c2.text_area(f"Visual {i}", value=shot.get("visual_prompt", ""), label_visibility="collapsed")
            # NATIVE SYNC: Forcing 4, 6, 8s in the UI
            current_dur = float(shot.get("duration", 4.0))
            if current_dur not in [4.0, 6.0, 8.0]:
                if current_dur < 5: current_dur = 4.0
                elif current_dur < 7: current_dur = 6.0
                else: current_dur = 8.0
            shot["duration"] = c3.selectbox(f"Dur {i}", options=[4.0, 6.0, 8.0], index=[4.0, 6.0, 8.0].index(current_dur), label_visibility="collapsed")

    if st.button("🎬 Proceed to Hero Identity", type="primary"):
        st.session_state.workflow_step = "hero_approval"
        st.rerun()
    
    if st.button("⬅️ Restart"):
        st.session_state.workflow_step = "idle"
        st.rerun()

# --- Stage 2.5: Hero Identity Approval ---
elif st.session_state.workflow_step == "hero_approval":
    st.header("🖼️ Hero Identity Approval")
    state = st.session_state.agent_state
    
    from src.nodes.image_node import image_node
    
    if not state.get("identity_dna"):
        with st.status("🎨 Generating Hero Identity...") as status:
            state = image_node(state, hero_only=True)
            st.session_state.agent_state = state
            status.update(label="Hero Shot Ready!", state="complete")

    col1, col2 = st.columns([1, 2])
    with col1:
        if state["scenes"][0].get("image_path"):
            with open(state["scenes"][0]["image_path"], "rb") as f:
                st.image(f.read(), caption="Proposed Indian Professional Persona", width="stretch")
    with col2:
        st.info("📝 **Identity Visual Prompt**")
        st.write(state["scenes"][0].get("visual_prompt"))
        st.warning("⚠️ **Check for Accuracy**: Does this look like an Indian professional in a realistic office? If yes, proceed to full video generation.")
        
        if st.button("✅ Confirm Persona & Start Production", type="primary"):
            st.session_state.workflow_step = "generate"
            st.rerun()
        
        if st.button("🔄 Regenerate Hero"):
            # Clear DNA and path to force new generation
            state["identity_dna"] = None
            state["scenes"][0]["image_path"] = None
            st.session_state.agent_state = state
            st.rerun()

# --- Stage 3: Production Pipeline ---
elif st.session_state.workflow_step == "generate" or st.session_state.workflow_step == "done":
    state = st.session_state.agent_state
    
    with st.container():
        prog_bar = st.progress(30)
        status = st.status("🎬 Production in Progress...", expanded=True)
        grid_placeholder = st.empty()
        
        try:
            # We skip the 'parser' node as it's already done
            current_state = state
            
            # Manually run the rest of the graph
            # This is simpler than filtering the stream
            from src.workflow import asset_generation_node
            from src.nodes.motion_node import motion_analyst_node
            from src.nodes.video_node import video_node
            from src.nodes.inspector_node import inspector_node
            from src.nodes.editor_node import editor_node

            if st.session_state.workflow_step != "done":
                status.write("🎨 **Studio**: Generating assets...")
                current_state = asset_generation_node(current_state)
                with grid_placeholder: display_scene_grid(current_state["scenes"])
                prog_bar.progress(60)

                status.write("🧠 **AI Analyst**: Planning motion paths...")
                current_state = motion_analyst_node(current_state)
                prog_bar.progress(75)

                status.write("🎬 **Video Gen**: Rendering AI Motion (Veo 3.1)...")
                current_state = video_node(current_state)
                with grid_placeholder: display_scene_grid(current_state["scenes"])
                prog_bar.progress(85)

                status.write("🕵️ **AI Inspector**: Watching for glitches...")
                current_state = inspector_node(current_state)
                prog_bar.progress(95)

                status.write("🎞️ **Final Editor**: Compiling video & safe-zones...")
                current_state = editor_node(current_state)
                prog_bar.progress(100)
                
                st.session_state.agent_state = current_state
                st.session_state.workflow_step = "done"
                st.rerun()

            # --- DISPLAY FINAL VIDEO & PERSISTENT GRID ---
            if st.session_state.workflow_step == "done":
                status.update(label="✅ Production Complete!", state="complete")
                node_state = st.session_state.agent_state
                
                # RE-RENDER THE GRID SO IT DOES NOT DISAPPEAR
                display_scene_grid(node_state["scenes"])
                
                st.divider()
                st.write("### 🚀 Final Elite Video")
                
                # Use columns to center and constrain the vertical video
                col_left, col_mid, col_right = st.columns([1, 1.1, 1])
                
                with col_mid:
                    if node_state.get("video_path"):
                        with open(node_state["video_path"], "rb") as f:
                            # Final surgical CSS override for the result player
                            st.markdown("""
                                <style>
                                    [data-testid="stVideo"] video {
                                        max-height: 480px !important;
                                        border: 2px solid #1f77b4;
                                    }
                                </style>
                            """, unsafe_allow_html=True)
                            st.video(f.read())
                        
                        st.download_button(
                            "📥 Download MP4", 
                            open(node_state["video_path"], "rb"), 
                            f"video_{node_state['session_id']}.mp4",
                            width="stretch"
                        )
                        
                        # New: Download Production JSON
                        manifest = {
                            "session_id": node_state.get("session_id"),
                            "character_description": node_state.get("character_description"),
                            "script": node_state.get("script"),
                            "shots": node_state.get("scenes")
                        }
                        st.download_button(
                            "💾 Download JSON Manifest",
                            data=json.dumps(manifest, indent=4),
                            file_name=f"manifest_{node_state['session_id']}.json",
                            mime="application/json",
                            width="stretch"
                        )

                        st.write("---")
                        st.write("### 💰 Production Receipt")
                        img_total = sum(s.get('image_cost', 0.0) for s in node_state.get('scenes', []))
                        vid_total = sum(s.get('video_cost', 0.0) for s in node_state.get('scenes', []))
                        total_cost = node_state.get('total_cost', 0.0)
                        display_production_bill(total_cost, img_total, vid_total)
                
                if st.button("⚡ Create New Video"):
                    st.session_state.workflow_step = "idle"
                    st.rerun()

                # --- DEVELOPER AUDIT LOG ---
                if node_state.get("audit_log"):
                    with st.expander("🕵️ Developer Audit Log (Full Workflow History)"):
                        for entry in node_state["audit_log"]:
                            st.write(f"**[{entry['timestamp']}] {entry['node']}**")
                            c1, c2 = st.columns([1, 4])
                            c1.caption(f"Status: {entry['status']}")
                            c1.caption(f"Model: {entry['model']}")
                            c2.code(entry['details'], language="text")
                            
                            # DISPLAY RAW TRACE IF EXISTS
                            if "trace" in entry:
                                with st.expander("🛠️ Technical Diagnostic (Raw Traceback)"):
                                    st.code(entry["trace"], language="python")
                            st.divider()

        except Exception as e:
            import traceback
            st.error(f"❌ Error during execution: {e}")
            with st.expander("🛠️ Technical Diagnostic (Traceback)", expanded=True):
                st.code(traceback.format_exc())
            
            if st.button("⬅️ Back to Review"):
                st.session_state.workflow_step = "review"
                st.rerun()

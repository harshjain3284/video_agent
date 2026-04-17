import streamlit as st
import os
import time
from src.workflow import VideoAgentWorkflow
from src.config import ASSETS_DIR, OUTPUT_DIR

# --- UI Configuration ---
st.set_page_config(
    page_title="Agentic Studio",
    page_icon="🎬",
    layout="wide",
)

st.markdown("""
<style>
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%); }
    .node-header { color: #00f2fe; font-weight: bold; font-size: 1.2rem; margin-top: 20px; }
    .json-box { background-color: #1e1e26; border-radius: 8px; padding: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🎬 Multi-Agent Video Production")
st.write("Watch as specialized agents collaborate to build your video.")

# Model Selection
from src.config import IMAGE_MODELS
selected_model_name = st.selectbox("Select Visual Artist Model", list(IMAGE_MODELS.keys()), index=2) # Default to FLUX

input_text = st.text_area("Enter Video Script", placeholder="Type your story here...", height=100)

if st.button("🚀 Start Production Pipeline"):
    if not input_text:
        st.error("Please enter a script!")
    else:
        # Pass the selected model to the config (simple way for this app)
        import src.config
        src.config.DEFAULT_MODEL = selected_model_name
        
        agent_workflow = VideoAgentWorkflow()
        
        # Initial state
        import datetime
        session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Ensure directory exists
        session_dir = os.path.join(ASSETS_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        state = {
            "input_text": input_text,
            "session_id": session_id,
            "scenes": [],
            "video_path": None,
            "audio_path": None,
            "current_node": "parser",
            "error": None
        }

        # --- STEP 1: PARSER AGENT ---
        with st.status("🧠 **Agent 1: Script Analyst (Llama-3)**", expanded=True) as status:
            st.write("Analyzing script and breaking into scenes...")
            for event in agent_workflow.app.stream(state):
                for node_name, node_state in event.items():
                    if node_name == "parser":
                        st.write("✅ Scenes Generated!")
                        st.json(node_state["scenes"])
                        state = node_state
                        status.update(label="Script Analyst: Finished", state="complete")

        # --- STEP 2: PARALLEL ASSET GENERATION ---
        if state["scenes"]:
            st.markdown("<div class='node-header'>⚡ Parallel Asset Production (Artist + Voiceover)</div>", unsafe_allow_html=True)
            with st.status("🎨🎤 Generating images and voiceovers simultaneously...", expanded=True) as status:
                for event in agent_workflow.app.stream(state):
                    for node_name, node_state in event.items():
                        if node_name == "assets":
                            state = node_state
                            
                            # Display all results at once
                            st.write("✅ Visuals and Narration Complete!")
                            cols = st.columns(len(state["scenes"]))
                            for i, scene in enumerate(state["scenes"]):
                                with cols[i]:
                                    st.info(f"Scene {i+1}")
                                    if scene.get("image_path"):
                                        st.image(scene["image_path"], use_column_width=True)
                                    if scene.get("narration"):
                                        st.caption(f"🔊 *\"{scene['narration'][:50]}...\"*")
                            
                            status.update(label="Asset Production: Finished", state="complete")

        # --- STEP 3: PROCESSOR AGENT ---
        if not state.get("error") and state.get("scenes"):
            st.markdown("<div class='node-header'>🎬 Agent 3: Video Director (FFmpeg)</div>", unsafe_allow_html=True)
            with st.status("🎬 Adding motion, stitching and exporting...", expanded=True) as status:
                # Stream the final step
                for event in agent_workflow.app.stream(state):
                    for node_name, node_state in event.items():
                        if node_name == "processor":
                            state = node_state
                            if state.get("video_path"):
                                st.success("Video Rendering Complete!")
                                status.update(label="Video Director: Finished", state="complete")
                                
                                st.divider()
                                c1, c2 = st.columns([2, 1])
                                with c1:
                                    st.video(state["video_path"])
                                with c2:
                                    st.write("🔍 **Production Details**")
                                    st.write(f"Duration: {len(state['scenes']) * 5}s")
                                    st.write(f"Codec: libx264")
                                    with open(state["video_path"], "rb") as file:
                                        st.download_button("📥 Download Final Video", file, "video.mp4")

        if state.get("error"):
            st.error(f"Pipeline Error: {state['error']}")

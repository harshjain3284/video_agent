import streamlit as st
import os

def apply_custom_styles():
    """Removes all complex themes and reverts to a clean, simple light interface."""
    st.markdown("""
        <style>
        /* STRICT UI size limits for ALL videos and images */
        .stImage > img, .stVideo video, div[data-testid="stVideo"] > video, .stVideo { 
            max-height: 450px !important; 
            width: auto !important; 
            max-width: 100% !important;
            margin: 0 auto !important; 
            display: block !important;
            object-fit: contain !important;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
                        st.info("✨ AI Motion Ready")
                        st.video(scene["video_path"])
                    elif scene.get("image_path") and os.path.exists(scene["image_path"]):
                        st.image(scene["image_path"], width=200)
                    else:
                        st.warning("⌛ Generating Assets...")

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

def display_production_bill(total_cost, img_cost, vid_cost):
    """Displays a premium, sleek production summary with dual USD/INR currency support."""
    ex_rate = 84.0  # Current USD to INR conversion rate
    total_inr = total_cost * ex_rate
    img_inr = img_cost * ex_rate
    vid_inr = vid_cost * ex_rate

    st.markdown(f"""
        <div style="background-color: #ffffff; padding: 25px; border-radius: 12px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-top: 30px; font-family: 'Inter', sans-serif;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="margin: 0; color: #1a1a1a; font-weight: 700;">🎬 Production Summary</h3>
                <span style="background-color: #f0f4f8; color: #1f77b4; padding: 4px 12px; border-radius: 20px; font-size: 0.85em; font-weight: 600;">Statement ID: #{os.urandom(2).hex().upper()}</span>
            </div>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #f0f0f0;">
                    <td style="padding: 12px 0; color: #666;">🧠 AI Scriptwriter & Logic</td>
                    <td style="text-align: right; padding: 12px 0; font-weight: 500;">$0.00 <span style="color: #999; font-size: 0.9em; margin-left: 5px;">(₹0.00)</span></td>
                </tr>
                <tr style="border-bottom: 1px solid #f0f0f0;">
                    <td style="padding: 12px 0; color: #666;">🎨 Studio Assets (AI Images)</td>
                    <td style="text-align: right; padding: 12px 0; font-weight: 500;">${img_cost:.3f} <span style="color: #999; font-size: 0.9em; margin-left: 5px;">(₹{img_inr:.2f})</span></td>
                </tr>
                <tr style="border-bottom: 2px solid #1a1a1a;">
                    <td style="padding: 12px 0; color: #666;">🧬 Motion Effects (AI Video)</td>
                    <td style="text-align: right; padding: 12px 0; font-weight: 500;">${vid_cost:.3f} <span style="color: #999; font-size: 0.9em; margin-left: 5px;">(₹{vid_inr:.2f})</span></td>
                </tr>
                <tr style="font-weight: 800; font-size: 1.3em;">
                    <td style="padding: 20px 0; color: #1a1a1a;">TOTAL INVESTMENT</td>
                    <td style="text-align: right; padding: 20px 0; color: #1f77b4;">${total_cost:.3f} <br><span style="font-size: 0.6em; color: #1a1a1a; font-weight: 600;">(₹{total_inr:.2f} INR)</span></td>
                </tr>
            </table>
            <div style="margin-top: 15px; text-align: center;">
                <p style="color: #999; font-size: 0.8em; margin: 0;">Pricing calculated based on industry standard model rates. (1 USD ≈ ₹84 INR)</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

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
    """Premium, detailed grid for reviewing every stage of production."""
    st.write("### 🎬 Detailed Production Breakdown")
    
    for idx, scene in enumerate(scenes):
        with st.container():
            st.markdown(f"#### 🎥 Scene {idx + 1} ({scene.get('duration', 0)}s)")
            
            # Top Row: Prompts and Text
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption("📝 **Narration Script**")
                st.info(scene.get("narration", "Waiting..."))
            with c2:
                st.caption("🎨 **Visual Prompt**")
                st.info(scene.get("visual_prompt", "Waiting..."))
            with c3:
                st.caption("🧠 **Motion Plan**")
                st.success(scene.get("motion_prompt", "Waiting for analyst..."))
            
            # Middle Row: Assets
            c4, c5, c6 = st.columns(3)
            with c4:
                st.caption("🔊 **AI Voice**")
                audio_path = scene.get("audio_path")
                if audio_path and os.path.exists(audio_path):
                    with open(audio_path, "rb") as f:
                        st.audio(f.read(), format="audio/mp3")
                else:
                    st.warning("⌛ Generating Audio...")
            with c5:
                st.caption("🖼️ **AI Image**")
                img_path = scene.get("image_path")
                if img_path and os.path.exists(img_path):
                    with open(img_path, "rb") as f:
                        st.image(f.read(), use_container_width=True)
                else:
                    st.warning("⌛ Generating Image...")
            with c6:
                st.caption("🎬 **AI Motion (Veo)**")
                vid_path = scene.get("video_path")
                if vid_path and os.path.exists(vid_path):
                    with open(vid_path, "rb") as f:
                        st.video(f.read())
                else:
                    st.info("⌛ Rendering Video...")

            # Bottom Row: QC / Inspector Data
            if "trim_start" in scene or "quality_score" in scene:
                with st.expander("🕵️ Inspector Quality Report", expanded=True):
                    sc, tr = st.columns(2)
                    sc.metric("Quality Score", f"{scene.get('quality_score', 0)*100:.1f}%")
                    tr.metric("Recommended Timeline", f"{scene.get('trim_start', 0.0)}s - {scene.get('trim_end', scene.get('duration', 0.0))}s")
            
            st.divider()

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

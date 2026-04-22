# 🎬 AI Video Agent: Elite Pipeline Map

This document serves as the "Master Blueprint" for your AI Video Production Agency workflow.

---

## 🏗 Phase I: The Strategic Brain (LLM Logic)
1.  **Idea Intake (UI)**:
    *   User provides a raw **Idea** and selects **Strategic Parameters** (Category, Brand Style, Post Type, Hook Type).
2.  **Narrative Architect - Stage 1 (Scriptwriter)**:
    *   Converts the **Idea** into a high-retention, conversational, human-centric **Script**.
    *   Injects natural puncuation for realistic pacing.
3.  **Narrative Architect - Stage 2 (Character Designer)**:
    *   Generates a persistent **Global Character Profile** (Visual DNA) to ensure the person in the video looks consistent throughout.
4.  **Narrative Architect - Stage 3 (Shot Architect)**:
    *   Breaks the Script into a **Dynamic Shot List**.
    *   Assigns **Shot Types** (Extreme Close-up, Visual Metaphor, etc.).
    *   Calculates **Dynamic Durations** (1.5s - 5s) for each shot based on word count.

---

## 🛡 Phase II: The Human Checkpoint
5.  **Review Node (Human-in-the-Loop)**:
    *   The pipeline pauses. The user reviews and edits:
        *   **The Global Script**
        *   **The Visual Character Design**
        *   **Individual Shot Details** (Narration, Prompt, Duration).

---

## 🎨 Phase III: Parallel Asset Generation (Engines)
6.  **Visual Studio (Image/Imagen Node)**:
    *   Generates 1024x1024 (or vertical) `.png` assets for each shot.
    *   **Logic**: `Shot Prompt` + `Global Character DNA` + `Brand Style`.
7.  **Voice Talent (Edge-TTS Node)**:
    *   Generates neural `.mp3` voiceovers for each shot.
    *   **Logic**: Automatically cleans XML/SSML tags to ensure smooth speech.

---

## 🎥 Phase IV: Cinematography & Motion (Video APIs)
8.  **Motion Analyst (Vision Node)**:
    *   Analyzes the image + narration + shot type to plan a camera path.
    *   **Logic**: Fast motion for "Hooks," steady motion for "Authority."
9.  **Video Production (Google Veo 3.1 Node)**:
    *   Sends the image and motion prompt to the Veo API.
    *   **Smart Block Selection**: Rounds up the target duration to the nearest Veo block (4s, 6s, or 8s).

---

## 🎞 Phase V: Final Post-Production (Final Editor)
10. **Smart Trimming (Center-Cut)**:
    *   Takes the "raw" Veo clips and trims them to the **exact shot duration** (usually taking the middle portion for best motion).
11. **Captioning (Safe-Zone Aware)**:
    *   Bakes subtitles onto the video.
    *   If Format is **9:16 (Reel)**, move captions higher to avoid the Instagram/TikTok UI overlay.
12. **Audio/Video Sync**:
    *   Attaches the neural voiceover to the specific trimmed shot clip.
13. **Final Assembly**:
    *   Concatenates all shots with fades and renders the final `.mp4`.
14. **Production Receipt**:
    *   Calculates total cost based on the number of shots and video length.

---

## 🚀 Final Output
*   **Final Video Player**
*   **Interactive Bill Breakdown**
*   **One-Click Download**

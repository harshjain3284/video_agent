# 🎬 Video Agent MCP Specification (v2.0)

This document defines the architecture, rules, and operational guidelines for the **Automated Cinematic Video Agent**, strictly following the **Model Context Protocol (MCP)** standards.

## **1. Core System Concept**
The system is an autonomous multi-agent pipeline orchestrated via **LangGraph**. It transforms raw input text into a high-fidelity cinematic video by coordinating specialized sub-agents.

---

## **2. MCP Primitives**

### **A. Prompts (User-Controlled Workflows)**
These are the templates that steer the AI behavior for specific content creation tasks.

- **`narrative_breakdown`**: Directs the AI to analyze raw text and extract logical scene breaks, timing, and visual descriptions.
- **`motion_intent`**: Directs the AI to analyze static images and describe realistic movement (e.g., "slow pan across documents," "light flickering").

### **B. Tools (Model-Controlled Functions)**
These are the executable nodes and functions the agent triggers.

| Tool Name | Operation | Model |
| :--- | :--- | :--- |
| `parser_v2` | Breaks script into JSON scene structured data. | `llama-3.3-70b` |
| `native_image_gen` | Generates 16:9 or 9:16 high-fidelity images. | `gemini-3.1-flash-image` |
| `cinematic_motion` | Transforms images into 4-6s video clips via ref image. | `veo-3.1-generate-preview` |
| `video_processor` | Concatenates clips, adds subtitles and audio. | `MoviePy v2.2` |

### **C. Resources (Application-Controlled Data)**
- **`SessionState`**: The active context of the video project, including scene IDs, paths, and metadata.
- **`AssetLibrary`**: The local storage path (`/assets/{session_id}/`) containing raw images, narration audio, and motion segments.

---

## **3. Agent Operational Guidelines (MCP Rules)**

### **Rule 1: Structured Communication**
All internal data passing between nodes must adhere to the `AgentState` TypedDict. No loose strings or untracked state is permitted.

### **Rule 2: Fallback Resilience**
Every Tool must have a defined fallback path:
- If **Veo** fails (Timeout/Quota): Revert to `Cinematic Zoom (Static)`.
- If **HuggingFace** fails: Revert to `Pollinations.ai`.

### **Rule 3: Resource Integrity**
Tools must never delete assets from `AssetLibrary`. Every output must be traceable back to a `SessionID`.

### **Rule 4: Input Validation**
- Tool `native_image_gen` must validate `aspect_ratio` string matches `[16-9, 9-16, 1-1]`.
- Tool `cinematic_motion` must validate that the `image_path` exists on disk before attempting API calls.

---

## **4. Error Handling Protocol**
Following the MCP standard for error reporting:
- **Status 400**: Invalid configuration (Mime type, Duration).
- **Status 429**: Quota exceeded (HF/Google rate limits).
- **Status 503**: Service Unavailable (Gemini demand spikes).

## **5. Future MCP Roadmap**
- [ ] Implement **Surgical Character Consistency** using a "Character Reference Resource."
- [ ] Add **Voice Overlay Resource** for local TTS generation using Whisper/ElevenLabs.
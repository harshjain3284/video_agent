import os
import time
import json
import traceback
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, MODEL_REGISTRY

def _inspect_single_video(client: genai.Client, scene: dict) -> dict:
    """Uploads and analyzes a single clip for quality using Gemini 1.5 Pro."""
    video_path = scene.get("video_path")
    if not video_path or not os.path.exists(video_path): return {}

    # 1. Upload for analysis
    file_upload = client.files.upload(file=video_path)
    
    # 1.1 Wait for file to be processed (Required for Gemini Video API)
    print(f"   [Inspector] Waiting for video processing ({file_upload.name})...")
    while file_upload.state.name == "PROCESSING":
        time.sleep(2)
        file_upload = client.files.get(name=file_upload.name)
    
    if file_upload.state.name == "FAILED":
        print(f"   [Inspector] Video processing failed!")
        return {}

    video_part = genai_types.Part.from_uri(file_uri=file_upload.uri, mime_type="video/mp4")
    
    # 2. Production QC Prompt
    duration = scene.get('duration', 4.0)
    prompt = f"""
    TASK: Professional Video QC for Consultease. 
    CONTEXT: {scene.get('narration', 'Ad scene')}
    VIDEO DURATION: {duration} seconds
    
    DIRECTIONS:
    - Watch for AI artifacts (face warping, melting features, flickering).
    - Identify the 'Golden Range' (longest high-quality segment).
    - Prioritize natural lip-sync.
    
    OUTPUT: Return ONLY a JSON object:
    {{
      "quality_score": 0.0 to 1.0,
      "has_glitch": true/false,
      "trim_start": 0.0,
      "trim_end": {duration},
      "reason": "Technical observation"
    }}
    """
    
    response = client.models.generate_content(
        model=MODEL_REGISTRY["quality_inspector"],
        contents=[video_part, prompt],
        config=genai_types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)

def inspector_node(state: AgentState) -> AgentState:
    """
    ELITE QUALITY INSPECTOR
    Uses Gemini 1.5 Pro to verify each clip before final assembly.
    """
    print(f"--- [Node: Elite Quality Inspector (Modular)] ---")
    api_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    if not api_key: return state

    client = genai.Client(api_key=api_key)
    results = []
    
    for i, scene in enumerate(state.get("scenes", [])):
        scene_id = scene.get("id", i+1)
        if not scene.get("video_path"):
            results.append(scene)
            continue

        print(f"   [Inspector] Reviewing Scene {scene_id}...")
        try:
            analysis = _inspect_single_video(client, scene)
            
            # Apply Trimming Logic
            scene["trim_start"] = float(analysis.get("trim_start", 0.0))
            scene["trim_end"] = float(analysis.get("trim_end", scene.get("duration", 8.0)))
            scene["quality_report"] = analysis
            
            # LOG SUCCESS
            state["audit_log"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "node": f"Quality Inspector: Scene {scene_id}",
                "status": "Verified",
                "model": MODEL_REGISTRY["quality_inspector"],
                "details": f"Score: {analysis.get('quality_score')} | Range: {scene['trim_start']}s-{scene['trim_end']}s | {analysis.get('reason')}"
            })
            
            print(f"      [OK] Score: {analysis.get('quality_score')} | Range: {scene['trim_start']}s-{scene['trim_end']}s")
        except Exception as e:
            import traceback
            print(f"   [CRITICAL DIAGNOSTIC] Quality Inspection failed for Scene {scene_id}!")
            traceback.print_exc()
            scene["trim_start"], scene["trim_end"] = 0.0, float(scene.get("duration", 8.0))

        results.append(scene)
        time.sleep(2)

    state["scenes"] = results
    return state

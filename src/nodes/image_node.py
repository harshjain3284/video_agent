import os
import time
import random
import traceback
import PIL.Image
import math
import re
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, COSTS, BRAND_STYLES, MODEL_REGISTRY
from src.prompts import (
    DEFAULT_IMAGE_PROMPT, 
    IMAGE_PROMPT_PREFIX, 
    DNA_EXTRACTION_PROMPT
)
from src.utils.core_utils import format_aspect_ratio, ensure_session_dir, retry_with_backoff

def extract_identity_dna(image_path, api_key, audit_log):
    """Uses a Triple-Model Chain to extract the 'Visual DNA' from src.prompts."""
    if not os.path.exists(image_path): return None
    
    client = genai.Client(api_key=api_key)
    # MODULAR: Using DNA_EXTRACTION_PROMPT from src.prompts
    prompt = DNA_EXTRACTION_PROMPT
    
    models = [
        MODEL_REGISTRY["identity_anchor"], 
        MODEL_REGISTRY["identity_backup_1"], 
        MODEL_REGISTRY["identity_backup_2"]
    ]
    
    for model_id in models:
        try:
            print(f" [IDENTITY CHAIN] Attempting Extraction with {model_id}...")
            response = client.models.generate_content(
                model=model_id,
                contents=[prompt, PIL.Image.open(image_path)]
            )
            dna = response.text.strip()
            print(f" DNA Extracted successfully using {model_id}")
            audit_log.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "node": "Identity Extraction",
                "status": "Success",
                "model": model_id,
                "details": f"Production DNA Anchor created."
            })
            return dna
        except Exception as e:
            trace = traceback.format_exc()
            print(f" [WARNING] Identity Extraction failed for {model_id}. Chain continuing...\n{trace}")
            
    return None

def generate_image_asset(scene: dict, api_key: str, model_id: str, session_id: str, global_aspect_ratio: str, audit_log: list, identity_dna: str = None, reference_image_path: str = None):
    """Surgical Image Generator with Fallback Chain, DNA Anchoring, and Visual Referencing."""
    if not api_key: return None
    scene_id = scene.get("id", "unknown")
    output_dir = ensure_session_dir(session_id)
    path = os.path.join(output_dir, f"scene_{scene_id}.png")
    
    if os.path.exists(path) and os.path.getsize(path) > 0:
        scene.update({"image_path": path})
        return scene

    # FALLBACK CHAIN
    models_to_try = [
        model_id, 
        MODEL_REGISTRY["image_fast"], 
        MODEL_REGISTRY["image_fallback"]
    ]
    
    for i, attempt_model in enumerate(models_to_try):
        try:
            visual_content = scene.get("prompt") or scene.get("visual_prompt") or DEFAULT_IMAGE_PROMPT
            
            # SANITIZE if it's a fallback attempt
            if i > 0:
                risk_words = ["fraud", "scam", "violence", "abuse", "crime", "illegal", "tenant", "dispute", "blood"]
                for word in risk_words:
                    visual_content = re.compile(re.escape(word), re.IGNORECASE).sub("professional", visual_content)

            # ANCHORING
            dna_prefix = f"{identity_dna}. " if identity_dna else ""
            visual_with_dna = f"{dna_prefix}{visual_content}"
            prefix = IMAGE_PROMPT_PREFIX.replace("{ASPECT_RATIO}", global_aspect_ratio)
            final_prompt = prefix + visual_with_dna
            ratio_imagen = format_aspect_ratio(global_aspect_ratio, "imagen")

            client = genai.Client(api_key=api_key)
            
            def _call_api():
                if "gemini" in attempt_model.lower():
                    # --- MULTIMODAL UPGRADE: Image + DNA + Prompt ---
                    content_list = []
                    
                    # 1. Add Reference Image (if available)
                    if reference_image_path and os.path.exists(reference_image_path):
                        content_list.append(PIL.Image.open(reference_image_path))
                    
                    # 2. Add Compound Prompt (DNA + Visual Instructions)
                    content_list.append(final_prompt)

                    response = client.models.generate_content(
                        model=attempt_model, 
                        contents=content_list,
                        config=genai_types.GenerateContentConfig(response_modalities=['IMAGE'])
                    )
                    if not response.candidates: raise RuntimeError("No candidates")
                    for part in response.candidates[0].content.parts:
                        if part.inline_data:
                            with open(path, "wb") as f: f.write(part.inline_data.data)
                            scene.update({"image_path": path, "image_model": attempt_model})
                            print(f"      [IMAGE SUCCESS] Reference-locked visual saved: {os.path.basename(path)} ({attempt_model})")
                            return scene

                    raise RuntimeError("No inline_data")
                else:
                    response = client.models.generate_images(
                        model=attempt_model, 
                        prompt=final_prompt,
                        config=genai_types.GenerateImagesConfig(number_of_images=1, aspect_ratio=ratio_imagen, person_generation="allow_adult"),
                    )
                    if response.generated_images:
                        with open(path, "wb") as f: f.write(response.generated_images[0].image.image_bytes)
                        scene.update({"image_path": path, "image_model": attempt_model})
                        return scene
                    raise RuntimeError("No images generated")

            # Try the API
            return retry_with_backoff(_call_api, retries=1)
            
        except Exception as e:
            print(f"      [RETRY] {attempt_model} failed for Scene {scene_id}. Trying next in chain...")
            if i == len(models_to_try) - 1:
                trace = traceback.format_exc()
                print(f" [DEV ERROR] Video Gen Scene {scene_id}:\n{trace}")
                return None
            time.sleep(2)
    return None


def image_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Image Generator (Grouped & Optimized Mode)] ---")
    if "audit_log" not in state: state["audit_log"] = []
    
    session_id = state["session_id"]
    api_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    model_id = state.get("model_id") or "gemini-3.1-flash-image-preview"
    global_aspect_ratio = state.get("aspect_ratio", "16:9")
    
    scenes = state.get("scenes", [])
    if not scenes: return state

    # --- PHASE 1: MATHEMATICAL GROUPING BY DURATION ---
    # CRITICAL FIX: Calculate the ACTUAL total duration based on user-reviewed scenes, not the UI slider.
    total_duration = sum(float(s.get("duration", 4.0)) for s in scenes)
    
    if total_duration < 12:

        num_target_groups = 1
    elif total_duration < 20:
        num_target_groups = 2
    else:
        num_target_groups = 3
    
    print(f"   [Strategy] Video Duration: {total_duration}s -> Using {num_target_groups} unique image(s).")
    
    # Split scenes into N mathematical groups evenly
    num_target_groups = min(num_target_groups, len(scenes))
    k, m = divmod(len(scenes), num_target_groups)
    scene_groups = [scenes[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)] for i in range(num_target_groups)]
    scene_groups = [g for g in scene_groups if g] # Remove empty groups just in case

    
    # --- PHASE 2: GENERATE HERO IMAGE & EXTRACT DNA ---
    hero_scene = None
    identity_dna = None
    
    # Generate the first image of the first group
    print(f"   [GROUP 1] Generating Hero Identity Anchor...")
    hero_scene = generate_image_asset(scene_groups[0][0], api_key, model_id, session_id, global_aspect_ratio, state["audit_log"])
    
    if not hero_scene:
        print(f"   [CRITICAL] Hero Image failed. Pipeline stop.")
        return state
        
    # Extract DNA
    print(f"   [DNA] Locking character identity...")
    identity_dna = extract_identity_dna(hero_scene["image_path"], api_key, state["audit_log"])
    state["identity_dna"] = identity_dna

    # --- PHASE 3: PROCESS ALL GROUPS ---
    final_scenes = []
    for g_idx, group in enumerate(scene_groups):
        group_id = g_idx + 1
        group_image_path = None
        group_model = None
        
        if g_idx == 0:
            # First group uses the Hero image we just made
            group_image_path = hero_scene["image_path"]
            group_model = hero_scene["image_model"]
        else:
            # Subsequent groups generate ONE new image using the DNA and the Hero Image as a reference
            print(f"   [GROUP {group_id}] Generating unique visual with Identity DNA & Visual Reference...")
            rep_scene = generate_image_asset(
                group[0], api_key, model_id, session_id, global_aspect_ratio, 
                state["audit_log"], identity_dna=identity_dna, 
                reference_image_path=hero_scene["image_path"]
            )
            if rep_scene:
                group_image_path = rep_scene["image_path"]
                group_model = rep_scene["image_model"]
            else:
                # Fallback to previous group image if generation fails
                group_image_path = final_scenes[-1]["image_path"]
                group_model = final_scenes[-1]["image_model"]

        # Apply the group image to all scenes in this group (100% stillness within group)
        for scene in group:
            scene["image_path"] = group_image_path
            scene["image_model"] = group_model
            final_scenes.append(scene)

    state["scenes"] = final_scenes
    print(f"   Consistency Stage Complete: {len(scene_groups)} unique looks created.")
    return state
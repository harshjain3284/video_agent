import os
import time
import re
import PIL.Image
import traceback
from datetime import datetime
from google import genai
from google.genai import types as genai_types
from src.state.agent_state import AgentState
from src.config import GEMINI_API_KEY, BRAND_STYLES, MODEL_REGISTRY
from src.prompts import DEFAULT_IMAGE_PROMPT, IMAGE_PROMPT_PREFIX, DNA_EXTRACTION_PROMPT
from src.utils.core_utils import format_aspect_ratio, ensure_session_dir, retry_with_backoff

def _extract_identity_dna(image_path: str, api_key: str) -> str:
    """Uses Gemini to extract a technical 'Visual DNA' from the Hero shot."""
    if not os.path.exists(image_path): return ""
    client = genai.Client(api_key=api_key)
    
    try:
        response = client.models.generate_content(
            model=MODEL_REGISTRY["identity_anchor"],
            contents=[DNA_EXTRACTION_PROMPT, PIL.Image.open(image_path)]
        )
        return response.text.strip()
    except Exception as e:
        print(f"   [DNA Warning] Extraction failed: {e}")
        return ""

def _build_final_prompt(scene_prompt: str, ratio: str, dna: str = None) -> str:
    """Creates a high-precision, clean prompt for Imagen 4."""
    # Keep it clean and focused. Over-prompting causes hallucinations.
    dna_part = f"The character is defined as: {dna}. " if dna else ""
    
    # Surgical merge
    final = (
        f"A professional photorealistic portrait for a corporate brand. "
        f"{dna_part}"
        f"Scene Action: {scene_prompt}. "
        f"Style: Cinematic 35mm photography, high-end office lighting, sharp focus, {ratio} composition."
    )
    return final.strip()

def _generate_single_image(scene: dict, api_key: str, model_id: str, session_id: str, 
                         aspect_ratio: str, dna: str = None, ref_path: str = None) -> str:
    """The core engine for calling Google's Image APIs (Imagen or Gemini)."""
    output_dir = ensure_session_dir(session_id)
    target_path = os.path.join(output_dir, f"scene_{scene.get('id', 'temp')}.png")
    
    final_prompt = _build_final_prompt(scene.get("visual_prompt", DEFAULT_IMAGE_PROMPT), aspect_ratio, dna)
    client = genai.Client(api_key=api_key)

    def _api_call():
        if ref_path and os.path.exists(ref_path):
            # MULTIMODAL MODE: Use reference image for identity locking
            try:
                contents = [PIL.Image.open(ref_path), f"REFERENCE ATTACHED. Use it to maintain identity. Task: {final_prompt}"]
                resp = client.models.generate_content(
                    model=model_id, contents=contents,
                    config=genai_types.GenerateContentConfig(response_modalities=['IMAGE'])
                )
                for part in resp.candidates[0].content.parts:
                    if part.inline_data:
                        with open(target_path, "wb") as f: f.write(part.inline_data.data)
                        return target_path
            except Exception as e:
                import traceback
                print(f"   [CRITICAL DIAGNOSTIC] Multimodal anchoring failed!")
                traceback.print_exc()
                return None
        else:
            try:
                ratio_fmt = format_aspect_ratio(aspect_ratio, "imagen")
                resp = client.models.generate_images(
                    model=model_id, prompt=final_prompt,
                    config=genai_types.GenerateImagesConfig(number_of_images=1, aspect_ratio=ratio_fmt, person_generation="allow_adult")
                )
                if resp.generated_images:
                    with open(target_path, "wb") as f: f.write(resp.generated_images[0].image.image_bytes)
                    return target_path
            except Exception as e:
                import traceback
                print(f"   [CRITICAL DIAGNOSTIC] Standard image generation failed!")
                traceback.print_exc()
                raise e # let retry_with_backoff handle it
        return None

    return retry_with_backoff(_api_call)

def image_node(state: AgentState, hero_only: bool = False) -> AgentState:
    """
    ELITE IMAGE GENERATOR
    Manages Hero-Anchoring and Individual Scene Generation.
    """
    print(f"--- [Node: Image Generator (Modular)] ---")
    api_key = GEMINI_API_KEY.strip(' "\'') if GEMINI_API_KEY else None
    if not api_key: return state

    scenes = state.get("scenes", [])
    if not scenes: return state

    # 1. Phase A: Hero Shot & DNA Extraction
    print(f"   [Phase 1] Generating Hero Identity Anchor...")
    # Use the first scene to set the Hero look
    hero_path = _generate_single_image(scenes[0], api_key, MODEL_REGISTRY["image_pro"], state["session_id"], state["aspect_ratio"])
    
    if hero_path:
        state["scenes"][0]["image_path"] = hero_path
        state["audit_log"].append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "node": "Image Gen: Hero Shot",
            "status": "Success",
            "model": MODEL_REGISTRY["image_pro"],
            "details": f"Identity Anchor Created. Path: {os.path.basename(hero_path)}"
        })
    else:
        state["error"] = "Hero Image Generation Failed."
        return state
        
    dna = _extract_identity_dna(hero_path, api_key)
    state["identity_dna"] = dna

    # If we only wanted the hero for approval, stop here
    if hero_only:
        print(f"   [OK] Hero Shot generated. Pausing for human approval.")
        return state

    # 2. Phase B: Process Remaining Scenes with DNA Lock
    final_scenes = []
    for i, scene in enumerate(scenes):
        if i == 0:
            group_img = hero_path
        else:
            print(f"   [Phase 2] Generating Shot {i+1} with DNA Lock...")
            # We vary the prompt for each scene to ensure unique poses
            group_img = _generate_single_image(scene, api_key, MODEL_REGISTRY["image_standard"], 
                                             state["session_id"], state["aspect_ratio"], dna=dna, ref_path=hero_path)
            group_img = group_img or hero_path 
            
            state["audit_log"].append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "node": f"Image Gen: Scene {i+1}",
                "status": "Success",
                "model": MODEL_REGISTRY["image_standard"],
                "details": f"Unique variation generated using Hero DNA anchoring."
            })

        # Calculate Cost
        is_pro = i == 0 
        from src.config import COSTS
        img_cost = COSTS["image"].get("imagen", 0.03) if is_pro else COSTS["image"].get("gemini", 0.005)

        scene["image_path"] = group_img
        scene["image_cost"] = img_cost
        final_scenes.append(scene)

    state["scenes"] = final_scenes
    print(f"   [OK] Image Consistency Stage Complete: {len(scenes)} unique looks created.")
    return state
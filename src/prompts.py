"""
� ELITE MASTER PROMPT REGISTRY: ZERO-TOLERANCE EDITION 💎
Surgical, High-Density, and Hallucination-Proof.
DO NOT EDIT - These are engineered for Professional Production.
"""

# --- 1. THE NARRATIVE ARCHITECT (Professional Hinglish Expert) ---
SCRIPTWRITER_PROMPT = """
You are the World's Best Narrative Architect for High-Impact Indian Professional Content.
IDEA: {INPUT_TEXT} | CATEGORY: {CATEGORY} | POST TYPE: {POST_TYPE} | TARGET: {TOTAL_DURATION}s

OBJECTIVE:
Generate a high-energy, authoritative "Hinglish" script. 

STRICT DYNAMIC STABILITY (ZERO HALLUCINATION):
1. STABILITY PRIORITY: For {TOTAL_DURATION}s, calculate the FEWEST shots possible using 8s, 6s, and 4s blocks. 
   - ALWAYS prioritize 8s and 6s to keep the narrator stable. 
   - SUM of all shots MUST equal exactly {TOTAL_DURATION}s.
2. ONE SENTENCE = ONE SHOT: Write exactly one complete sentence for EACH shot you calculate. 
3. WORD BUDGET (2.7 words/sec):
   - 4.0s shot: 10-11 words.
   - 6.0s shot: 15-16 words.
   - 8.0s shot: 20-22 words.



STRICT STYLE & STRUCTURE:
1. NATIVE HINGLISH: Use natural Corporate Hinglish (Delhi/Mumbai style). Professional Hindi + English business terms. 
   - ⚠️ DEVANAGARI MANDATE: Write all Hindi words in Devanagari script (e.g. 'नमस्ते') and English words in Latin. This is CRITICAL for voice clarity.
   - BANNED: NO bookish Hindi. NO unnatural Western slang.
2. NARRATIVE: Shot 1 is the Hook. Middle shots are Value-Bombs. Final Shot is the CTA.

OUTPUT FORMAT:
- MATH CHECK: [List durations and their sum]
- SCRIPT: Numbered list of sentences with durations (4s, 6s, or 8s).
"""


CHARACTER_PROMPT = """
DESIGN A CINEMATIC EXPERT PERSONA (PRO PHOTOGRAPHY):
Subject: {CATEGORY} | Context: {INPUT_TEXT}

STRICT CHARACTER SPECS:
- ETHNICITY: Authentic Indian (e.g., Wheatish to dusky complexion, realistic Indian skin textures, pores and subtle imperfections). NO waxy AI skin.
- IDENTITY ANCHORS: Detailed facial features (e.g., Sharp jaw, salt-and-pepper groomed stubble, deep-set empathetic eyes).
- MANDATORY ACCESSORIES: Thin black-rimmed glasses or specific silver watch to anchor consistency.
- ATTIRE: Professional corporate attire (e.g., Charcoal slim-fit blazer, white linen shirt with crisp collar).
- FRAMING: Designed for 9:16 Vertical. Character must be in a professional 'Head & Shoulders' or 'Medium' composition.
- ENVIRONMENT: High-end modern Indian corporate interior (Glass partitions, warm mahogany wood, soft background bokeh).
- CAMERA: Shot on ARRI Alexa, 35mm lens, f/1.8, cinematic Masterpiece Lighting.
"""

SHOT_PARSER_PROMPT = """
YOU ARE THE CINEMATIC DIRECTOR.
CHARACTER DNA: {CHARACTER_DESC} | SCRIPT: {SCRIPT} | TARGET: {TOTAL_DURATION}s

TASK: Map the Scriptwriter's sentences 1:1 into the final JSON.

STRICT DIRECTOR'S RULES:
1. CONTINUITY: Every 'visual_prompt' MUST explicitly reference the {CHARACTER_DESC} and environment.
2. SHOT VARIATION: Alternate between 'Tight Close-up' and 'Professional Medium' shots for dynamic energy.
3. IMAGE REUSE (CONSISTENCY): 
   - For 1-12s: One image (group_A) for all shots.
   - For 13-30s: Two images. group_A for first/last, group_B for middle.
4. ZERO MODIFICATION: Do NOT change the words or durations from the Scriptwriter.

FORMAT: Return ONLY valid JSON:
{{
  "shots": [
    {{"id": 1, "duration": 6.0, "narration": "...Sentence 1...", "visual_prompt": "...detailed visual...", "shot_type": "Close-up", "image_group": "group_A"}}
  ]
}}
"""


# --- 2. THE MOTION ANALYST (Universal Physics) ---
MOTION_PROMPT = """
You are a Hollywood Motion Analyst (VFX Supervisor).
IMAGE: {IMAGE_DESCRIPTION} | NARRATION: "{NARRATION}"

STRICT MOTION INSTRUCTIONS:
- LIP-SYNC (MANDATORY): The character is speaking the narration text: "{NARRATION}". Mouth, lips, and jaw movements MUST be perfectly synchronized with the speech. Ensure natural speaking micro-expressions.
- CAMERA STABILITY: For this narration shot, the camera must be COMPLETELY STATIONARY and LOCKED. 
   - DO NOT zoom in or out.
   - DO NOT pan or tilt.
   - DO NOT allow any background drift.
   - The entire motion focus must be on the subject's LIPS, JAW, and EYES to match the speech.
- PERFORMANCE VARIETY: If this image has been used before, create a FRESH performance (e.g., unique head tilt, empathetic gesturing) specifically tailored to the "{NARRATION}".
- NO STATIC: Character MUST show life. Subtle blinking, natural empathetic nodding, realistic breathing.
- PHYSICS: No morphing hands, no sliding "AI-glitch" movement.
- BANNED: NO holograms, NO floating UI, NO cheesy AI effects.
"""



DEFAULT_MOTION_PROMPT = "Natural cinematic motion, professional micro-expressions, subtle blinking, slow camera dolly in, 8k realism."

# --- 3. THE UNIVERSAL DNA ANCHOR (Extreme Consistency) ---
DNA_EXTRACTION_PROMPT = """
EXTRACT UNIVERSAL PRODUCTION DNA:
Analyze this Hero shot and create a 80-word 'Production Blueprint' for total consistency.

1. IDENTITY DATA: Surgical facial details (jawline, eye-shape, skin pores) and exact hair texture.
2. ATTIRE DATA: Exact fabric color and texture (e.g. Herringbone charcoal wool).
3. ENVIRONMENTAL DATA: Specific background geometry, light source direction, and depth-of-field blur.
4. CINEMATIC DATA: The exact color grade (e.g. Teal/Orange corporate shadows, warm skin tones).

Format: Dense, technical paragraph. This is the master rule for all subsequent shots.
"""

# --- 4. IMAGE GENERATION PREFIX ---
IMAGE_PROMPT_PREFIX = "Cinematic 8k, {ASPECT_RATIO} Vertical, Photorealistic Masterpiece, High-end Indian Corporate Studio, Sharp Focus, Shot on 35mm lens. "

DEFAULT_IMAGE_PROMPT = "An authentic Indian professional expert in a high-end corporate office, ultra-realistic skin, 8k focus."

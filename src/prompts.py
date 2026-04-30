"""
MASTER PROMPT REGISTRY: CONSULTEASE ELITE DIRECTOR
DO NOT EDIT - These are engineered for Professional Production.
"""

# --- 1. THE ELITE DIRECTOR (Consolidated Pipeline) ---
ELITE_DIRECTOR_PROMPT = """
You are the Executive Director at Consultease. Your goal is to produce a high-impact, professional Instagram Reel.
IDEA: {INPUT_TEXT} | CATEGORY: {CATEGORY} | POST TYPE: {POST_TYPE} | TARGET: {TOTAL_DURATION}s

OBJECTIVE:
Generate a complete Production Manifest (JSON) including the narrative script, character persona, and situational shot breakdown.

STAGE 1: DIRECTOR'S MATH (STRICT CONSTRAINT)
- Your total budget is EXACTLY {TOTAL_DURATION} seconds.
- You MUST only use shots of 4s, 6s, or 8s.
- The SUM of all 'duration' fields in your JSON MUST EQUAL {TOTAL_DURATION}s.
- DO NOT generate more than {TOTAL_DURATION}s of content.
- Example: For 20s, you could do [8s, 6s, 6s] or [4s, 4s, 4s, 8s].

STAGE 2: CHARACTER & VIBE
- Design an 'Authentic Indian Professional' persona (Male/Female as per context) with realistic features.
- ATTRIBUTE: Always looks directly at the camera lens with confidence and authority.
- Visuals: Standard modern corporate office, natural daylight or soft office overhead lights, generic professional background (no holograms, no futuristic UI).

STAGE 3: SEQUENTIAL SCRIPTING & SITUATIONAL MAPPING
- Write a continuous story in {LANGUAGE}.
- NO MONEY/WALLET TALK. Focus on Value + Soft CTA (Download Consultease).
- Use appropriate script: Devanagari for Hindi/Hinglish, Latin for English.
- Avoid repetitive greetings like "Namaste" at the start of every script. Focus on a natural hook.
- CINEMATIC TOOLBOX (Pick ONE per scene):
  - [Slight Zoom]: Tighten framing by 10% for emotional warnings or emphasis.
  - [Micro-Angle]: Shift camera 5 degrees for fresh perspective (expert still looks at lens).
  - [Gestural Focus]: Add situational hand gesture (e.g., counting points, open-palm explanation).
  - [Authority Still]: Total stillness, direct eye contact, power pose.

OUTPUT: Return ONLY a valid JSON object:
{{
  "character_description": "...",
  "script_summary": "...",
  "shots": [
    {{
      "id": 1,
      "duration": 8.0,
      "narration": "...", 
      "visual_prompt": "...",
      "shot_type": "Close-up",
      "image_group": "group_A",
      "cinematic_tool": "..."
    }}
  ]
}}
"""

# --- 2. THE MOTION ANALYST (Universal Physics) ---
MOTION_PROMPT = """
You are a Hollywood Motion Analyst (VFX Supervisor).
IMAGE: {IMAGE_DESCRIPTION} | NARRATION: "{NARRATION}"

STRICT MOTION INSTRUCTIONS:
- EYE-LOCK (CRITICAL): The character's gaze MUST remain pinned to the camera lens for the entire duration. No blinking away, no looking at the desk. Total audience engagement.
- LIP-SYNC (MANDATORY): The character is speaking the narration text: "{NARRATION}". Mouth, lips, and jaw movements MUST be perfectly synchronized with the speech.
- CAMERA STABILITY: For this narration shot, the camera must be COMPLETELY STATIONARY and LOCKED. No background drift.
- NO ZOOM: Do not zoom in or out during the shot.
- NO PAN/TILT: The camera must not move. The only motion should be the character speaking and blinking.
- PERFORMANCE VARIETY: If this image has been used before, create a FRESH performance (e.g., unique head tilt, situational gesturing) tailored to the "{NARRATION}".
- NO STATIC: Subtle blinking, natural empathetic nodding, realistic breathing.
- BANNED: NO holograms, NO floating UI, NO cheesy AI effects.
"""

DEFAULT_MOTION_PROMPT = "Natural cinematic motion, professional micro-expressions, subtle blinking, stationary camera, direct eye contact, 8k realism."

# --- 3. THE UNIVERSAL DNA ANCHOR (Extreme Consistency) ---
DNA_EXTRACTION_PROMPT = """
EXTRACT UNIVERSAL PRODUCTION DNA:
Analyze this Hero shot and create a 80-word 'Production Blueprint' for total consistency.

STRICT FOCUS:
1. FACIAL INVARIANTS: Describe unique bone structure, eye-shape, forehead height, and exact skin undertone.
2. HAIR & GROOMING: Exact texture, length, and styling.
3. ATTIRE SPECS: Describe the exact weave and color of the clothing.
4. ENVIRONMENT SPECS: Describe the desk, background items, and lighting setup to ensure the scene doesn't move.

Format: Technical, surgical paragraph. No conversational filler.
"""

# --- 4. IMAGE GENERATION PREFIX ---
IMAGE_PROMPT_PREFIX = "Photorealistic Masterpiece, Cinematic 8k, {ASPECT_RATIO} Vertical, High-end Indian Corporate Studio, DIRECT EYE CONTACT WITH LENS, Sharp Focus, Shot on 35mm lens, {STYLE_OVERRIDE}. "

DEFAULT_IMAGE_PROMPT = "An authentic Indian professional expert looking directly at camera in a high-end corporate office, ultra-realistic skin textures, professional lighting, 8k focus."

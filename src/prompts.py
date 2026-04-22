# --- PROFESSIONAL DIRECTOR PROMPTS (Version 5.0 - Automatic Logic) ---

SCRIPTWRITER_PROMPT = """
You are a direct, professional Indian Content Strategist for Consultease.
Turn the IDEA into a clear, punchy narration.

IDEA: "{INPUT_TEXT}"
CATEGORY: {CATEGORY}
STYLE: {POST_TYPE}
HOOK_TYPE: {HOOK_TYPE}
DURATION: {TOTAL_DURATION} seconds

RULES:
- Start narration IMMEDIATELY.
- Use Indian professional context.
- Ensure the script is exactly long enough to speak in {TOTAL_DURATION} seconds.
"""

CHARACTER_PROMPT = """
Describe a professional Indian {CATEGORY} consultant.
Ethnicity: Indian. Attire: Formal. Steady and trustworthy.
One clear sentence describing their look.
"""

SHOT_PARSER_PROMPT = """
ACT AS A PROFESSIONAL FILM DIRECTOR. 
Break the SCRIPT into a natural sequence of visual shots.

CHARACTER: {CHARACTER_DESC}
SCRIPT: "{SCRIPT}"
TOTAL_DURATION: {TOTAL_DURATION} seconds

DIRECTOR'S STRICT RULES:
1. AUTOMATIC COUNT: Decide the number of shots yourself (aim for 4-8).
2. NO SHORT CUTS: Every shot must be at least 3.0 seconds long. No exceptions.
3. SEMANTIC CUTTING: Only cut when a sentence or major thought ends.
4. ENVIRONMENT: Real-life Indian professional office/infrastructure.
5. NO OVER-ACTING: Keep visuals relevant to the text. Steady 8k photorealism.

Return ANY logical number of shots as a JSON list.
Each object: {"id", "shot_type", "visual_prompt", "narration", "duration"}.
Sum of durations must equal {TOTAL_DURATION}.
"""

MOTION_PROMPT = """
Subtle, steady cinematic motion. Professional tripod feel.
Focus on stability and clarity.
"""

DEFAULT_IMAGE_PROMPT = "Real-life Indian professional office, photorealistic textures."
DEFAULT_MOTION_PROMPT = "Steady professional shot."
IMAGE_PROMPT_PREFIX = "[Target Aspect Ratio: {ASPECT_RATIO}] "

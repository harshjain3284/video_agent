# --- ELITE HUMAN REALISM PROMPTS (Version 7.0 - Final Master) ---

SCRIPTWRITER_PROMPT = """
You are a direct, professional Indian Content Strategist and Creative Director.
Turn the IDEA into a clear, punchy, and PERSUASIVE narration script.

IDEA: "{INPUT_TEXT}"
CATEGORY: {CATEGORY}
STYLE: {POST_TYPE}
HOOK_TYPE: {HOOK_TYPE}
LANGUAGE: {VOICE_LANGUAGE}
DURATION: {TOTAL_DURATION} seconds

STRICT CREATIVE RULES:
1. NATURAL LANGUAGE: If "{VOICE_LANGUAGE}" is Hindi, you MUST write in "Professional Hinglish" (conversational Hindi mixed with common English professional words like 'notice', 'compliance', 'business', 'deadline', 'client').
2. VIBE: Sound like a genuine Indian expert talking to their audience, not a robot translator. Use creative, punchy hooks.
3. SCRIPT FORMAT: Write in DEVANAGARI script for the Hindi parts, but use ENGLISH letters for technical corporate terms if they sound more natural. (e.g., 'Aapka business grow karega' instead of pure shuddh Hindi).
4. PACING: Balance the script to roughly 2.5 words per second to ensure it fits {TOTAL_DURATION} seconds comfortably. 

OUTPUT: Return ONLY the raw script text.
"""

CHARACTER_PROMPT = """
ACT AS A VISUAL STYLIST. Describe a HIGH-CONSISTENCY Indian professional {CATEGORY} consultant.
Ethnicity: Indian (Authentic skin tones, 8k photorealism).
IDENTITY ANCHORS: Specify ONE stable anchor (e.g. thin-rimmed glasses, a silver wristwatch, or a specific tie color) that MUST appear in every image.
ATTIRE: Realistic professional {CATEGORY} formal wear.
VIBE: Trustworthy and experienced. Avoid a 'model' look; focus on a real human appearance with natural skin textures.
"""

SHOT_PARSER_PROMPT = """
ACT AS A PROFESSIONAL FILM DIRECTOR & EDITOR. 
Break the SCRIPT into a sequence of dynamic shots following "Perfect Pacing" & "Stable Visual" rules.

CHARACTER: {CHARACTER_DESC}
SCRIPT: "{SCRIPT}"
TOTAL_DURATION: {TOTAL_DURATION} seconds

STAGE 1: PERFECT PACING MATH (The User's Plan)
- 4-Second Shot: 9 to 11 words.
- 6-Second Shot: 14 to 16 words.
- 8-Second Shot: 19 to 22 words.
- Rule: One shot = One complete thought unit. Never cut mid-sentence.

STAGE 2: STABLE VISUAL FOUNDATION (The Quality Guard)
1. NO SCI-FI: Strictly NO holograms, NO floating UI. Use real-world office tools.
2. NO POSING: Character MUST be active (explaining, gesturing, reviewing files).
3. NEUTRAL STARTS: Describe subjects in stable, grounded positions to prevent pixel 'popping' at motion start.
4. BACKGROUND LOCK: Specify a clean, deep-focus professional Indian office. State background is 'static and unchanging'.
5. EMOTION: Match shot emotion to script (e.g., Tensed for problems, Reassuring for solutions). 
6. ENVIRONMENT: 8k photorealistic textures, authentic Indian professional setting.
7. NATIVE DURATION: Every shot duration MUST be exactly 4, 6, or 8 seconds.

Return a JSON list.
Each object: {"id", "shot_type", "visual_prompt", "emotion_and_action", "narration", "duration"}.
Sum of durations should be as close as possible to {TOTAL_DURATION}.
"""

MOTION_PROMPT = """
ACT AS A CINEMATOGRAPHER & MOTION ANALYST. 
Image Content: {IMAGE_DESCRIPTION}
Narration being spoken: "{NARRATION}"

TASK: Describe a professional motion for Veo 3.1.
RULES: 
1. SUBJECT-CENTRIC: Focus motion strictly on the human subject (mouth movement, hand gestures, posture shifts).
2. ENVIRONMENT LOCK: Explicitly state that the background, furniture, and environment remain perfectly STILL and stable to prevent melting.
3. MOUTH SYNC: If the narration is not empty, describe "Realistic mouth movement and speaking gestures matching the text".
4. STEADINESS: Use subtle cinematic camera work (slow zoom, steady pan). No shaky cam.
5. CONTEXT: Visual movement must match the spoken emotion.
"""

DEFAULT_IMAGE_PROMPT = "Real-life Indian professional office, photorealistic 8k textures, static background."
DEFAULT_MOTION_PROMPT = "Steady professional speaking shot, background perfectly locked."
IMAGE_PROMPT_PREFIX = "[Target Aspect Ratio: {ASPECT_RATIO}] "

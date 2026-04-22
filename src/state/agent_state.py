from typing import List, TypedDict, Optional

class Scene(TypedDict):
    id: int
    description: str
    visual_prompt: str
    narration: str
    image_path: Optional[str]
    audio_path: Optional[str]
    video_path: Optional[str]
    image_model: Optional[str]
    motion_model: Optional[str]
    motion_prompt: Optional[str]

class AgentState(TypedDict):
    input_text: str
    session_id: str
    scenes: List[Scene]
    video_path: Optional[str]
    audio_path: Optional[str]
    current_node: str
    error: Optional[str]
    aspect_ratio: str  # e.g., "16:9", "9:16", "1:1"
    resolution: tuple  # (width, height)
    scene_count: int
    scene_duration: int
    enable_subtitles: bool
    enable_voiceover: bool
    enable_transitions: bool
    total_duration: int  # in seconds
    model_id: str
    video_model_id: str
    video_clips: List[str] # Paths to 5-6s animated scene files
    usage_stats: List[dict] # List of costs per action
    total_cost: float
    # Creative Narrative Parameters
    script: Optional[str]
    character_description: Optional[str]
    # Strategic Parameters
    category: Optional[str]
    post_type: Optional[str]
    hook_type: Optional[str]
    brand_page: Optional[str]
    format: Optional[str]

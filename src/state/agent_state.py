from typing import List, TypedDict, Optional

class Scene(TypedDict):
    id: int
    description: str
    visual_prompt: str
    narration: str
    image_path: Optional[str]
    audio_path: Optional[str]

class AgentState(TypedDict):
    input_text: str
    session_id: str
    scenes: List[Scene]
    video_path: Optional[str]
    audio_path: Optional[str]
    current_node: str
    error: Optional[str]

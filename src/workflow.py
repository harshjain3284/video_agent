import os
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, START, END

from src.state.agent_state import AgentState
from src.nodes.parser_node import parser_node
from src.nodes.image_node import image_node
from src.nodes.voice_node import voice_node
from src.nodes.editor_node import editor_node
from src.nodes.motion_node import motion_analyst_node
from src.nodes.video_node import video_node

def asset_generation_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Parallel Asset Generation] ---")
    
    with ThreadPoolExecutor() as executor:
        future_gen = executor.submit(image_node, state.copy())
        future_voice = executor.submit(voice_node, state.copy())
        
        state_gen = future_gen.result()
        state_voice = future_voice.result()
        
    for i in range(len(state["scenes"])):
        state["scenes"][i]["image_path"] = state_gen["scenes"][i].get("image_path")
        state["scenes"][i]["audio_path"] = state_voice["scenes"][i].get("audio_path")
        
    return state

class VideoAgentWorkflow:
    def __init__(self):
        workflow = StateGraph(AgentState)

        # Add all nodes
        workflow.add_node("parser", parser_node)
        workflow.add_node("image_generator", asset_generation_node)
        workflow.add_node("motion_analyst", motion_analyst_node)
        workflow.add_node("video_generator", video_node)
        workflow.add_node("final_editor", editor_node)

        # Define the new Motion-Enabled Path
        workflow.add_edge(START, "parser")
        workflow.add_edge("parser", "image_generator")
        workflow.add_edge("image_generator", "motion_analyst")
        workflow.add_edge("motion_analyst", "video_generator")
        workflow.add_edge("video_generator", "final_editor")
        workflow.add_edge("final_editor", END)

        self.app = workflow.compile()

# Instantiate the singleton
agent_workflow = VideoAgentWorkflow()

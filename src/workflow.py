import os
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, START, END

from src.state.agent_state import AgentState
from src.nodes.parser_node import parser_node
from src.nodes.generator_node import generator_node
from src.nodes.voice_node import voice_node
from src.nodes.processor_node import processor_node
from src.nodes.motion_node import motion_analyst_node
from src.nodes.animator_node import animator_node

def asset_generation_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Parallel Asset Generation] ---")
    
    with ThreadPoolExecutor() as executor:
        future_gen = executor.submit(generator_node, state.copy())
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
        workflow.add_node("assets", asset_generation_node)
        workflow.add_node("motion_analyst", motion_analyst_node)
        workflow.add_node("animator", animator_node)
        workflow.add_node("processor", processor_node)

        # Define the new Motion-Enabled Path
        workflow.add_edge(START, "parser")
        workflow.add_edge("parser", "assets")
        workflow.add_edge("assets", "motion_analyst")
        workflow.add_edge("motion_analyst", "animator")
        workflow.add_edge("animator", "processor")
        workflow.add_edge("processor", END)

        self.app = workflow.compile()

# Instantiate the singleton
agent_workflow = VideoAgentWorkflow()

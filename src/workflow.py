import os
from concurrent.futures import ThreadPoolExecutor
from langgraph.graph import StateGraph, START, END

from src.state.agent_state import AgentState
from src.nodes.parser_node import parser_node
from src.nodes.generator_node import generator_node
from src.nodes.voice_node import voice_node
from src.nodes.processor_node import processor_node

def asset_generation_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Parallel Asset Generation] ---")
    
    with ThreadPoolExecutor() as executor:
        # Run generator and voice node in parallel
        future_gen = executor.submit(generator_node, state.copy())
        future_voice = executor.submit(voice_node, state.copy())
        
        state_gen = future_gen.result()
        state_voice = future_voice.result()
        
    # Merge findings back into the main state
    for i in range(len(state["scenes"])):
        state["scenes"][i]["image_path"] = state_gen["scenes"][i].get("image_path")
        state["scenes"][i]["audio_path"] = state_voice["scenes"][i].get("audio_path")
        
    return state

class VideoAgentWorkflow:
    def __init__(self):
        # 1. Initialize the StateGraph
        workflow = StateGraph(AgentState)

        # 2. Add Nodes
        workflow.add_node("parser", parser_node)
        workflow.add_node("assets", asset_generation_node)
        workflow.add_node("processor", processor_node)

        # 3. Define Edges
        workflow.add_edge(START, "parser")
        workflow.add_edge("parser", "assets")
        workflow.add_edge("assets", "processor")
        workflow.add_edge("processor", END)

        # 4. Compile the graph
        self.app = workflow.compile()

    def run(self, input_text: str):
        # Optional: High level runner method
        pass

# Instantiate the singleton for the app to use
agent_workflow = VideoAgentWorkflow()

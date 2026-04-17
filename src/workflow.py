from langgraph.graph import StateGraph, START, END
from src.state.agent_state import AgentState
from src.nodes.parser_node import parser_node
from src.nodes.generator_node import generator_node
from src.nodes.voice_node import voice_node
from src.nodes.processor_node import processor_node
from concurrent.futures import ThreadPoolExecutor

def asset_generation_node(state: AgentState) -> AgentState:
    print(f"--- [Node: Parallel Asset Generation] ---")
    
    with ThreadPoolExecutor() as executor:
        # Run generator and voice node in parallel
        # We pass copies to ensure thread safety on the scenes list
        future_gen = executor.submit(generator_node, state.copy())
        future_voice = executor.submit(voice_node, state.copy())
        
        # Wait for both to complete
        state_gen = future_gen.result()
        state_voice = future_voice.result()
        
    # Merge findings back into the main state
    for i in range(len(state["scenes"])):
        # Get image_path from generator result
        state["scenes"][i]["image_path"] = state_gen["scenes"][i].get("image_path")
        # Get audio_path from voice result
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
        import datetime
        from src.config import ASSETS_DIR
        
        session_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join(ASSETS_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        initial_state: AgentState = {
            "input_text": input_text,
            "session_id": session_id,
            "scenes": [],
            "video_path": None,
            "audio_path": None,
            "current_node": "parser",
            "error": None
        }
        return self.app.invoke(initial_state)

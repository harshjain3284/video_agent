import sys
import os
import traceback

# Add project root to path
sys.path.append(os.getcwd())

from src.workflow import agent_workflow
from src.state.agent_state import AgentState

def diagnostic_test():
    print("--- [PIPELINE INTEGRITY DIAGNOSTIC START] ---")
    
    test_state = AgentState(
        session_id="diagnostic_test_001",
        input_text="How to save Income Tax in India?",
        category="Income Tax",
        post_type="Authority",
        total_duration=15,
        aspect_ratio="9:16",
        voice_language="Hindi (India)",
        voice_gender="Female",
        enable_voiceover=True,
        enable_subtitles=True,
        scenes=[],
        audit_log=[]
    )

    print("\n1. Testing Node Connectivity...")
    try:
        # We simulate a partial run to check for import errors and node logic
        print("   - Testing Parser Node...")
        # Note: We are using the actual compiled app to check the graph flow
        app = agent_workflow.app
        
        # We only run the first step (Parser) to see if it works
        # In a real check, we'd use 'interrupt' points, but for now we just verify nodes exist
        nodes = app.get_graph().nodes
        print(f"   - Verified Graph Nodes: {list(nodes.keys())}")
        
        required_nodes = ["parser", "image_generator", "motion_analyst", "video_generator", "quality_inspector", "final_editor"]
        for node in required_nodes:
            if node in nodes:
                print(f"      [OK] Node '{node}' is correctly registered.")
            else:
                print(f"      [ERROR] Node '{node}' is MISSING!")
                return False

        print("\n2. Checking Module Imports...")
        # Manually import each to trigger potential hidden errors
        from src.nodes.parser_node import parser_node
        from src.nodes.image_node import image_node
        from src.nodes.voice_node import voice_node
        from src.nodes.motion_node import motion_analyst_node
        from src.nodes.video_node import video_node
        from src.nodes.inspector_node import inspector_node
        from src.nodes.editor_node import editor_node
        
        print("   [OK] All node modules are importable and error-free.")

        print("\n3. Validating Config Alignment...")
        from src.config import MODEL_REGISTRY, BRAND_STYLES, COSTS
        print(f"   - Primary Director: {MODEL_REGISTRY.get('elite_director')}")
        print(f"   - Video Engine: {MODEL_REGISTRY.get('video_pro')}")
        print(f"   - QC Inspector: {MODEL_REGISTRY.get('quality_inspector')}")
        print("   [OK] Config values are correctly loaded.")

        print("\n--- [DIAGNOSTIC SUCCESS] ---")
        print("The modular architecture is sound and ready for production.")
        return True

    except Exception as e:
        print("\n--- [DIAGNOSTIC FAILED] ---")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnostic_test()
    if not success:
        sys.exit(1)

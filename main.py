from src.workflow import VideoAgentWorkflow
import sys

def main():
    agent = VideoAgentWorkflow()
    
    input_text = "A magical forest where trees are made of glass. A blue dragon flies over a crystal lake. The sun sets, casting rainbows everywhere."
    
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        
    print(f"STARTING: Video Agent Workflow...")
    result = agent.run(input_text)
    
    if result["error"]:
        print(f"ERROR: {result['error']}")
    elif result["video_path"]:
        print(f"SUCCESS: Your video is ready at: {result['video_path']}")
    else:
        print("INFO: Workflow finished but no video path was found.")

if __name__ == "__main__":
    main()

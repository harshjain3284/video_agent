from src.workflow import VideoAgentWorkflow
import sys

def main():
    agent = VideoAgentWorkflow()
    
    input_text = "A magical forest where trees are made of glass. A blue dragon flies over a crystal lake. The sun sets, casting rainbows everywhere."
    
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        
    print(f"🚀 Starting Video Agent Workflow...")
    result = agent.run(input_text)
    
    if result["error"]:
        print(f"❌ Error: {result['error']}")
    elif result["video_path"]:
        print(f"✅ Success! Your video is ready at: {result['video_path']}")
    else:
        print("🤔 Workflow finished but no video path was found.")

if __name__ == "__main__":
    main()

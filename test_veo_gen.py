import os
import time
from google import genai
from google.genai import types as genai_types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_veo_generation(image_path, prompt, output_filename="test_veo_output.mp4"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file.")
        return

    client = genai.Client(api_key=api_key)
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Error: Image file not found at {image_path}")
        return

    print(f"🚀 Starting Veo video generation...")
    print(f"📝 Prompt: {prompt}")
    print(f"🖼️  Image: {image_path}")

    try:
        # Load image
        image = genai_types.Image.from_file(location=image_path)

        # Configure video generation
        config = genai_types.GenerateVideosConfig(
            number_of_videos=1,
            duration_seconds=4,  # Veo 3.1 supports 4, 6, 8
            aspect_ratio="16:9", # Veo 3.1 supports 16:9, 9:16
            person_generation="allow_adult"
        )

        # Start generation
        operation = client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            image=image,
            config=config,
        )

        print("⏳ Generation in progress (polling every 10 seconds)...")
        
        # Poll for completion
        while not operation.done:
            time.sleep(10)
            operation = client.operations.get(operation)
            print("...", end="", flush=True)

        print("\n✅ Generation complete!")

        # Process response
        response = getattr(operation, "response", None)
        if not response or not getattr(response, "generated_videos", None):
            print("❌ Error: No video was generated.")
            return

        generated_video = response.generated_videos[0]
        video_obj = generated_video.video

        # Download and save
        print(f"💾 Downloading video to {output_filename}...")
        client.files.download(file=video_obj)
        video_obj.save(output_filename)
        
        print(f"🎉 Success! Video saved at: {os.path.abspath(output_filename)}")

    except Exception as e:
        print(f"❌ Failed to generate video: {str(e)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Veo AI Video Generation")
    parser.add_argument("--image", type=str, help="Path to input image")
    parser.add_argument("--prompt", type=str, default="Cinematic motion, slow camera move.", help="Motion prompt")
    parser.add_argument("--output", type=str, default="test_veo_output.mp4", help="Output filename")
    
    args = parser.parse_args()
    
    # Try to find a default image if none provided
    if not args.image:
        print("🔍 No image path provided. Searching for a sample image in assets...")
        found_image = None
        for root, dirs, files in os.walk("assets"):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg")):
                    found_image = os.path.join(root, file)
                    break
            if found_image: break
        
        if found_image:
            print(f"✅ Found sample image: {found_image}")
            args.image = found_image
        else:
            print("❌ No images found in assets/ directory. Please provide an image path using --image")
            exit(1)

    # Put your prompt here inside the quotes:
    my_test_prompt = "A cinematic shot with slow motion movement, high quality."
    
    test_veo_generation(
        r"C:\Users\Dell\Desktop\video_agent\video_agent\assets\20260420_182413\scene_1.png", 
        my_test_prompt, 
        args.output
    )

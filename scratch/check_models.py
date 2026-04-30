from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY").strip(' "\'')
client = genai.Client(api_key=api_key)

with open("scratch/all_models.txt", "w") as f:
    for m in client.models.list():
        f.write(f"{m.name}\n")

print("Raw model list saved to scratch/all_models.txt")

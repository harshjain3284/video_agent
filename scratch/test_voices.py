import asyncio
import edge_tts

async def test_voices():
    voices = await edge_tts.VoicesManager.create()
    hi_voices = voices.find(Locale="hi-IN")
    print("Hindi Voices found:")
    for v in hi_voices:
        print(f"- {v['Name']} ({v['Gender']})")

if __name__ == "__main__":
    try:
        asyncio.run(test_voices())
    except Exception as e:
        print(f"Error: {e}")

from google import genai
from app.core.config import settings
import asyncio

async def list_models():
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    print("--- AVAILABLE MODELS ---")
    print(f"Using API Key (first 5): {settings.GEMINI_API_KEY[:5]}...")
    try:
        # Use the SDK to list available models
        for model in client.models.list():
            print(f"Model: {model}")
    except Exception as e:
        print(f"Failed to list models: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())

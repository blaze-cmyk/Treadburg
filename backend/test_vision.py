"""
Test script to verify Gemini Vision API is working
"""
import asyncio
import base64
from google import genai
from google.genai import types
import os

async def test_vision():
    # Read a test image (we'll use a simple base64 string)
    # This is a 1x1 red pixel PNG
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key: {api_key[:20]}...")
    
    client = genai.Client(api_key=api_key)
    
    # Decode base64 to bytes
    image_bytes = base64.b64decode(test_image_b64)
    print(f"Image bytes: {len(image_bytes)}")
    
    # Create the message
    message_parts = [
        types.Part(text="What do you see in this image?"),
        types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    ]
    
    contents = [types.Content(role="user", parts=message_parts)]
    
    config = types.GenerateContentConfig(
        system_instruction="You are a helpful AI. Describe the image.",
        temperature=0.7,
    )
    
    print("Calling Gemini API...")
    response = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=contents,
        config=config,
    )
    
    print(f"Response: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_vision())

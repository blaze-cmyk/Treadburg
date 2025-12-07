"""
Test Gemini API Configuration
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv('env')

print("=" * 50)
print("Gemini API Configuration Test")
print("=" * 50)
print()

# Check if API key exists
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ GEMINI_API_KEY not found in environment!")
    print("Please check your backend/env file")
    sys.exit(1)

print(f"✅ GEMINI_API_KEY found: {api_key[:20]}...{api_key[-4:]}")
print()

# Try to import and initialize Gemini
try:
    from google import genai
    from google.genai import types
    print("✅ Google GenAI library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Google GenAI: {e}")
    print("Run: pip install google-genai")
    sys.exit(1)

# Try to create client
try:
    client = genai.Client(api_key=api_key)
    print("✅ Gemini client created successfully")
except Exception as e:
    print(f"❌ Failed to create Gemini client: {e}")
    sys.exit(1)

# Try a simple API call
try:
    print()
    print("Testing Gemini API with a simple query...")
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',  # Using stable experimental model
        contents='Say "Hello, TradeBerg!" in one sentence.',
        config=types.GenerateContentConfig(
            temperature=0.7,
            max_output_tokens=100
        )
    )
    
    print("✅ Gemini API call successful!")
    print(f"Response: {response.text}")
    print()
    print("=" * 50)
    print("✅ All tests passed! Gemini is configured correctly.")
    print("=" * 50)
    
except Exception as e:
    print(f"❌ Gemini API call failed: {e}")
    print()
    print("Possible issues:")
    print("1. API key is invalid or expired")
    print("2. API key doesn't have access to gemini-2.0-flash-lite-preview-02-05")
    print("3. Network connectivity issues")
    print("4. Quota exceeded")
    sys.exit(1)

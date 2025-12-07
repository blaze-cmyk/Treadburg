
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("GEMINI_API_KEY not found")
    exit(1)

client = genai.Client(api_key=api_key)

print("Listing models...")
try:
    # The SDK might have a different way to list models, but let's try the standard way for this SDK if possible.
    # Based on the error message "Call ListModels", let's try to find that method.
    # Since I don't have the SDK docs in front of me, I'll try to inspect the client or just try the v1beta way if I can.
    # Actually, the error came from `client.models.generate_content_stream`.
    # Let's try `client.models.list()` if it exists.
    
    # If using the new google-genai SDK (v0.x or 1.x):
    for model in client.models.list():
        print(model.name)
        
except Exception as e:
    print(f"Error listing models: {e}")
    # Fallback to trying to print dir(client.models) to see what's available
    try:
        print(dir(client.models))
    except:
        pass

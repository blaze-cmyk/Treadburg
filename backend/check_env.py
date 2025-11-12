"""Quick check if environment variables are loaded"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env
backend_dir = Path(__file__).parent
load_dotenv(backend_dir / ".env")

print("\n" + "="*60)
print("ENVIRONMENT VARIABLES CHECK")
print("="*60 + "\n")

# Check API keys
perplexity_key = os.getenv("PERPLEXITY_API_KEY", "")
openai_key = os.getenv("OPENAI_API_KEY", "")

if perplexity_key:
    print(f"✅ PERPLEXITY_API_KEY: {perplexity_key[:20]}... (loaded)")
else:
    print("❌ PERPLEXITY_API_KEY: NOT FOUND")

if openai_key:
    print(f"✅ OPENAI_API_KEY: {openai_key[:20]}... (loaded)")
else:
    print("❌ OPENAI_API_KEY: NOT FOUND")

print("\n" + "="*60)

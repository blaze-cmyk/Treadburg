"""
GeminiService wrapper for TradeBerg - EXACT COPY OF WORKING IMPLEMENTATION

This matches the working tradeberg-ai-chat (2) implementation.
"""

from __future__ import annotations

import asyncio
import base64
import os
from typing import AsyncGenerator, Dict, Optional

from core.constants import TRADEBERG_GENERAL_IDENTITY
from config import settings

try:
    from google import genai
    from google.genai import types
except ImportError as exc:
    genai = None  # type: ignore
    types = None  # type: ignore
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class GeminiService:
    """
    High-level Gemini adapter - matches working TypeScript implementation
    """

    def __init__(self) -> None:
        if genai is None:
            raise RuntimeError(f"Gemini client import failed: {_IMPORT_ERROR!r}")
        
        api_key = settings.GEMINI_API_KEY or os.getenv("API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY or API_KEY environment variable not set")
        
        self._client = genai.Client(api_key=api_key)

    async def stream(
        self,
        *,
        prompt: str,
        mode: str,
        chart_image: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Call Gemini and yield the assistant response as a stream of chunks.
        
        IMPORTANT: This matches the working TypeScript implementation:
        - Model: gemini-2.5-flash (not gemini-1.5-flash)
        - Image format: inlineData with mimeType and base64 data
        """
        # Use TRADEBERG_GENERAL_IDENTITY as system instruction
        system_content = TRADEBERG_GENERAL_IDENTITY

        # Configure the model - MATCH WORKING IMPLEMENTATION
        config = types.GenerateContentConfig(
            system_instruction=system_content,
            temperature=0.7,
        )

        # Build the user message
        # If there's an image, send it as multipart content
        if chart_image:
            # Extract mime type from data URL if present
            mime_type = "image/png"  # default
            image_data = chart_image
            
            # Check if it's a data URL
            if chart_image.startswith("data:"):
                # Format: data:image/png;base64,iVBORw0KG...
                parts = chart_image.split(",", 1)
                if len(parts) == 2:
                    header = parts[0]  # data:image/png;base64
                    image_data = parts[1]  # base64 string
                    
                    # Extract mime type
                    if ":" in header and ";" in header:
                        mime_type = header.split(":")[1].split(";")[0]
            
            print(f"DEBUG: Sending image with mime_type={mime_type}, data_length={len(image_data)}")
            
            # Decode base64 to bytes
            try:
                image_bytes = base64.b64decode(image_data)
                print(f"DEBUG: Decoded {len(image_bytes)} bytes")
            except Exception as e:
                print(f"DEBUG: Failed to decode base64: {e}")
                image_bytes = image_data.encode('utf-8') if isinstance(image_data, str) else image_data
            
            # Create multipart content with text and image
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type,
                                data=image_bytes
                            )
                        )
                    ]
                )
            ]
        else:
            # Text-only message
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )
            ]

        # Stream the response - USE WORKING MODEL VERSION
        try:
            print(f"DEBUG: Calling Gemini API with model=gemini-2.5-flash")
            response = self._client.models.generate_content_stream(
                model="gemini-2.5-flash",  # Match working implementation
                contents=contents,
                config=config,
            )

            # Yield chunks as they arrive
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    await asyncio.sleep(0.01)
                    
        except Exception as e:
            print(f"Gemini API error: {e}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            yield f"Sorry, I encountered an error: {str(e)}"

    async def generate_content(self, prompt: str, use_search_grounding: bool = False, system_instruction: Optional[str] = None) -> tuple[str, Optional[Any]]:
        """
        Generate a single text response (non-streaming).
        Supports Google Search Grounding via tools.
        Returns: (text, grounding_metadata)
        """
        try:
            tools = []
            if use_search_grounding:
                # Enable Google Search Retrieval tool
                # Must use Tool object, not string, for newer SDKs
                tools = [types.Tool(google_search={})]

            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=tools if tools else None, # Pass tools if not empty, otherwise None
                    temperature=0.7,
                    system_instruction=system_instruction
                )
            )
            
            # Extract grounding metadata if present
            metadata = None
            if response.candidates and response.candidates[0].grounding_metadata:
                # Convert to dict for easier serialization
                # The SDK object might need helper to convert to dict, but let's try returning the object or a simplified dict
                # For now, let's return the raw object and handle conversion in chat.py or here.
                # Actually, let's try to get the search_entry_point or grounding_chunks
                metadata = response.candidates[0].grounding_metadata
                
            return response.text, metadata
        except Exception as e:
            print(f"Generate content error: {e}")
            return "", None

    async def analyze_image(self, image: Any, prompt: str) -> str:
        """
        Analyze an image using Gemini Vision.
        Accepts base64 string or bytes.
        """
        try:
            # Prepare image data
            image_bytes = None
            mime_type = "image/png"

            if isinstance(image, str):
                if image.startswith("data:"):
                    # Extract base64
                    header, data = image.split(",", 1)
                    image_bytes = base64.b64decode(data)
                    if ":" in header and ";" in header:
                        mime_type = header.split(":")[1].split(";")[0]
                else:
                    # Assume raw base64 or file path (not supported here for simplicity, assume base64)
                    image_bytes = base64.b64decode(image)
            elif isinstance(image, bytes):
                image_bytes = image
            
            if not image_bytes:
                return "Error: Invalid image data"

            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=mime_type,
                                data=image_bytes
                            )
                        )
                    ]
                )
            ]

            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents
            )
            return response.text
        except Exception as e:
            print(f"Analyze image error: {e}")
            return f"Error analyzing image: {str(e)}"

    async def embed_content(self, text: str) -> List[float]:
        """
        Generate embeddings for text using Gemini
        """
        try:
            # Use text-embedding-004 model
            response = self._client.models.embed_content(
                model="text-embedding-004",
                contents=text,
            )
            return response.embeddings[0].values
        except Exception as e:
            print(f"Embedding error: {e}")
            return []


# Lazy singleton
_gemini_service_instance = None

def get_gemini_service() -> GeminiService:
    global _gemini_service_instance
    if _gemini_service_instance is None:
        _gemini_service_instance = GeminiService()
    return _gemini_service_instance

# For backward compatibility
gemini_service = get_gemini_service()

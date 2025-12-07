"""
PerplexityService wrapper for TradeBerg.

This module provides a thin, well-typed adapter around the existing
`perplexity_bot.services.perplexity_service` client.

Responsibilities:
- Accept a fully-built prompt string from TradeBergPromptService.
- Attach an appropriate system message (doctrine + mode hint).
- Call Perplexity's chat completion API.
- Yield the assistant content as a streaming sequence of text chunks.

IMPORTANT:
- This wrapper MUST NOT change the core doctrine. That is defined in
  `core.constants.TRADEBERG_DOCTRINE` and by the prompt builder.
"""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Dict, List, Optional

from core.constants import TRADEBERG_DOCTRINE

# We reuse the low-level Perplexity client from the existing module.
try:
    from perplexity_bot.services.perplexity_service import PerplexityService as _PerplexityClient
except Exception as exc:  # pragma: no cover - defensive import
    _PerplexityClient = None  # type: ignore
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


class PerplexityService:
    """
    High-level Perplexity adapter used by the chat pipeline.

    NOTE:
    - `prompt` here is already the full user-facing instruction string
      produced by TradeBergPromptService.
    - We still prepend TRADEBERG_DOCTRINE as a system message so the
      model sees it as privileged context.
    """

    def __init__(self) -> None:
        if _PerplexityClient is None:
            # Import failed – we keep this explicit so errors surface clearly.
            raise RuntimeError(f"Perplexity client import failed: {_IMPORT_ERROR!r}")
        self._client = _PerplexityClient()

    async def stream(
        self,
        *,
        prompt: str,
        mode: str,
        chart_image: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Call Perplexity and yield the assistant response as a stream of chunks.

        Parameters:
        - prompt: final user instruction text from TradeBergPromptService.
        - mode: high-level mode hint ("analysis", "chart", "general", etc).
        - chart_image: optional base64 string (without data URL prefix).
        - metadata: optional extra context (currently unused but reserved).

        Returns:
        - Async generator of text chunks (unicode strings).
        """
        # Build messages: doctrine as explicit system message, plus mode hint.
        system_content = f"""{TRADEBERG_DOCTRINE}

---

MODE: {mode}

- You MUST obey all constraints in the doctrine above.
- The following USER message already includes structured instructions
  and context; follow them exactly while staying within the doctrine.
"""

        messages: List[Dict] = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ]

        image_data = chart_image or None

        # Call the low-level Perplexity client.
        # We bypass its own system prompts and build our own messages.
        api_response = await self._client.call_perplexity_api(
            messages=messages,
            model=None,
            temperature=None,
            max_tokens=None,
        )

        # Parse response to get main content.
        content, _citations, _related, _tokens = self._client.parse_response(api_response)
        text = content or ""

        # Stream text out in small chunks so the frontend can animate typing.
        chunk_size = 64
        for i in range(0, len(text), chunk_size):
            chunk = text[i : i + chunk_size]
            if not chunk:
                continue
            yield chunk
            # Tiny delay for more natural streaming; tune as needed.
            await asyncio.sleep(0.01)


# Singleton-style instance for convenience
perplexity_service = PerplexityService()



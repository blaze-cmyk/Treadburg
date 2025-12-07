"""
FormatterService
----------------

Responsible for light, non-destructive post-processing of markdown
coming back from the LLM.

Rules:
- NEVER add hype, extra narrative, or marketing language.
- NEVER change headings, sections, or semantic content.
- ONLY perform mechanical cleanup (whitespace, duplicated newlines, etc.).
"""

from __future__ import annotations

from typing import AsyncGenerator, Iterable


class FormatterService:
    """
    Minimal markdown cleaner.

    We keep this intentionally conservative so we do not accidentally
    change the meaning of the model's output.
    """

    async def clean_stream(
        self, stream: AsyncGenerator[str, None]
    ) -> AsyncGenerator[str, None]:
        """
        Wrap an async text stream and yield cleaned chunks.

        Currently we:
        - normalise CRLF to LF
        - avoid emitting empty all-whitespace chunks
        """
        async for raw in stream:
            if raw is None:
                continue
            text = str(raw).replace("\r\n", "\n").replace("\r", "\n")
            # Skip chunks that are just whitespace
            if not text.strip():
                continue
            yield text


# Singleton-style instance for convenience
formatter_service = FormatterService()



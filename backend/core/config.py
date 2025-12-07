"""
Core config wrapper.

We keep the original `config.Settings` but centralize access here so
new services can import from `core.config` instead of reaching into
the root module directly.
"""

from config import settings  # re-export

__all__ = ["settings"]



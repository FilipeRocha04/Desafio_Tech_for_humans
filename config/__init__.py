"""Módulo de configuração."""
from .settings import (
    LLM_PROVIDER,
    LLM_MODEL,
    LLM_TEMPERATURE,
    MAX_AUTH_ATTEMPTS,
    OPENAI_API_KEY,
    TAVILY_API_KEY,
    STREAMLIT_PORT,
    STREAMLIT_HOST,
)

__all__ = [
    "LLM_PROVIDER",
    "LLM_MODEL",
    "LLM_TEMPERATURE",
    "MAX_AUTH_ATTEMPTS",
    "OPENAI_API_KEY",
    "TAVILY_API_KEY",
    "STREAMLIT_PORT",
    "STREAMLIT_HOST",
]

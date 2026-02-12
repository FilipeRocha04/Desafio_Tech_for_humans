"""Configurações centralizadas da aplicação."""
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# CONFIGURAÇÕES DE LLM
# ============================================================================

LLM_PROVIDER = os.getenv("PROVIDER", "openai")
LLM_MODEL = os.getenv("MODEL_NAME", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

# ============================================================================
# CONFIGURAÇÕES DE AUTENTICAÇÃO
# ============================================================================

MAX_AUTH_ATTEMPTS = int(os.getenv("MAX_AUTH_ATTEMPTS", "2"))

# ============================================================================
# CONFIGURAÇÕES DE API
# ============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# ============================================================================
# CONFIGURAÇÕES DO STREAMLIT
# ============================================================================

STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
STREAMLIT_HOST = os.getenv("STREAMLIT_HOST", "0.0.0.0")

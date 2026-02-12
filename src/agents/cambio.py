from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from src.tools.tavily import (cotacao, encerramento)
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent / "prompts"

def carregar_prompt_cambio(nome_arquivo: str) -> str:
    caminho = BASE_DIR / nome_arquivo
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()



def cria_agente_cambio():
    
    system_prompt = carregar_prompt_cambio("cambio.md")

    tools = [
        cotacao,
        encerramento
    ]

    agente = create_agent(
        model=ChatOpenAI(model="gpt-4.1-mini", temperature=0.2),
        tools=tools,
        system_prompt=system_prompt
    )

    return agente


agente_cambio = cria_agente_cambio()

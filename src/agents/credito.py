from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from src.tools.credito import (consultar_limite, finalizar_atendimento,solicitar_aumento_limite)
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent / "prompts"

def carregar_prompt_credito(nome_arquivo: str) -> str:
    caminho = BASE_DIR / nome_arquivo
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

def cria_agente_credito():
    

    system_prompt_credito = carregar_prompt_credito("credito.md")

    tools = [
        consultar_limite,
        solicitar_aumento_limite,
        finalizar_atendimento
    ]

    
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    agente = create_agent(
        model=llm_with_tools,
        tools=tools,
        system_prompt=system_prompt_credito
    )

    return agente


agente_credito = cria_agente_credito()
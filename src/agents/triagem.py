from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from src.tools.triagem import (autenticar_cliente,finalizar_atendimento)
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent / "prompts"

def carregar_prompt_triagem(nome_arquivo: str) -> str:
    caminho = BASE_DIR / nome_arquivo
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()

def cria_agente_triagem():
   

    system_prompt_triagem = carregar_prompt_triagem("triagem.md")

    tools = [autenticar_cliente,finalizar_atendimento]
  
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    agente = create_agent(
        model=llm_with_tools,
        tools=tools,
        system_prompt=system_prompt_triagem
    )

    return agente


agente_triagem = cria_agente_triagem()
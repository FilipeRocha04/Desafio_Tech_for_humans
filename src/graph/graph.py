import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import re
import json
import traceback
from typing_extensions import TypedDict, Annotated
from uuid import uuid4
from typing import Literal
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command
from langchain_openai import ChatOpenAI

from src.agents.triagem import agente_triagem
from src.agents.credito import agente_credito
from src.agents.entrevista import agente_entrevista
from src.agents.cambio import agente_cambio
from pathlib import Path
from config import LLM_MODEL, LLM_TEMPERATURE, MAX_AUTH_ATTEMPTS

BASE_PATH = Path(__file__).parent.parent / "prompts"
def load_prompt(filename: str) -> str:
    with open(BASE_PATH / filename, "r", encoding="utf-8") as f:
        return f.read()
SYSTEM_PROMPT_SUPERVISOR = load_prompt("supervisor.md")


class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]
    is_authenticated: bool
    current_agent: str
    supervisor_reasoning: str
    client_cpf: str  
    client_name: str  
    auth_attempts: int  


# ============================================================================
# SCHEMA ESTRUTURADO DO SUPERVISOR
# ============================================================================

class SupervisorDecision(BaseModel):
    """Decisão estruturada do supervisor com explicação."""
    agent: Literal["triagem", "credito", "entrevista", "cambio"] = Field(
        description="Qual agente deve lidar com o request"
    )
    reasoning: str = Field(
        description="Explicação detalhada de POR QUE esse agente foi escolhido"
    )
    should_end: bool = Field(
        default=False,
        description="True se o atendimento deve ser finalizado, False caso contrário"
    )


# ============================================================================
# SUPERVISOR NODE COM STRUCTURED OUTPUT
# ============================================================================

def supervisor_node(state: ConversationState) -> Command:
    """
    Supervisor LLM que retorna decisão estruturada com motivo.
    """

    # ✅ VALIDAÇÃO: Se não está autenticado, FORÇA triagem
    if not state["is_authenticated"]:
        reasoning = "Usuário não autenticado - acesso restrito a triagem para autenticação"
 
        
        return Command(
            update={
                "current_agent": "triagem",
                "supervisor_reasoning": reasoning
            },
            goto="triagem_node",
        )
    
    # ✅ Se chegou aqui = está autenticado, usa LLM com structured output
    llm = ChatOpenAI(model=LLM_MODEL, temperature=LLM_TEMPERATURE)
    
    # 🔑 STRUCTURED OUTPUT: O LLM retorna SupervisorDecision com agent + reasoning
    llm_structured = llm.with_structured_output(SupervisorDecision)
    
    response = llm_structured.invoke([
        {"role": "system", "content": SYSTEM_PROMPT_SUPERVISOR},
        *state["messages"],
    ])
    
    agent = response.agent
    reasoning = response.reasoning
    should_end = response.should_end

    # ✅ SE LLM decidiu encerrar
    if should_end:
      
        
        return Command(
            update={
                "messages": state["messages"] + [AIMessage(
                    content="Obrigado por usar nossos serviços! Até logo! 👋"
                )],
                "current_agent": "supervisor",
                "supervisor_reasoning": "Encerramento solicitado",
            },
            goto=END  # 🔴 ENCERRA O GRAFO
        )
    
    # Caso normal: roteia para agente
    return Command(
        update={
            "current_agent": agent,
            "supervisor_reasoning": reasoning,
        },
        goto=f"{agent}_node",
    )


# ============================================================================
# AGENT NODES
# ============================================================================

def triagem_node(state: ConversationState) -> Command:
    """Triagem: autentica; se decidir handoff, vai direto para o nó alvo."""

    #Agente de triagem
    result = agente_triagem.invoke({
        "messages": state["messages"],
        "is_authenticated": state["is_authenticated"]
    })
    messages = result["messages"]
    last = messages[-1].content

    # Detecta autenticação bem-sucedida NESTA RODADA
    newly_authenticated = (
        "bem-sucedida" in last.lower() or
        "autenticado" in last.lower() or
        "__client_data__:" in last.lower()
    )

    # Extrair dados do cliente se autenticado
    client_cpf = state.get("client_cpf", "")
    client_name = state.get("client_name", "")
    auth_attempts = state.get("auth_attempts", 0)

    if newly_authenticated and "__CLIENT_DATA__:" in last:
        # Extrair JSON com dados do cliente
        match = re.search(r'__CLIENT_DATA__:(\{.*?\})', last)
        if match:
            try:
                client_data = json.loads(match.group(1))
                client_cpf = client_data.get("cpf", "")
                client_name = client_data.get("nome", "")
                # Limpar a mensagem removendo o JSON
                clean_last = last[:match.start()].strip()
                messages = messages[:-1] + [AIMessage(content=clean_last)]
            except json.JSONDecodeError:
                pass

    # Verificar se houve falha na autenticação
    if not newly_authenticated and not state["is_authenticated"]:
        if "incorretos" in last.lower() or "❌" in last:
            auth_attempts += 1

            # Se excedeu o número de tentativas, encerrar
            if auth_attempts >= MAX_AUTH_ATTEMPTS:
                return Command(
                    update={
                        "messages": messages + [AIMessage(
                            content=f"Como você está com dificuldade para autenticar, "
                                    f"por segurança, o atendimento será encerrado. Por favor, entre em contato com nossa central."
                        )],
                        "is_authenticated": False,
                        "current_agent": "triagem",
                        "supervisor_reasoning": "Limite de tentativas de autenticação excedido",
                        "client_cpf": "",
                        "client_name": "",
                        "auth_attempts": auth_attempts
                    },
                    goto=END
                )

    # ✅ PRESERVA: Se já estava autenticado OU acabou de autenticar
    is_auth = state["is_authenticated"] or newly_authenticated

    # Se triagem decidir handoff explicitamente via marcador, salta direto
    if "##HANDOFF_PARA_" in last.upper():
        m = re.search(r'##HANDOFF_PARA_(\w+)##', last, flags=re.IGNORECASE)
        if m:
            target = m.group(1).lower()
            clean = last.replace(m.group(0), "").strip()

            return Command(
                update={
                    "messages": messages[:-1] + [AIMessage(content=clean)],
                    "is_authenticated": is_auth,
                    "current_agent": target,
                    "supervisor_reasoning": f"Handoff direto de triagem para {target}",
                    "client_cpf": client_cpf,
                    "client_name": client_name,
                    "auth_attempts": auth_attempts
                },
                goto=f"{target}_node",
            )

    # Caso padrão: retorna resposta e aguarda próximo input
    return Command(
        update={
            "messages": messages,
            "is_authenticated": is_auth,
            "current_agent": "triagem",
            "supervisor_reasoning": "Triagem processando",
            "client_cpf": client_cpf,
            "client_name": client_name,
            "auth_attempts": auth_attempts
        },
        goto=END,
    )


# Criar agente de handoff
def _make_agent_node(agent, name):
    """Factory para criar nós dos agentes."""
    def node(state: ConversationState) -> Command:
        # Preparar mensagens com contexto do cliente
        agent_messages = state["messages"].copy()

        # Injetar informações do cliente no contexto se autenticado
        if state.get("is_authenticated") and state.get("client_cpf"):
            context_message = HumanMessage(
                content=f"[CONTEXTO DO SISTEMA - NÃO MENCIONE ISSO AO CLIENTE]\n"
                        f"CPF do cliente: {state['client_cpf']}\n"
                        f"Nome do cliente: {state['client_name']}\n"
                        f"[FIM DO CONTEXTO]"
            )
            # Inserir contexto no início (após mensagens de sistema)
            agent_messages = [agent_messages[0]] + [context_message] + agent_messages[1:] if len(agent_messages) > 0 else [context_message]

        result = agent.invoke({"messages": agent_messages})
        messages = result["messages"]
        last = messages[-1].content

        # Se o agente emitir marcador de handoff, salta direto
        if "##HANDOFF_PARA_" in last.upper():
            m = re.search(r'##HANDOFF_PARA_(\w+)##', last, flags=re.IGNORECASE)
            if m:
                target = m.group(1).lower()
                clean = last.replace(m.group(0), "").strip()

                # Validação de autenticação
                if target != "triagem" and not state["is_authenticated"]:
                    return Command(
                        update={
                            "messages": messages[:-1] + [AIMessage(
                                content=f"Desculpe, você precisa estar autenticado para acessar o agente de {target}. "
                                        f"Por favor, complete a autenticação primeiro.\n\n{clean}"
                            )],
                            "current_agent": name,
                            "supervisor_reasoning": "🚫 Acesso negado - usuário não autenticado"
                        },
                        goto=END
                    )

                return Command(
                    update={
                        "messages": messages[:-1] + [AIMessage(content=clean)],
                        "current_agent": target,
                        "supervisor_reasoning": f"Handoff de {name} para {target}"
                    },
                    goto=f"{target}_node",
                )

        # Resposta normal
        return Command(
            update={
                "messages": messages,
                "current_agent": name,
                "supervisor_reasoning": f"{name.upper()} processou o request"
            },
            goto=END
        )

    return node


# ============================================================================
# GRAPH BUILDER
# ============================================================================

def build_graph():
    """Compila o grafo com supervisor inteligente."""
    graph = StateGraph(ConversationState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("triagem_node", triagem_node)
    graph.add_node("credito_node", _make_agent_node(agente_credito, "credito"))
    graph.add_node("entrevista_node", _make_agent_node(agente_entrevista, "entrevista"))
    graph.add_node("cambio_node", _make_agent_node(agente_cambio, "cambio"))

    graph.add_edge(START, "supervisor")
    
    graph.add_edge("triagem_node", END)
    graph.add_edge("credito_node", END)
    graph.add_edge("entrevista_node", END)
    graph.add_edge("cambio_node", END)

    return graph.compile(checkpointer=MemorySaver())



def main():
    compiled_graph = build_graph()

    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    current_state = None
    
    while True:
        try:
            user_input = input("👤 Você: ").strip()

            if user_input.lower() in {"sair", "exit", "quit"}:
                break
            
            if not user_input:
                continue

            # Inicializa ou atualiza o estado
            if current_state is None:
                current_state = {
                    "messages": [HumanMessage(content=user_input)],
                    "is_authenticated": False,
                    "current_agent": "supervisor",
                    "supervisor_reasoning": "",
                    "client_cpf": "",
                    "client_name": "",
                    "auth_attempts": 0
                }
            else:
                current_state["messages"] = current_state["messages"] + [HumanMessage(content=user_input)]

            # Executa uma rodada do grafo
            current_state = compiled_graph.invoke(current_state, config=config)

            # Exibe resultado
            print(f"\n🤖 Sistema: {current_state['messages'][-1].content}\n")

            # ✅ VERIFICAR SE DEVE ENCERRAR
            if "##FINALIZA_ATENDIMENTO##" in current_state['messages'][-1].content:
                break

            # Fallback para mensagens antigas
            if "Até logo" in current_state['messages'][-1].content or "Obrigado por usar" in current_state['messages'][-1].content:
                break

        except KeyboardInterrupt:
            break
        except Exception as e:
            traceback.print_exc()
            break




if __name__ == "__main__":
    main()
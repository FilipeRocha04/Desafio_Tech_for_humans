from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import pandas as pd
from datetime import datetime
import os
import json
from src.utils.data_utils import load_clientes_db

@tool
def autenticar_cliente(cpf: str, data_nascimento: str) -> str:
    """Autentica cliente contra base de dados.

    Args:
        cpf: CPF do cliente (formato: 000.000.000-00 ou 00000000000)
        data_nascimento: Data de nascimento (formato: DD/MM/YYYY)

    Returns:
        String indicando sucesso ou falha na autenticação
    """
    try:
        # Normalizar CPF (remover pontos e hífens)
        cpf_clean = cpf.replace(".", "").replace("-", "").strip()

        # Normalizar data de nascimento (converter DD/MM/YYYY para YYYY-MM-DD)
        if "/" in data_nascimento:
            # Formato DD/MM/YYYY
            parts = data_nascimento.split("/")
            if len(parts) == 3:
                data_nascimento_csv = f"{parts[2]}-{parts[1]}-{parts[0]}"  # YYYY-MM-DD
            else:
                return "❌ Formato de data inválido. Use DD/MM/YYYY"
        else:
            # Assumir que já está em YYYY-MM-DD
            data_nascimento_csv = data_nascimento

        # Carregar base
        df = load_clientes_db()

        # Converter coluna cpf para string para comparação
        df["cpf"] = df["cpf"].astype(str)

        # Buscar cliente
        client = df[(df["cpf"] == cpf_clean) & (df["data_nascimento"] == data_nascimento_csv)]

        if len(client) > 0:
            # Extrair dados do cliente
            nome = client.iloc[0]["nome"]
            score = int(client.iloc[0].get("score", 600))
            limite_credito = float(client.iloc[0].get("limite_credito", 5000))

            # Retornar mensagem de sucesso com dados em JSON no final
            client_data_json = json.dumps({
                "cpf": cpf_clean,
                "nome": nome,
                "score": score,
                "limite_credito": limite_credito,
                "authenticated": True
            })

            return f"✅ Autenticação bem-sucedida! Bem-vindo(a), {nome}!\n__CLIENT_DATA__:{client_data_json}"
        else:
            return "❌ CPF ou data de nascimento incorretos. Tente novamente."
    except Exception as e:
        return f"❌ Erro ao autenticar: {str(e)}"

@tool
def finalizar_atendimento() -> str:
    """Encerra o atendimento de triagem quando o cliente não precisa de mais nada."""
    return "🙏 Obrigado por escolher o **Banco Ágil**! Foi um prazer atendê-lo. Tenha um excelente dia! 👋\n\n##FINALIZAR_ATENDIMENTO##"
from langchain.tools import tool
import pandas as pd
from datetime import datetime
import os
from src.utils.data_utils import load_clientes_db, save_clientes_db


@tool
def calculo_e_atualizacao_score(
    cpf: str,
    renda_mensal: float,
    tipo_emprego: str,
    despesas_fixas: float,
    num_dependentes: int,
    tem_dividas: str
) -> str:
    """Realiza avaliação financeira do cliente e atualiza o score automaticamente."""

    try:
        # ----------------------------
        # Validações básicas
        # ----------------------------
        if renda_mensal < 0 or despesas_fixas < 0:
            return "❌ Valores de renda e despesas devem ser positivos."


        # Normalização para aceitar variações
        tipo_emprego_normalizado = tipo_emprego.strip().lower()
        if tipo_emprego_normalizado in {"autonomo", "autónomo", "informal"}:
            tipo_emprego_normalizado = "autônomo"
        elif tipo_emprego_normalizado in {"formal", "desempregado"}:
            pass
        else:
            return "❌ Tipo de emprego inválido."

        tipos_validos = {"formal", "autônomo", "desempregado"}
        if tipo_emprego_normalizado not in tipos_validos:
            return "❌ Tipo de emprego inválido."

        if tem_dividas not in {"sim", "não"}:
            return "❌ Campo de dívidas deve ser 'sim' ou 'não'."

        # ----------------------------
        # Definição de pesos
        # ----------------------------
        multiplicador_renda = 30

        mapa_emprego = {
            "formal": 300,
            "autônomo": 200,
            "desempregado": 0
        }

        mapa_dependentes = {
            0: 100,
            1: 80,
            2: 60,
            3: 30
        }

        mapa_dividas = {
            "sim": -100,
            "não": 100
        }

        # ----------------------------
        # Cálculo do score
        # ----------------------------

        indice_renda = (renda_mensal / (despesas_fixas + 1)) * multiplicador_renda
        impacto_emprego = mapa_emprego.get(tipo_emprego_normalizado, 0)

        dependentes_ajustado = num_dependentes if num_dependentes < 3 else 3
        impacto_dependentes = mapa_dependentes.get(dependentes_ajustado, 30)

        impacto_dividas = mapa_dividas.get(tem_dividas, 0)

        score_calculado = indice_renda + impacto_emprego + impacto_dependentes + impacto_dividas
        novo_score = int(max(0, min(1000, score_calculado)))

        # ----------------------------
        # Atualização na base
        # ----------------------------
        cpf_tratado = cpf.replace(".", "").replace("-", "").strip()
        base_clientes = load_clientes_db()

        if base_clientes.empty:
            return "❌ Não foi possível acessar a base de clientes."

        base_clientes["cpf"] = base_clientes["cpf"].astype(str)
        cliente_encontrado = base_clientes[base_clientes["cpf"] == cpf_tratado]

        if cliente_encontrado.empty:
            return f"❌ Cliente com CPF {cpf_tratado} não localizado."

        indice_cliente = cliente_encontrado.index[0]
        score_antigo = int(base_clientes.loc[indice_cliente, "score"])
        nome_cliente = base_clientes.loc[indice_cliente, "nome"]

        base_clientes.loc[indice_cliente, "score"] = novo_score
        save_clientes_db(base_clientes)

        variacao = novo_score - score_antigo

        # ----------------------------
        # Montagem da resposta
        # ----------------------------
        resposta = (
            f"📊 **Resultado da Avaliação de Crédito**\n\n"
            f"Cliente: {nome_cliente}\n"
            f"CPF: {cpf_tratado}\n"
            f"Score anterior: {score_antigo}\n"
            f"Score atualizado: {novo_score}/1000\n"
            f"Variação: {variacao:+d} pontos\n\n"
            f"🔎 Detalhamento do cálculo:\n"
            f"- Relação renda/despesas: +{int(indice_renda)}\n"
            f"- Emprego ({tipo_emprego}): +{impacto_emprego}\n"
            f"- Dependentes ({dependentes_ajustado}): +{impacto_dependentes}\n"
            f"- Dívidas ({tem_dividas}): {impacto_dividas:+d}\n"
        )

        # Interpretação
        if novo_score < 600:
            resposta += "\n📌 Perfil classificado como risco elevado."
        elif novo_score < 700:
            resposta += "\n📌 Perfil moderado com potencial de melhoria."
        elif novo_score < 800:
            resposta += "\n📌 Perfil considerado bom para concessão."
        else:
            resposta += "\n📌 Perfil excelente para crédito."

        resposta += f"\n\n🕒 Registro atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

        return resposta

    except Exception as erro:
        return f"❌ Falha ao processar avaliação: {erro}"


@tool
def finaliza_entrevista() -> str:
    """Finaliza a etapa de entrevista e prepara transição."""
    return "✅ Entrevista concluída com sucesso. Encaminhando para análise de crédito."


@tool
def finaliza_atendimento() -> str:
    """Finaliza completamente o atendimento."""
    return (
        "📋 Atendimento de entrevista finalizado.\n\n"
        "Agradecemos sua participação. Até breve! 👋\n\n"
        "##FINALIZA_ATENDIMENTO##"
    )

from langchain.tools import tool
from datetime import datetime
from src.utils.data_utils import (load_clientes_db,load_score_limite,save_clientes_db,append_to_csv)

# ================================
# UTILITÁRIOS INTERNOS
# ================================

def _normalizar_cpf(cpf: str) -> str:
    return cpf.replace(".", "").replace("-", "").strip()

def _buscar_cliente_por_cpf(df, cpf: str):
    df["cpf"] = df["cpf"].astype(str)
    return df[df["cpf"] == cpf]

def _formatar_valor(valor: float) -> str:
    return f"R$ {valor:,.2f}"

# ================================
# CONSULTA DE LIMITE
# ================================

@tool
def consultar_limite(cpf: str) -> str:
    """Retorna informações de limite e score do cliente."""

    try:
        cpf_limpo = _normalizar_cpf(cpf)
        print(f"[DEBUG] CPF recebido: {cpf} | CPF limpo: {cpf_limpo}")
        clientes = load_clientes_db()

        if clientes.empty:
            return "❌ Não foi possível acessar a base de clientes."

        registro = _buscar_cliente_por_cpf(clientes, cpf_limpo)
        print(f"[DEBUG] DataFrame filtrado por CPF:\n{registro}")

        if registro.empty:
            return "❌ Cliente não localizado."


        dados = registro.iloc[0]
        nome = dados.get("nome", "Cliente")
        limite = float(dados.get("limite"))
        score = int(dados.get("score", 600))

        return (
            f"💳 **Resumo de Crédito — {nome}**\n\n"
            f"• Limite disponível: {_formatar_valor(limite)}\n"
            f"• Score atual: {score}\n"
            f"• Situação: Ativa\n\n"
            "Deseja solicitar um aumento ou precisa de outra informação?"
        )

    except Exception as err:
        return f"❌ Falha ao consultar limite: {err}"


@tool
def solicitar_aumento_limite(cpf: str, novo_limite: float) -> str:
    """Solicita aumento de limite de crédito.

    Args:
        cpf: CPF do cliente
        novo_limite: Novo limite desejado (ex: 15000)

    Returns:
        Status da solicitação (aprovada/rejeitada)
    """
    try:
        cpf_clean = cpf.replace(".", "").replace("-", "").strip()
        df_clientes = load_clientes_db()
        df_score_limite = load_score_limite()

        if df_clientes.empty:
            return "❌ Base de dados não encontrada."

        # Converter CPF para string para comparação
        df_clientes["cpf"] = df_clientes["cpf"].astype(str)
        cliente = df_clientes[df_clientes["cpf"] == cpf_clean]
        
        if len(cliente) == 0:
            return "❌ Cliente não encontrado."
        
        # Extrair dados do cliente
        score = int(cliente.iloc[0].get("score"))
        limite_atual = float(cliente.iloc[0].get("limite"))
        nome = cliente.iloc[0]["nome"]
        
        # Validar novo limite
        if novo_limite <= limite_atual:
            return f"⚠️ O novo limite deve ser maior que o limite atual de R$ {limite_atual:,.2f}"
        
        # Verificar se score permite este limite
        limite_permitido = None
        for _, row in df_score_limite.iterrows():
            if row["score_min"] <= score <= row["score_max"]:
                limite_permitido = row["limite_max"]
                break
        
        if limite_permitido is None:
            limite_permitido = 4000
        
        # Determinar status
        status = "aprovado" if novo_limite <= limite_permitido else "rejeitado"
        
        # ✅ SE APROVADO: Atualizar o limite no clientes.csv
        if status == "aprovado":
            # Encontrar o índice do cliente
            idx = df_clientes[df_clientes["cpf"] == cpf_clean].index
            
            if len(idx) > 0:
                # Atualizar o limite_credito
                df_clientes.loc[idx[0], "limite"] = novo_limite
                
                # Salvar no arquivo CSV
                save_clientes_db(df_clientes)
        
        # Registrar solicitação no CSV
        solicitacao_data = {
            "cpf_cliente": cpf_clean,
            "data_hora_solicitacao": datetime.now().isoformat(),
            "limite_atual": limite_atual,
            "novo_limite_solicitado": novo_limite,
            "status_pedido": status
        }
        
        # Adicionar ao arquivo CSV
        append_to_csv("data/solicitacoes_aumento_limite.csv", solicitacao_data)
        
        # Preparar resposta
        if status == "aprovado":
            return f"""✅ **Solicitação de Aumento de Limite APROVADA!**

Cliente: {nome}
Limite Anterior: R$ {limite_atual:,.2f}
Novo Limite: R$ {novo_limite:,.2f}
Score: {score}

Seu novo limite está ativo! Você pode começar a usar imediatamente."""
        else:
            return f"""❌ **Solicitação de Aumento de Limite REJEITADA**

Cliente: {nome}
Limite Solicitado: R$ {novo_limite:,.2f}
Limite Máximo Permitido: R$ {limite_permitido:,.2f}
Score: {score}

Seu score de crédito ({score}) não permite este limite no momento.
💡 Dica: Você gostaria de fazer uma entrevista de crédito para tentar melhorar seu score?"""
    
    except Exception as e:
        return f"❌ Erro ao processar solicitação: {str(e)}"

@tool
def finalizar_atendimento() -> str:
    """Encerra o atendimento de crédito quando o cliente não precisa de mais nada."""
    return "💳 Obrigado por escolher nosso serviço de **Crédito**! Foi um prazer ajudar você. Tenha um excelente dia! 👋\n\n##FINALIZAR_ATENDIMENTO##"
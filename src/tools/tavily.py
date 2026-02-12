from langchain.tools import tool
from tavily import TavilyClient
import os
import re
from decimal import Decimal, InvalidOperation

# Inicializar cliente Tavily
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def cotacao(origem_cotacao: str, destino_cotacao: str, amount: float = 1.0) -> str:
    """
    Busca a cotação atual entre duas moedas utilizando Tavily
    e realiza conversão opcional de valor.
    """

    try:
        #  Validação inicial
        if not origem_cotacao or not destino_cotacao:
            return (
                "❗ Parâmetros inválidos.\n"
                "Informe a moeda base e a moeda de conversão "
                "(ex: USD BRL ou EUR USD)."
            )

        # Normalização
        f = origem_cotacao.strip().upper()
        t = destino_cotacao.strip().upper()

        if f == t:
            return "⚠️ A moeda de origem e destino são iguais."

        # Query otimizada
        query = f"cotação atual {f} para {t} hoje taxa de conversão"

        response = tavily.search(
            query=query,
            search_depth="basic",
            max_results=1,
            include_answer=True,
            include_domains=[
                "investing.com",
                "google.com/finance",
                "uol.com.br",
                "xe.com"
            ]
        )

        if not response:
            return "❌ Não foi possível consultar a cotação no momento."

        resultado = f"💱 **Cotação {f} → {t}**\n\n"

        taxa = None

        # 📊 Extrair resposta resumida
        if response.get("answer"):
            answer = response["answer"]
            resultado += f"📊 {answer}\n\n"

            # 🔍 Regex mais segura para taxa
            taxa_match = re.search(r'\b\d{1,4}[.,]\d{2,6}\b', answer)

            if taxa_match:
                try:
                    taxa = Decimal(taxa_match.group(0).replace(",", "."))
                except InvalidOperation:
                    taxa = None

        # 💰 Conversão
        if taxa and amount:
            valor_convertido = Decimal(str(amount)) * taxa
            resultado += (
                f"💰 **Conversão:**\n"
                f"{amount:,.2f} {f} ≈ {valor_convertido:,.2f} {t}\n\n"
            )

        # 🔗 Fontes
        if response.get("results"):
            resultado += "🔗 **Fontes:**\n"
            for idx, item in enumerate(response["results"][:2], 1):
                titulo = item.get("title", "Fonte")
                url = item.get("url", "")
                resultado += f"{idx}. {titulo}\n   {url}\n"

        if not response.get("answer") and not response.get("results"):
            return f"❌ Não encontrei cotação disponível para {f}/{t}."

        return resultado.strip()

    except Exception as e:
        return f"❌ Erro ao consultar cotação: {str(e)}"


@tool
def encerramento() -> str:
    """Encerra o atendimento de câmbio."""
    return (
        "💱 Obrigado por utilizar nosso serviço de **Câmbio**.\n"
        "Se precisar de novas cotações, estou à disposição! 👋\n\n"
        "##FINALIZAR_ATENDIMENTO##"
    )

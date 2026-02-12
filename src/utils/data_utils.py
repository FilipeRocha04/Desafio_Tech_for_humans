import pandas as pd
import os
import csv
from typing import Dict, Any


# =========================
# UTILITÁRIOS DE ARQUIVO
# =========================

def load_csv_as_df(filepath: str) -> pd.DataFrame:
    """Lê um CSV e retorna um DataFrame vazio caso o arquivo não exista."""
    try:
        if not os.path.isfile(filepath):
            return pd.DataFrame()
        return pd.read_csv(filepath)
    except Exception:
        return pd.DataFrame()


# =========================
# CLIENTES
# =========================

def load_clientes_db() -> pd.DataFrame:
    """Retorna a base de clientes."""
    caminho = os.path.join("data", "clientes.csv")
    return load_csv_as_df(caminho)


def save_clientes_db(df: pd.DataFrame) -> None:
    """Persiste a base de clientes no CSV."""
    caminho = os.path.join("data", "clientes.csv")
    df.to_csv(caminho, index=False)


# =========================
# SCORE x LIMITE
# =========================

def load_score_limite() -> pd.DataFrame:
    """Carrega a tabela de regras de score para limite."""
    caminho = os.path.join("data", "score_limite.csv")
    tabela = load_csv_as_df(caminho)

    if tabela.empty:
        # Estrutura padrão caso o arquivo ainda não exista
        tabela_padrao = pd.DataFrame(
            [
                {"score_min": 0, "score_max": 699, "limite_max": 5000},
                {"score_min": 700, "score_max": 799, "limite_max": 10000},
                {"score_min": 800, "score_max": 899, "limite_max": 15000},
                {"score_min": 900, "score_max": 1000, "limite_max": 40000},
            ]
        )
        return tabela_padrao

    return tabela


# =========================
# APPEND GENÉRICO
# =========================

def append_to_csv(filepath: str, data: Dict[str, Any]) -> None:
    """Acrescenta um registro ao CSV informado."""
    diretorio = os.path.dirname(filepath)

    if diretorio:
        os.makedirs(diretorio, exist_ok=True)

    arquivo_existe = os.path.isfile(filepath)

    with open(filepath, mode="a", newline="", encoding="utf-8") as arquivo:
        campos = list(data.keys())
        escritor = csv.DictWriter(arquivo, fieldnames=campos)

        if not arquivo_existe:
            escritor.writeheader()

        escritor.writerow(data)

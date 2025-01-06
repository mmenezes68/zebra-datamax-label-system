import os
import json
import pandas as pd
from fractions import Fraction
import chardet

# Caminho para o arquivo JSON com os modelos de etiquetas
caminho_json = "/Applications/MAMP/htdocs/ZPL_estudos/etiquetas_config.json"

def carregar_modelos():
    """Carrega os modelos de etiquetas do arquivo JSON."""
    if not os.path.exists(caminho_json):
        print(f"Erro: Arquivo JSON de modelos não encontrado em {caminho_json}.")
        return None
    with open(caminho_json, "r") as f:
        return json.load(f)

def detectar_codificacao(arquivo):
    """Detecta a codificação do arquivo CSV."""
    try:
        with open(arquivo, "rb") as f:
            resultado = chardet.detect(f.read())
        return resultado["encoding"]
    except Exception as e:
        print(f"Erro ao detectar codificação do arquivo: {e}")
        return None

def carregar_arquivo(caminho):
    """
    Carrega os dados de um arquivo CSV ou Excel.

    :param caminho: Caminho do arquivo.
    :return: DataFrame com os dados ou None em caso de erro.
    """
    try:
        if caminho.endswith(".csv"):
            codificacao = detectar_codificacao(caminho)
            if not codificacao:
                print("Não foi possível detectar a codificação do arquivo CSV.")
                return None
            return pd.read_csv(caminho, encoding=codificacao)
        elif caminho.endswith((".xls", ".xlsx")):
            return pd.read_excel(caminho)
        else:
            print("Erro: O arquivo deve ser CSV ou Excel.")
            return None
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return None

def selecionar_colunas(df):
    """
    Permite a seleção de colunas de um DataFrame.

    :param df: DataFrame com os dados.
    :return: Lista de etiquetas geradas a partir das colunas selecionadas.
    """
    try:
        # Exibir colunas disponíveis
        print("\nColunas disponíveis no arquivo:")
        for idx, coluna in enumerate(df.columns, start=1):
            print(f"{idx}. {coluna}")

        # Solicitar colunas a serem usadas
        escolha = input("Digite os números das colunas para as etiquetas, separados por vírgulas: ").strip()
        indices = [int(num.strip()) - 1 for num in escolha.split(",")]

        # Validar seleção
        if any(idx < 0 or idx >= len(df.columns) for idx in indices):
            print("Um ou mais números selecionados são inválidos.")
            return None

        # Criar lista de etiquetas combinando as colunas selecionadas
        colunas_selecionadas = df.iloc[:, indices].fillna("").astype(str)
        etiquetas = colunas_selecionadas.apply(" - ".join, axis=1).tolist()
        print(f"Colunas selecionadas: {[df.columns[idx] for idx in indices]}")
        return etiquetas
    except Exception as e:
        print(f"Erro ao selecionar colunas: {e}")
        return None

def carregar_dados(caminho):
    """
    Carrega os dados de um arquivo e permite a seleção de colunas para gerar etiquetas.

    :param caminho: Caminho do arquivo.
    :return: Lista de etiquetas e o DataFrame carregado.
    """
    df = carregar_arquivo(caminho)
    if df is None:
        print("Erro ao carregar o arquivo. Verifique o caminho e o formato.")
        return None, None

    etiquetas = selecionar_colunas(df)
    if etiquetas is None:
        print("Erro ao selecionar colunas. Tente novamente.")
        return None, None

    return etiquetas, df

    etiquetas = selecionar_colunas(df)
    if etiquetas is None:
        print("Erro ao selecionar colunas. Tente novamente.")
        return None, None

    return etiquetas, df
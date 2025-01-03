import os
import json
import pandas as pd
from fractions import Fraction

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
    import chardet
    with open(arquivo, "rb") as f:
        resultado = chardet.detect(f.read())
    return resultado["encoding"]

def carregar_dados(caminho):
    """Carrega os dados de um arquivo CSV ou Excel e exibe as colunas disponíveis."""
    try:
        if caminho.endswith(".csv"):
            codificacao = detectar_codificacao(caminho)
            df = pd.read_csv(caminho, encoding=codificacao)
        elif caminho.endswith((".xls", ".xlsx")):
            df = pd.read_excel(caminho)
        else:
            print("Erro: O arquivo deve ser CSV ou Excel.")
            return None, None

        # Exibir colunas disponíveis
        print("\nColunas disponíveis no arquivo:")
        for idx, coluna in enumerate(df.columns, start=1):
            print(f"{idx}. {coluna}")

        # Solicitar colunas a serem usadas
        escolha = input("Digite os números das colunas para as etiquetas, separados por vírgulas: ").strip()
        indices = [int(num.strip()) - 1 for num in escolha.split(",")]

        if any(idx < 0 or idx >= len(df.columns) for idx in indices):
            print("Opção inválida. Saindo...")
            return None, None

        # Criar lista de etiquetas combinando as colunas selecionadas
        colunas_selecionadas = df.iloc[:, indices].fillna("").astype(str)
        etiquetas = colunas_selecionadas.apply(" - ".join, axis=1).tolist()
        return etiquetas, df
    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
        return None, None
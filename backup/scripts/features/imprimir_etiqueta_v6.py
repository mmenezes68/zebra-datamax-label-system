import json
import os
import tempfile
import pandas as pd
import subprocess
from scripts.utils.printer import selecionar_impressora

# Caminho para o arquivo de modelos JSON
caminho_json = "/Applications/MAMP/htdocs/ZPL_estudos/config/etiquetas_config.json"


def carregar_modelos():
    """Carrega os modelos de etiquetas do arquivo JSON."""
    print(f"[LOG] Tentando carregar modelos de: {caminho_json}\n")
    if not os.path.exists(caminho_json):
        print(f"[ERRO] Arquivo JSON não encontrado: {caminho_json}\n")
        return None
    try:
        with open(caminho_json, "r") as f:
            modelos = json.load(f)
        print(f"[LOG] Modelos carregados com sucesso: {list(modelos.keys())}\n")
        return modelos
    except Exception as e:
        print(f"[ERRO] Erro ao carregar modelos: {e}\n")
        return None


def carregar_dados(caminho):
    """Carrega dados de um arquivo CSV ou Excel."""
    print(f"[LOG] Carregando dados do arquivo: {caminho}\n")
    try:
        if caminho.endswith(".csv"):
            df = pd.read_csv(caminho)
        elif caminho.endswith((".xls", ".xlsx")):
            df = pd.read_excel(caminho)
        else:
            print(f"[ERRO] Formato de arquivo não suportado: {caminho}\n")
            return None
        print(f"[LOG] Dados carregados com sucesso. {len(df)} linhas disponíveis.\n")
        return df
    except Exception as e:
        print(f"[ERRO] Erro ao carregar o arquivo: {e}\n")
        return None


def gerar_zpl(etiquetas, modelo, copias):
    """Gera código ZPL para as etiquetas selecionadas."""
    largura = modelo["largura"]
    altura = modelo["altura"]
    espaco = modelo["espaco"]
    colunas = modelo["colunas"]
    largura_total = modelo["largura_total"]
    posicoes_horizontais = modelo["posicoes_horizontais"]

    zpl_code = ""
    for idx, etiqueta in enumerate(etiquetas * copias):
        coluna_atual = idx % colunas
        if coluna_atual == 0:
            if idx > 0:
                zpl_code += "^XZ\n"
            zpl_code += f"^XA\n^PW{int(largura_total)}\n^LL{int(altura)}\n^CI28\n"

        x_atual = posicoes_horizontais[coluna_atual]
        y_atual = 30
        zpl_code += f"^FO{x_atual},{y_atual}^FB{int(largura)},5,L,10,0^A0N,30,20^FD{etiqueta}^FS\n"

    zpl_code += "^XZ\n"
    return zpl_code


def salvar_zpl_temp(zpl_code):
    """Salva o ZPL em um arquivo temporário."""
    print("[LOG] Salvando ZPL em arquivo temporário...\n")
    try:
        arquivo_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".zpl").name
        with open(arquivo_temp, "w") as f:
            f.write(zpl_code)
        print(f"[LOG] Arquivo ZPL salvo em: {arquivo_temp}\n")
        return arquivo_temp
    except Exception as e:
        print(f"[ERRO] Erro ao salvar o arquivo ZPL: {e}\n")
        return None


def selecionar_etiquetas(etiquetas):
    """Permite que o usuário selecione etiquetas para impressão."""
    print("[LOG] Exibindo etiquetas numeradas:")
    for idx, etiqueta in enumerate(etiquetas, start=1):
        print(f"{idx}. {etiqueta}")
    print("Selecione as etiquetas:")
    print("- Use números separados por vírgula (ex: 1,3,5)")
    print("- Use range (ex: 1-10)")
    print("- Digite 'todos' para selecionar todas")

    escolha = input("Sua escolha: ").strip().lower()
    try:
        if escolha == "todos":
            return etiquetas
        elif "-" in escolha:
            inicio, fim = map(int, escolha.split("-"))
            return etiquetas[inicio - 1 : fim]
        else:
            indices = map(int, escolha.split(","))
            return [etiquetas[i - 1] for i in indices]
    except (ValueError, IndexError):
        print("[ERRO] Seleção inválida. Tente novamente.\n")
        return selecionar_etiquetas(etiquetas)


def main():
    print("[LOG] Iniciando o script...\n")

    # Carregar modelos
    modelos = carregar_modelos()
    if not modelos:
        return

    print("Modelos disponíveis:")
    for idx, nome in enumerate(modelos.keys(), start=1):
        print(f"{idx}. {nome}")
    modelo_idx = int(input("Escolha um modelo pelo número: ").strip()) - 1
    modelo = list(modelos.values())[modelo_idx]

    # Escolher origem dos dados
    print("\nEscolha a origem dos dados (1: Manual, 2: Arquivo): ", end="")
    origem = input().strip()

    etiquetas = []
    if origem == "1":
        print("[LOG] Inserindo etiquetas manualmente. Digite uma etiqueta por linha (deixe vazio para finalizar):\n")
        while True:
            etiqueta = input("> ").strip()
            if not etiqueta:
                break
            etiquetas.append(etiqueta)

        if not etiquetas:
            print("[ERRO] Nenhuma etiqueta foi inserida. Encerrando...\n")
            return

        etiquetas_selecionadas = etiquetas
        copias = int(input("\nDigite o número de cópias para cada etiqueta: ").strip())

    elif origem == "2":
        caminho = input("Digite o caminho do arquivo CSV ou Excel: ").strip()
        df = carregar_dados(caminho)
        if df is None:
            return
        print("\nColunas disponíveis no arquivo:")
        for idx, col in enumerate(df.columns, start=1):
            print(f"{idx}. {col}")
        colunas = input("Digite os números das colunas desejadas (separados por vírgula): ").strip()
        indices = [int(x) - 1 for x in colunas.split(",")]
        etiquetas = df.iloc[:, indices].apply(lambda row: " | ".join(map(str, row)), axis=1).tolist()

        etiquetas_selecionadas = selecionar_etiquetas(etiquetas)
        copias = int(input("\nDigite o número de cópias para cada etiqueta: ").strip())

    else:
        print("[ERRO] Opção inválida.\n")
        return

    # Gerar e salvar ZPL
    zpl_code = gerar_zpl(etiquetas_selecionadas, modelo, copias)
    if not zpl_code:
        return
    arquivo_temp = salvar_zpl_temp(zpl_code)
    if not arquivo_temp:
        return

    # Selecionar impressora
    impressora = selecionar_impressora()
    if not impressora:
        print("[ERRO] Impressora não selecionada. Encerrando o programa.\n")
        return

    # Enviar para impressão
    print(f"[LOG] Enviando ZPL para a impressora: {impressora}\n")
    try:
        subprocess.run(["lp", "-d", impressora, "-o", "raw", arquivo_temp], check=True)
        print("[LOG] Impressão enviada com sucesso.\n")
    except Exception as e:
        print(f"[ERRO] Erro ao enviar para impressão: {e}\n")


if __name__ == "__main__":
    main()
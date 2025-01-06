import os
import json
import pandas as pd
from fractions import Fraction
import subprocess

# Caminho para o arquivo JSON com os modelos de etiquetas
caminho_json = "/Applications/MAMP/htdocs/ZPL_estudos/etiquetas_config.json"

# Funções auxiliares
def detectar_codificacao(arquivo):
    """Detecta a codificação do arquivo CSV."""
    import chardet
    with open(arquivo, "rb") as f:
        resultado = chardet.detect(f.read())
    return resultado["encoding"]

def polegadas_para_pontos(valor):
    """Converte valores em polegadas (incluindo fracionários) para pontos ZPL."""
    try:
        if " " in valor:
            inteiro, fracao = valor.split(" ")
            return (int(inteiro) + float(Fraction(fracao))) * 72
        return float(valor) * 72
    except Exception as e:
        print(f"Erro ao converter polegadas: {e}")
        return None

def mm_para_pontos(valor):
    """Converte valores em milímetros para pontos ZPL."""
    return float(valor) * 2.83465

def listar_impressoras():
    """Lista impressoras disponíveis no macOS."""
    try:
        resultado = subprocess.check_output("lpstat -p", shell=True, text=True)
        impressoras = []
        for linha in resultado.split("\n"):
            if "impressora" in linha:
                nome = linha.split()[1]
                impressoras.append(nome)
        return impressoras if impressoras else None
    except subprocess.CalledProcessError:
        return None

def selecionar_impressora():
    """Permite ao usuário selecionar uma impressora."""
    impressoras = listar_impressoras()
    if impressoras:
        print("\nImpressoras disponíveis:")
        for idx, nome in enumerate(impressoras, start=1):
            print(f"{idx}. {nome}")
        escolha = input("Escolha uma impressora pelo número: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(impressoras):
            return impressoras[int(escolha) - 1]
        else:
            print("Opção inválida. Nenhuma impressora será selecionada.")
            return None
    else:
        print("Nenhuma impressora foi encontrada. Digite o nome manualmente.")
        return input("Nome da impressora: ").strip()

def carregar_modelos():
    """Carrega os modelos de etiquetas do arquivo JSON."""
    if not os.path.exists(caminho_json):
        with open(caminho_json, "w") as f:
            json.dump({}, f)
    with open(caminho_json, "r") as f:
        return json.load(f)

def carregar_dados(caminho):
    """Carrega os dados de um arquivo CSV ou Excel."""
    try:
        if caminho.endswith(".csv"):
            codificacao = detectar_codificacao(caminho)
            df = pd.read_csv(caminho, encoding=codificacao)
        elif caminho.endswith((".xls", ".xlsx")):
            df = pd.read_excel(caminho)
        else:
            print("Erro: O arquivo deve ser CSV ou Excel.")
            return None, None

        print("\nColunas disponíveis no arquivo:")
        for idx, coluna in enumerate(df.columns, start=1):
            print(f"{idx}. {coluna}")

        escolha = input("Digite os números das colunas para as etiquetas, separados por vírgulas: ").strip()
        indices = [int(num.strip()) - 1 for num in escolha.split(",")]

        if any(idx < 0 or idx >= len(df.columns) for idx in indices):
            print("Opção inválida. Saindo...")
            return None, None

        colunas_selecionadas = df.iloc[:, indices].fillna("").astype(str)
        etiquetas = colunas_selecionadas.apply(" - ".join, axis=1).tolist()
        return etiquetas, df
    except Exception as e:
        print(f"Erro ao carregar os dados: {e}")
        return None, None

def gerar_zpl(etiquetas, modelo):
    """Gera o código ZPL para as etiquetas fornecidas."""
    largura = modelo["largura"]
    altura = modelo["altura"]
    colunas = modelo["colunas"]
    largura_total = modelo["largura_total"]
    posicoes_horizontais = modelo["posicoes_horizontais"]

    zpl_code = "^XA\n"
    zpl_code += f"^PW{int(largura_total)}\n"
    zpl_code += f"^LL{int(altura)}\n"
    zpl_code += "^CI28\n"

    for idx, etiqueta in enumerate(etiquetas):
        coluna = idx % colunas
        x_atual = posicoes_horizontais[coluna]
        y_atual = 30
        zpl_code += f"^FO{x_atual},{y_atual}^FB{int(largura)},5,L,10,0^A0N,30,20^FD{etiqueta}^FS\n"
        if coluna == colunas - 1:
            zpl_code += "^XZ\n^XA\n"

    zpl_code += "^XZ"
    return zpl_code

def imprimir_zpl(arquivo_zpl, impressora):
    """Envia o arquivo ZPL para a impressora selecionada."""
    comando = f"lp -d {impressora} -o raw {arquivo_zpl}"
    resultado = os.system(comando)
    if resultado == 0:
        print("Impressão enviada com sucesso.")
    else:
        print("Erro ao enviar para a impressora.")

def imprimir_opcoes(etiquetas, df):
    """Oferece opções de impressão seletiva."""
    print("\nResumo das etiquetas disponíveis:")
    for idx, row in df.iterrows():
        if len(df.columns) > 1:
            print(f"{idx + 1}. {row[0]} - {row[1]}")
        else:
            print(f"{idx + 1}. {row[0]}")

    print("\nOpções de impressão:")
    print("1. Imprimir tudo.")
    print("2. Imprimir um intervalo.")
    print("3. Selecionar etiquetas específicas.")
    escolha = input("Digite sua escolha: ").strip()

    if escolha == "1":
        return etiquetas
    elif escolha == "2":
        intervalo = input("Digite o intervalo (ex.: 1-3): ").strip()
        inicio, fim = map(int, intervalo.split("-"))
        return etiquetas[inicio - 1:fim]
    elif escolha == "3":
        especificos = input("Digite os números das etiquetas separadas por vírgulas: ").strip()
        indices = [int(num.strip()) - 1 for num in especificos.split(",")]
        return [etiquetas[idx] for idx in indices]
    else:
        print("Opção inválida. Nenhuma etiqueta será impressa.")
        return []

def main():
    modelos = carregar_modelos()
    if not modelos:
        print("Nenhum modelo encontrado no arquivo JSON.")
        return

    print("\nModelos disponíveis:")
    for idx, nome in enumerate(modelos.keys(), start=1):
        print(f"{idx}. {nome}")

    escolha = int(input("Escolha um modelo pelo número: ").strip())
    modelo = modelos[list(modelos.keys())[escolha - 1]]

    print("\nEscolha a origem dos dados:")
    print("1. Inserir etiquetas manualmente.")
    print("2. Carregar etiquetas de um arquivo CSV ou Excel.")
    origem = int(input("Digite 1 ou 2: ").strip())

    if origem == 1:
        etiquetas = []
        while True:
            etiqueta = input("Digite o conteúdo da etiqueta: ").strip()
            if etiqueta:
                etiquetas.append(etiqueta)
            if input("Deseja inserir outra etiqueta? (s/n): ").strip().lower() == "n":
                break
        df = pd.DataFrame({"Etiquetas": etiquetas})
    elif origem == 2:
        caminho = input("Digite o caminho completo do arquivo: ").strip()
        etiquetas, df = carregar_dados(caminho)
        if not etiquetas:
            print("Erro ao carregar etiquetas.")
            return
    else:
        print("Opção inválida. Saindo...")
        return

    etiquetas_selecionadas = imprimir_opcoes(etiquetas, df)
    if not etiquetas_selecionadas:
        print("Nenhuma etiqueta foi selecionada.")
        return

    impressora = selecionar_impressora()
    if not impressora:
        print("Nenhuma impressora foi selecionada.")
        return

    zpl_code = gerar_zpl(etiquetas_selecionadas, modelo)
    arquivo_zpl = f"{list(modelos.keys())[escolha - 1]}_etiquetas.zpl"

    with open(arquivo_zpl, "w") as f:
        f.write(zpl_code)

    print(f"Arquivo ZPL gerado com sucesso: {arquivo_zpl}")
    print("\nZPL Gerado:")
    print(zpl_code)

    imprimir_zpl(arquivo_zpl, impressora)

if __name__ == "__main__":
    main()
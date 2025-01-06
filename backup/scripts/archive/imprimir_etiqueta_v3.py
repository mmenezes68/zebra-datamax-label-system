import os
import json
import pandas as pd
from fractions import Fraction

# Caminho para o arquivo JSON com os modelos de etiquetas
caminho_json = "/Applications/MAMP/htdocs/ZPL_estudos/etiquetas_config.json"

# Funções de conversão e manipulação de dados
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

def carregar_modelos():
    """Carrega os modelos de etiquetas do arquivo JSON."""
    if not os.path.exists(caminho_json):
        with open(caminho_json, "w") as f:
            json.dump({}, f)
    with open(caminho_json, "r") as f:
        return json.load(f)

def salvar_modelos(modelos):
    """Salva os modelos de etiquetas no arquivo JSON."""
    with open(caminho_json, "w") as f:
        json.dump(modelos, f, indent=4)

def carregar_dados(caminho):
    """Carrega os dados do arquivo CSV ou Excel e valida as colunas."""
    try:
        if caminho.endswith(".csv"):
            codificacao = detectar_codificacao(caminho)
            df = pd.read_csv(caminho, encoding=codificacao)
        elif caminho.endswith((".xls", ".xlsx")):
            df = pd.read_excel(caminho)
        else:
            print("Erro: Arquivo deve ser CSV ou Excel.")
            return None

        print("\nColunas disponíveis no arquivo:")
        for idx, coluna in enumerate(df.columns, start=1):
            print(f"{idx}. {coluna}")

        escolha = input("Digite o(s) número(s) da(s) coluna(s) que contém os dados das etiquetas (separados por vírgula): ").strip()
        try:
            indices = [int(num.strip()) - 1 for num in escolha.split(",")]
            if any(idx < 0 or idx >= len(df.columns) for idx in indices):
                print("Opção inválida. Saindo...")
                return None

            colunas_escolhidas = [df.columns[idx] for idx in indices]
            print(f"Colunas escolhidas: {', '.join(colunas_escolhidas)}")

            etiquetas = df[colunas_escolhidas].fillna("").astype(str).apply(" - ".join, axis=1).tolist()
            if not etiquetas:
                print("As colunas selecionadas não contêm dados válidos.")
                return None

            return etiquetas, df
        except ValueError:
            print("Erro ao processar os números das colunas. Certifique-se de usar números válidos separados por vírgulas.")
            return None, None
    except Exception as e:
        print(f"Erro ao carregar o arquivo: {e}")
        return None, None

def gerar_zpl(etiquetas, modelo):
    largura = modelo["largura"]
    altura = modelo["altura"]
    espaco = modelo["espaco"]
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

def inserir_etiquetas():
    """Permite inserir etiquetas manualmente."""
    etiquetas = []
    while True:
        etiqueta = input("Digite o conteúdo da etiqueta: ").strip()
        if etiqueta:
            etiquetas.append(etiqueta)
        continuar = input("Deseja inserir outra etiqueta? (s/n): ").strip().lower()
        if continuar == "n":
            break
    return etiquetas

def imprimir_opcoes(etiquetas, df):
    """Oferece opções de impressão (lote completo, intervalo ou etiquetas específicas)."""
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
        try:
            inicio, fim = map(int, intervalo.split("-"))
            return etiquetas[inicio - 1:fim]
        except ValueError:
            print("Intervalo inválido.")
            return []
    elif escolha == "3":
        especificos = input("Digite os números das etiquetas separadas por vírgulas: ").strip()
        try:
            indices = [int(num.strip()) - 1 for num in especificos.split(",")]
            return [etiquetas[idx] for idx in indices]
        except ValueError:
            print("Entrada inválida.")
            return []
    else:
        print("Opção inválida. Nenhuma etiqueta será impressa.")
        return []

def main():
    modelos = carregar_modelos()
    if not modelos:
        print("Nenhum modelo encontrado no arquivo JSON. Verifique o arquivo.")
        return

    print("\nModelos disponíveis:")
    for idx, nome in enumerate(modelos.keys(), start=1):
        print(f"{idx}. {nome}")

    escolha = input("Escolha um modelo pelo número: ").strip()
    if not escolha.isdigit() or int(escolha) < 1 or int(escolha) > len(modelos):
        print("Opção inválida. Saindo...")
        return

    nome_modelo = list(modelos.keys())[int(escolha) - 1]
    modelo = modelos[nome_modelo]
    print(f"Modelo selecionado: {nome_modelo}")

    print("\nEscolha a origem dos dados:")
    print("1. Inserir etiquetas manualmente.")
    print("2. Carregar etiquetas de um arquivo de dados (CSV ou Excel).")
    origem = input("Digite 1 ou 2: ").strip()

    if origem == "1":
        etiquetas = inserir_etiquetas()
        df = pd.DataFrame({"Etiquetas": etiquetas})
    elif origem == "2":
        caminho = input("Digite o caminho completo do arquivo: ").strip()
        etiquetas, df = carregar_dados(caminho)
        if etiquetas is None:
            print("Erro ao carregar os dados. Saindo...")
            return
    else:
        print("Opção inválida. Saindo...")
        return

    if not etiquetas:
        print("Nenhuma etiqueta fornecida. Saindo...")
        return

    etiquetas_selecionadas = imprimir_opcoes(etiquetas, df)
    if not etiquetas_selecionadas:
        print("Nenhuma etiqueta foi selecionada. Saindo...")
        return

    zpl_code = gerar_zpl(etiquetas_selecionadas, modelo)

    arquivo_saida = f"{nome_modelo}_etiquetas.zpl"
    with open(arquivo_saida, "w") as f:
        f.write(zpl_code)

    print(f"Arquivo ZPL gerado com sucesso: {arquivo_saida}")
    print("\nZPL Gerado:")
    print(zpl_code)

if __name__ == "__main__":
    main()
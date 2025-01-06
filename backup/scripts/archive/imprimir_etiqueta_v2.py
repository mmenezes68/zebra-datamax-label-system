import os
import pandas as pd
import chardet
from fractions import Fraction


def detecta_codificacao(arquivo):
    """Detecta a codificação do arquivo."""
    with open(arquivo, 'rb') as f:
        resultado = chardet.detect(f.read())
    return resultado['encoding']


def polegadas_para_pontos(valor):
    """Converte valores em polegadas (incluindo fracionários) para pontos ZPL."""
    try:
        if " " in valor:  # Trata valores como '2 1/2'
            inteiro, fracao = valor.split(" ")
            return (int(inteiro) + float(Fraction(fracao))) * 72
        return float(valor) * 72
    except Exception as e:
        print(f"Erro ao converter polegadas: {e}")
        return None


def mm_para_pontos(valor):
    """Converte milímetros para pontos ZPL."""
    return float(valor) * 2.83465


def configurar_midia():
    """Configura as especificações da mídia."""
    print("Escolha a unidade de medida:")
    print("1. Milímetros (mm)")
    print("2. Polegadas (in, aceita valores fracionários como '2 1/2')")
    
    while True:
        escolha = input("Digite 1 ou 2: ").strip()
        if escolha not in ("1", "2"):
            print("Opção inválida. Escolha 1 ou 2.")
            continue
        unidade = "mm" if escolha == "1" else "in"
        break

    print(f"As medidas serão configuradas em {unidade}.")
    largura = input("Digite a largura da etiqueta: ").strip()
    altura = input("Digite a altura da etiqueta: ").strip()
    espaco = input("Digite o espaço (gap) entre etiquetas: ").strip()
    colunas = input("Digite o número de colunas de etiquetas: ").strip()

    try:
        if unidade == "mm":
            largura_pontos = mm_para_pontos(largura)
            altura_pontos = mm_para_pontos(altura)
            espaco_pontos = mm_para_pontos(espaco)
        else:
            largura_pontos = polegadas_para_pontos(largura)
            altura_pontos = polegadas_para_pontos(altura)
            espaco_pontos = polegadas_para_pontos(espaco)
        colunas = int(colunas)
        return largura_pontos, altura_pontos, espaco_pontos, colunas
    except ValueError:
        print("Entrada inválida. Certifique-se de inserir valores numéricos.")
        return configurar_midia()


def carregar_arquivo():
    """Carrega o arquivo CSV ou Excel e exibe as colunas."""
    while True:
        caminho = input("Digite o caminho completo do arquivo (CSV ou Excel): ").strip()
        if not os.path.isfile(caminho):
            print("Erro: O arquivo especificado não foi encontrado.")
            continue
        try:
            if caminho.endswith(".csv"):
                codificacao = detecta_codificacao(caminho)
                df = pd.read_csv(caminho, encoding=codificacao)
            elif caminho.endswith((".xls", ".xlsx")):
                df = pd.read_excel(caminho)
            else:
                print("Erro: O arquivo deve ser CSV ou Excel.")
                continue

            print("\nColunas disponíveis no arquivo:")
            for idx, coluna in enumerate(df.columns, start=1):
                print(f"{idx}. {coluna}")
            return df
        except Exception as e:
            print(f"Erro ao carregar o arquivo: {e}")
            continue


def selecionar_colunas(df):
    """Seleciona uma ou mais colunas do DataFrame."""
    while True:
        try:
            escolha = input(
                "Digite os números correspondentes às colunas desejadas, separados por vírgulas: "
            ).strip()
            indices = [int(num.strip()) - 1 for num in escolha.split(",")]
            if all(0 <= idx < len(df.columns) for idx in indices):
                return [df.columns[idx] for idx in indices]
            else:
                print("Número fora do intervalo. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Certifique-se de inserir números separados por vírgulas.")


def gerar_zpl(df, colunas, largura, altura, espaco, colunas_layout):
    """Gera arquivos ZPL e imprime etiquetas."""
    arquivos = []
    x_inicial, y_inicial = 50, 50
    x_atual, y_atual = x_inicial, y_inicial
    etiquetas_por_linha = colunas_layout
    contador_coluna = 0

    for idx, row in df.iterrows():
        conteudo = " - ".join(str(row[coluna]) for coluna in colunas)
        zpl = f"^XA\n^FO{x_atual},{y_atual}^ADN,36,20^FD{conteudo}^FS\n^XZ"
        arquivo_nome = f"etiqueta_{idx + 1}_{str(row[colunas[0]]).replace(' ', '_')}.zpl"
        caminho_zpl = os.path.join("/Applications/MAMP/htdocs/ZPL_estudos/etiquetas", arquivo_nome)

        with open(caminho_zpl, "w") as f:
            f.write(zpl)
        arquivos.append(caminho_zpl)

        contador_coluna += 1
        if contador_coluna < etiquetas_por_linha:
            x_atual += largura + espaco
        else:
            contador_coluna = 0
            x_atual = x_inicial
            y_atual += altura + espaco

    return arquivos


def imprimir_etiquetas(arquivos):
    """Envia os arquivos para impressão."""
    print("\nDeseja imprimir as etiquetas?")
    print("1. Todas")
    print("2. Intervalo")
    print("3. Selecionar específicas")
    print("4. Cancelar")
    escolha = input("Digite sua escolha: ").strip()

    if escolha == "1":
        for arquivo in arquivos:
            print(f"Imprimindo: {arquivo}")
            os.system(f"lpr {arquivo}")
    elif escolha == "2":
        intervalo = input("Digite o intervalo (ex.: 1-3): ").strip()
        try:
            inicio, fim = map(int, intervalo.split("-"))
            for arquivo in arquivos[inicio - 1 : fim]:
                print(f"Imprimindo: {arquivo}")
                os.system(f"lpr {arquivo}")
        except ValueError:
            print("Intervalo inválido.")
    elif escolha == "3":
        especificos = input("Digite os números das etiquetas separadas por vírgulas: ").strip()
        try:
            indices = [int(num.strip()) - 1 for num in especificos.split(",")]
            for idx in indices:
                print(f"Imprimindo: {arquivos[idx]}")
                os.system(f"lpr {arquivos[idx]}")
        except ValueError:
            print("Entrada inválida.")
    elif escolha == "4":
        print("Impressão cancelada.")


def main():
    os.makedirs("/Applications/MAMP/htdocs/ZPL_estudos/etiquetas", exist_ok=True)
    largura, altura, espaco, colunas_layout = configurar_midia()
    df = carregar_arquivo()
    colunas = selecionar_colunas(df)

    print("\nPré-visualização das etiquetas:")
    for idx, row in df.iterrows():
        conteudo = " - ".join(str(row[coluna]) for coluna in colunas)
        print(f"Etiqueta {idx + 1}: {conteudo}")

    arquivos = gerar_zpl(df, colunas, largura, altura, espaco, colunas_layout)
    print("\nArquivos ZPL gerados com sucesso:")
    for arquivo in arquivos:
        print(arquivo)

    imprimir_etiquetas(arquivos)


if __name__ == "__main__":
    main()
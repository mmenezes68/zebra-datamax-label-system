import os
import pandas as pd
import chardet
from fractions import Fraction


def polegadas_para_pontos(valor):
    """Converte valores em polegadas (incluindo fracionários) para pontos ZPL."""
    try:
        if " " in valor:  # Para tratar valores como '2 1/2'
            inteiro, fracao = valor.split(" ")
            return (int(inteiro) + float(Fraction(fracao))) * 72
        return float(Fraction(valor)) * 72
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
        if not caminho:
            print("Caminho não fornecido. Tente novamente.")
            continue

        if not caminho.endswith(('.csv', '.xls', '.xlsx')):
            print("Erro: O arquivo deve ser CSV ou Excel.")
            continue

        try:
            with open(caminho, 'rb') as f:
                codificacao = chardet.detect(f.read())['encoding']
            print(f"Codificação detectada: {codificacao}")

            if caminho.endswith('.csv'):
                df = pd.read_csv(caminho, encoding=codificacao)
            else:
                df = pd.read_excel(caminho)

            print("\nColunas disponíveis no arquivo:")
            for idx, coluna in enumerate(df.columns, start=1):
                print(f"{idx}. {coluna}")
            return df
        except Exception as e:
            print(f"Erro ao carregar o arquivo: {e}")
            continue


def selecionar_colunas(df):
    """Permite ao usuário selecionar múltiplas colunas do DataFrame."""
    while True:
        try:
            escolha = input("Digite os números correspondentes às colunas desejadas, separados por vírgulas: ").strip()
            indices = [int(num.strip()) - 1 for num in escolha.split(",")]

            if all(0 <= idx < len(df.columns) for idx in indices):
                return [df.columns[idx] for idx in indices]
            else:
                print("Um ou mais números estão fora do intervalo. Tente novamente.")
        except ValueError:
            print("Entrada inválida. Certifique-se de digitar números válidos separados por vírgulas.")


def selecionar_etiquetas(df):
    """Permite selecionar quais etiquetas imprimir."""
    print("\nOpções de impressão:")
    print("1. Imprimir todas as etiquetas.")
    print("2. Imprimir um intervalo de etiquetas.")
    print("3. Selecionar etiquetas específicas.")

    escolha = input("Digite sua escolha (1, 2 ou 3): ").strip()
    if escolha == "1":
        return df
    elif escolha == "2":
        intervalo = input("Digite o intervalo (ex.: 1-5): ").strip()
        try:
            inicio, fim = map(int, intervalo.split("-"))
            return df.iloc[inicio - 1:fim]
        except ValueError:
            print("Intervalo inválido. Imprimindo todas as etiquetas.")
            return df
    elif escolha == "3":
        indices = input("Digite os números das etiquetas separadas por vírgulas: ").strip()
        try:
            indices = [int(i.strip()) - 1 for i in indices.split(",")]
            return df.iloc[indices]
        except ValueError:
            print("Seleção inválida. Imprimindo todas as etiquetas.")
            return df
    else:
        print("Opção inválida. Retornando todas as etiquetas.")
        return df


def gerar_zpl(df, colunas, largura, altura, espaco, colunas_por_linha, copias=1):
    """Gera o código ZPL para as etiquetas."""
    x_inicial = 50
    y_inicial = 50
    y_atual = y_inicial
    x_atual = x_inicial
    contador_coluna = 0

    zpl_code = "^XA\n"

    for idx, row in df.iterrows():
        conteudo_etiqueta = " - ".join(str(row[coluna]) for coluna in colunas)
        for _ in range(copias):  # Repetir para o número de cópias
            zpl_code += f"^FO{x_atual},{y_atual}^ADN,36,20^FD{conteudo_etiqueta}^FS\n"

        contador_coluna += 1
        if contador_coluna < colunas_por_linha:
            x_atual += largura + espaco
        else:
            contador_coluna = 0
            x_atual = x_inicial
            y_atual += altura + espaco

    zpl_code += "^XZ"
    return zpl_code


def main():
    largura, altura, espaco, colunas_por_linha = configurar_midia()
    df = carregar_arquivo()
    colunas = selecionar_colunas(df)
    df_selecionado = selecionar_etiquetas(df)
    copias = int(input("Digite o número de cópias para cada etiqueta: ").strip())

    zpl_code = gerar_zpl(df_selecionado, colunas, largura, altura, espaco, colunas_por_linha, copias)
    print("\nZPL gerado:")
    print(zpl_code)

    with open("etiquetas.zpl", "w") as f:
        f.write(zpl_code)
    print("\nCódigo ZPL salvo em etiquetas.zpl.")


if __name__ == "__main__":
    main()
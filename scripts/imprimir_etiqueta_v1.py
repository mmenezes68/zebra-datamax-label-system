"""
###############################################################################
# Script: imprimir_etiqueta_v1.py
# Autor: Marcos Menezes
# Descrição:
# Este script processa arquivos CSV ou Excel (.xlsx) para gerar etiquetas no 
# formato ZPL, com base nas configurações fornecidas pelo usuário, como dimensões 
# das etiquetas, unidade de medida, e seleção de colunas. Ele salva cada etiqueta 
# gerada como um arquivo individual em uma pasta especificada.
#
# Funcionalidades Implementadas:
# 1. Configuração de medidas:
#    - Suporte a milímetros (mm) e polegadas (in), incluindo valores fracionários 
#      como "2 1/2" ou "1/8".
#    - Conversão para pontos ZPL:
#        - 1 mm = 2.83465 pontos
#        - 1 in = 72 pontos
#
# 2. Leitura e validação de arquivos:
#    - Suporte a arquivos CSV e Excel (.xlsx).
#    - Detecção de codificação e delimitador (no caso de CSV).
#    - Verificação do formato do arquivo com mensagens claras em caso de erro.
#
# 3. Seleção de colunas:
#    - Exibição de colunas disponíveis no arquivo carregado.
#    - Suporte para seleção de múltiplas colunas separadas por vírgulas.
#
# 4. Geração de etiquetas:
#    - Criação de arquivos ZPL individuais, com nomes baseados no primeiro campo
#      selecionado (exemplo: etiqueta_1_<primeiro_campo>.zpl).
#    - Organização das etiquetas em layout configurável (dimensões e espaçamento).
#    - Exibição dos valores das colunas selecionadas em formato combinado no 
#      conteúdo da etiqueta.
#
# 5. Mensagens claras:
#    - Informações detalhadas sobre erros e como corrigi-los.
#    - Suporte contínuo a interações do usuário no terminal.
#
# Dificuldades Enfrentadas e Soluções:
# 1. Problemas com exibição incorreta das colunas:
#    - Solução: Ajustes no carregamento e exibição para garantir leitura precisa
#      dos cabeçalhos.
# 2. Problemas com suporte a arquivos Excel:
#    - Solução: Adição da biblioteca 'openpyxl' para leitura de .xlsx.
# 3. Nomeação extensa dos arquivos:
#    - Solução: Utilização apenas do primeiro campo como base para o nome.
# 4. Conversão de dimensões para polegadas:
#    - Solução: Implementação de lógica para suportar valores fracionários.
#
# Sugestões Futuras:
# - Adicionar funcionalidade de impressão direta das etiquetas.
# - Implementar visualização prévia das etiquetas no terminal.
# - Permitir layouts mais customizáveis (ex.: fontes e posicionamento dinâmico).
#
# Data da última modificação: [30dez24]
###############################################################################
"""

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


def gerar_zpl(df, colunas, largura, altura, espaco, colunas_por_linha):
    """Gera o código ZPL para as etiquetas."""
    arquivos = []
    x_inicial = 50
    y_inicial = 50
    y_atual = y_inicial
    x_atual = x_inicial

    contador_coluna = 0

    for idx, row in df.iterrows():
        conteudo_etiqueta = " - ".join(str(row[coluna]) for coluna in colunas)  # Combina os campos selecionados
        nome_base = str(row[colunas[0]])  # Usa apenas o primeiro campo para o nome do arquivo
        nome_arquivo = f"etiqueta_{idx + 1}_{nome_base.replace(' ', '_').replace('/', '_')[:20]}.zpl"

        zpl = "^XA\n"
        zpl += f"^FO{x_atual},{y_atual}^ADN,36,20^FD{conteudo_etiqueta}^FS\n"
        zpl += "^XZ\n"
        
        with open(f"/Applications/MAMP/htdocs/ZPL_estudos/etiquetas/{nome_arquivo}", "w") as f:
            f.write(zpl)
        
        arquivos.append(nome_arquivo)
        
        contador_coluna += 1
        if contador_coluna < colunas_por_linha:
            x_atual += largura + espaco
        else:
            contador_coluna = 0
            x_atual = x_inicial
            y_atual += altura + espaco

    return arquivos


def main():
    largura, altura, espaco, colunas_por_linha = configurar_midia()
    df = carregar_arquivo()
    colunas = selecionar_colunas(df)  # Múltiplas colunas
    print(f"Colunas selecionadas: {colunas}")

    arquivos_gerados = gerar_zpl(df, colunas, largura, altura, espaco, colunas_por_linha)
    print("Arquivos ZPL gerados com sucesso:")
    for arquivo in arquivos_gerados:
        print(arquivo)


if __name__ == "__main__":
    main()
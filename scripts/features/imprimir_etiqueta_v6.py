import json
import sys
import os
import tempfile
import subprocess

# Ajuste para o caminho correto do arquivo JSON
caminho_json = "/Applications/MAMP/htdocs/ZPL_estudos/config/etiquetas_config.json"

# Adicionar o diretório scripts ao caminho de busca do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from scripts.core.zpl_generator import gerar_zpl  # Aqui é onde ocorre a importação
from scripts.core.loader import carregar_dados, carregar_modelos
from scripts.utils.printer import listar_impressoras, selecionar_impressora, imprimir_zpl

def carregar_modelos():
    """Carrega os modelos de etiquetas do arquivo JSON."""
    if not os.path.exists(caminho_json):
        print(f"Erro: Arquivo JSON de modelos não encontrado em {caminho_json}.")
        return None
    with open(caminho_json, "r") as f:
        return json.load(f)

def salvar_zpl_temp(zpl_code, arquivo_temp=None):
    """
    Salva o ZPL em um arquivo temporário ou no caminho especificado, sobrescrevendo o arquivo anterior.
    
    :param zpl_code: O código ZPL gerado.
    :param arquivo_temp: Caminho do arquivo temporário. Se None, cria um arquivo temporário.
    :return: Caminho do arquivo salvo.
    """
    try:
        if arquivo_temp is None:
            # Cria ou sobrescreve um arquivo temporário no diretório padrão do sistema
            arquivo_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".zpl", prefix="etiqueta_").name
        
        with open(arquivo_temp, "w") as f:
            f.write(zpl_code)
        print(f"Arquivo ZPL salvo em: {arquivo_temp}")
        return arquivo_temp
    except Exception as e:
        print(f"Erro ao salvar o arquivo ZPL: {e}")
        return None

def enviar_para_impressora(arquivo_zpl, impressora):
    """
    Envia o arquivo ZPL para a impressora selecionada.
    
    :param arquivo_zpl: Caminho do arquivo ZPL.
    :param impressora: Nome da impressora.
    :return: True se a impressão foi bem-sucedida, False caso contrário.
    """
    if not os.path.exists(arquivo_zpl) or os.path.getsize(arquivo_zpl) == 0:
        print(f"Erro: Arquivo ZPL '{arquivo_zpl}' não é válido ou está vazio.")
        return False

    comando = f"lp -d {impressora} -o raw {arquivo_zpl}"
    try:
        print(f"Executando comando: {comando}")
        resultado = subprocess.run(comando, shell=True, check=True)
        if resultado.returncode == 0:
            print(f"Impressão enviada com sucesso para a impressora '{impressora}'.")
            return True
        else:
            print(f"Erro ao enviar para a impressora '{impressora}'. Código de retorno: {resultado.returncode}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando lp: {e}")
        return False

def main():
    print("Executando a função main...")

    
    # Carregar modelos de etiquetas
    modelos = carregar_modelos()
    if not modelos:
        print("Nenhum modelo de etiqueta encontrado. Saindo...")
        return

    # Listar modelos disponíveis
    print("Modelos disponíveis:")
    for idx, nome in enumerate(modelos.keys(), start=1):
        print(f"{idx}. {nome}")
    
    try:
        escolha_modelo = int(input("Escolha um modelo pelo número: ").strip())
        if escolha_modelo not in range(1, len(modelos) + 1):
            raise ValueError
    except ValueError:
        print("Modelo inválido. Saindo...")
        return

    modelo_selecionado = list(modelos.keys())[escolha_modelo - 1]
    modelo = modelos[modelo_selecionado]
    print(f"Modelo selecionado: {modelo_selecionado}\n")

    # Escolha da origem dos dados
    print("Escolha a origem dos dados:")
    print("1. Inserir etiquetas manualmente.")
    print("2. Carregar etiquetas de um arquivo CSV ou Excel.")
    opcao_origem = input("Digite o número da sua escolha: ").strip()

    etiquetas = []
    if opcao_origem == "1":
        # Entrada manual
        while True:
            etiqueta = input("Digite o conteúdo da etiqueta (ou deixe vazio para finalizar): ").strip()
            if not etiqueta:
                break
            etiquetas.append(etiqueta)
        if not etiquetas:
            print("Nenhuma etiqueta foi inserida. Saindo...")
            return
    elif opcao_origem == "2":
        # Carregar de um arquivo
        caminho = input("Digite o caminho completo do arquivo CSV ou Excel: ").strip()
        if not caminho:
            print("Nenhum caminho fornecido. Saindo...")
            return
        etiquetas, _ = carregar_dados(caminho)
        if not etiquetas:
            print("Erro ao carregar etiquetas do arquivo. Saindo...")
            return
    else:
        print("Opção inválida. Saindo...")
        return

    # Solicitar o número de cópias
    try:
        copias = int(input("Digite o número de cópias para cada etiqueta: ").strip())
        if copias <= 0:
            raise ValueError
    except ValueError:
        print("Número de cópias inválido. Saindo...")
        return

    # Gerar ZPL
    zpl_code = gerar_zpl(etiquetas, modelo, copias)
    if not zpl_code:
        print("Erro ao gerar ZPL. Saindo...")
        return
    print("\nZPL Gerado:")
    print(zpl_code)

    # Salvar ZPL em arquivo temporário
    arquivo_temp = salvar_zpl_temp(zpl_code)
    if not arquivo_temp:
        print("Erro ao salvar o arquivo ZPL. Saindo...")
        return

    # Escolher impressora
    impressora = selecionar_impressora()
    if not impressora:
        print("Nenhuma impressora selecionada. Saindo...")
        return

    # Enviar para impressão
    if imprimir_zpl(arquivo_temp, impressora):
        print("Impressão concluída com sucesso.")
    else:
        print("Erro ao enviar ZPL para a impressora.")

if __name__ == "__main__":
    main()
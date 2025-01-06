import subprocess
import os
import logging

# Configuração de logging
logging.basicConfig(filename="impressao.log", level=logging.INFO)

def gerar_zpl(etiquetas, modelo, copias):
    largura = modelo["largura"]
    altura = modelo["altura"]
    espaco = modelo["espaco"]
    colunas = modelo["colunas"]
    largura_total = modelo["largura_total"]
    posicoes_horizontais = modelo["posicoes_horizontais"]

    zpl_code = ""
    linha_atual = 0

    for idx, etiqueta in enumerate(etiquetas * copias):
        coluna_atual = idx % colunas
        linha_atual = idx // colunas

        if coluna_atual == 0:
            if idx > 0:
                zpl_code += "^XZ\n"
            zpl_code += f"^XA\n^PW{int(largura_total)}\n^LL{int(altura)}\n^CI28\n"

        x_atual = posicoes_horizontais[coluna_atual]
        y_atual = 30

        zpl_code += f"^FO{x_atual},{y_atual}^FB{int(largura)},5,L,10,0^A0N,30,20^FD{etiqueta}^FS\n"

    zpl_code += "^XZ\n"
    return zpl_code

def listar_impressoras():
    """
    Lista impressoras disponíveis no macOS.
    :return: Lista de impressoras disponíveis ou None se não houver impressoras.
    """
    try:
        print("Executando comando lpstat para listar impressoras...")
        resultado = subprocess.check_output("lpstat -p", shell=True, text=True)
        impressoras = []
        for linha in resultado.split("\n"):
            print(f"Depuração linha: {linha}")  # Linha de depuração
            if "impressora" in linha:
                nome = linha.split()[1]
                impressoras.append(nome)
        return impressoras if impressoras else None
    except subprocess.CalledProcessError as e:
        print(f"Erro ao listar impressoras: {e}")
        return None


def selecionar_impressora():
    """
    Permite ao usuário selecionar uma impressora da lista disponível ou inserir manualmente.
    :return: Nome da impressora selecionada.
    """
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
        print("Nenhuma impressora foi encontrada.")
        impressora_manual = input("Digite o nome da impressora manualmente: ").strip()
        return impressora_manual if impressora_manual else None


def salvar_zpl_temp(zpl_code, arquivo_temp=None):
    """
    Salva o ZPL em um arquivo temporário ou no caminho especificado, sobrescrevendo o arquivo anterior.
    
    :param zpl_code: O código ZPL gerado.
    :param arquivo_temp: Caminho do arquivo temporário. Se None, cria um arquivo temporário.
    :return: Caminho do arquivo salvo.
    """
    try:
        if arquivo_temp is None:
            # Define o caminho para o arquivo temporário que será sobrescrito a cada nova geração
            arquivo_temp = "/Applications/MAMP/htdocs/ZPL_estudos/etiqueta_temp.zpl"

        # Sobrescreve o arquivo temporário com o novo código ZPL
        with open(arquivo_temp, "w") as f:
            f.write(zpl_code)
        
        print(f"Arquivo ZPL salvo em: {arquivo_temp}")
        return arquivo_temp
    except Exception as e:
        print(f"Erro ao salvar o arquivo ZPL: {e}")
        return None


def imprimir_zpl(arquivo_zpl, impressora):
    """
    Envia o código ZPL diretamente para a impressora selecionada.
    :param arquivo_zpl: Caminho para o arquivo ZPL.
    :param impressora: Nome da impressora selecionada.
    """
    if not os.path.exists(arquivo_zpl) or os.path.getsize(arquivo_zpl) == 0:
        print(f"Erro: Arquivo ZPL '{arquivo_zpl}' não encontrado ou está vazio.")
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


# Exemplo de uso independente:
if __name__ == "__main__":
    # Solicitar o código ZPL diretamente
    zpl_code = input("Digite o código ZPL para teste (ou cole o conteúdo): ").strip()

    # Selecionar impressora
    impressora = selecionar_impressora()
    if not impressora:
        print("Nenhuma impressora selecionada. Saindo...")
        exit(1)

    # Salvar ZPL no arquivo temporário
    arquivo_temp = salvar_zpl_temp(zpl_code)
    if arquivo_temp:
        # Enviar código ZPL para a impressora
        imprimir_zpl(arquivo_temp, impressora)
    else:
        print("Erro ao salvar o arquivo ZPL. Saindo...")
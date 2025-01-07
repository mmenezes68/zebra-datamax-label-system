import os
import json
import subprocess

# Caminho para o arquivo JSON com os modelos de etiquetas
caminho_json = "/Applications/MAMP/htdocs/ZPL_estudos/etiquetas_config.json"

def carregar_modelos():
    """Carrega os modelos de etiquetas do arquivo JSON."""
    if not os.path.exists(caminho_json):
        print(f"Erro: Arquivo JSON de modelos não encontrado em {caminho_json}.")
        return None
    with open(caminho_json, "r") as f:
        return json.load(f)

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
        print("Nenhuma impressora foi encontrada.")
        return None

def gerar_zpl(etiquetas, modelo, copias):
    """
    Gera o código ZPL para as etiquetas fornecidas, respeitando o número de colunas e ajustando ao sensor.
    """
    largura = modelo["largura"]
    altura = modelo["altura"]
    espaco = modelo["espaco"]
    colunas = modelo["colunas"]
    largura_total = modelo["largura_total"]
    posicoes_horizontais = modelo["posicoes_horizontais"]

    zpl_code = ""
    linha_atual = 0

    for idx, etiqueta in enumerate(etiquetas * copias):
        coluna_atual = idx % colunas  # Define a coluna atual
        linha_atual = idx // colunas  # Define a linha atual

        if coluna_atual == 0:  # Início de uma nova linha (novo bloco para o sensor)
            if idx > 0:  # Fecha o bloco anterior
                zpl_code += "^XZ\n"
            # Inicia um novo bloco com a altura ajustada para a linha
            zpl_code += f"^XA\n^PW{int(largura_total)}\n^LL{int(altura)}\n^CI28\n"

        # Posição da etiqueta atual
        x_atual = posicoes_horizontais[coluna_atual]
        y_atual = 30  # Margem superior para cada etiqueta no bloco

        # Adiciona a etiqueta no bloco
        zpl_code += f"^FO{x_atual},{y_atual}^FB{int(largura)},5,L,10,0^A0N,30,20^FD{etiqueta}^FS\n"

    # Fecha o último bloco
    zpl_code += "^XZ\n"

    return zpl_code


    for idx, etiqueta in enumerate(etiquetas * copias):
        coluna = idx % colunas
        linha = idx // colunas
        x = posicoes_horizontais[coluna]
        y = linha * (altura + espaco)
        zpl_code += f"^FO{x},{y}^FB{int(largura)},5,L,10,0^A0N,30,20^FD{etiqueta}^FS\n"

        # Adiciona um ^XZ e ^XA para cada linha completa
        if coluna == colunas - 1:
            zpl_code += "^XZ\n^XA\n"

    zpl_code += "^XZ"
    return zpl_code

def main():
    modelos = carregar_modelos()
    if not modelos:
        print("Erro: Não foi possível carregar os modelos.")
        return

    print("\nModelos disponíveis:")
    for idx, nome in enumerate(modelos.keys(), start=1):
        print(f"{idx}. {nome}")
    escolha = int(input("Escolha um modelo pelo número: ").strip())
    modelo_nome = list(modelos.keys())[escolha - 1]
    modelo = modelos[modelo_nome]
    print(f"Modelo selecionado: {modelo_nome}")

    etiquetas = []
    while True:
        etiqueta = input("Digite o conteúdo da etiqueta: ").strip()
        if etiqueta:
            etiquetas.append(etiqueta)
        if input("Deseja inserir outra etiqueta? (s/n): ").strip().lower() != "s":
            break

    copias = int(input("Digite o número de cópias para cada etiqueta: ").strip())
    impressora = selecionar_impressora()
    if not impressora:
        print("Nenhuma impressora selecionada. Encerrando...")
        return

    zpl_code = gerar_zpl(etiquetas, modelo, copias)
    print("\nZPL Gerado:")
    print(zpl_code)

    arquivo_zpl = f"{modelo_nome}_etiquetas.zpl"
    with open(arquivo_zpl, "w") as f:
        f.write(zpl_code)

    print(f"Arquivo ZPL gerado com sucesso: {arquivo_zpl}")
    comando = f"lp -d {impressora} -o raw {arquivo_zpl}"
    os.system(comando)

if __name__ == "__main__":
    main()
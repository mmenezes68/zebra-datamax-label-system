from scripts.loader import carregar_dados, carregar_modelos
from scripts.zpl_generator import gerar_zpl
from scripts.printer import listar_impressoras, selecionar_impressora, imprimir_zpl

def main():
    print("Bem-vindo ao sistema de impressão de etiquetas (v6)\n")
    
    # Carregar modelos de etiquetas
    modelos = carregar_modelos()
    if not modelos:
        print("Nenhum modelo de etiqueta encontrado. Saindo...")
        return

    # Listar modelos disponíveis
    print("Modelos disponíveis:")
    for idx, nome in enumerate(modelos.keys(), start=1):
        print(f"{idx}. {nome}")
    escolha_modelo = input("Escolha um modelo pelo número: ").strip()

    if not escolha_modelo.isdigit() or int(escolha_modelo) not in range(1, len(modelos) + 1):
        print("Modelo inválido. Saindo...")
        return

    modelo_selecionado = list(modelos.keys())[int(escolha_modelo) - 1]
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
    copias = input("Digite o número de cópias para cada etiqueta: ").strip()
    if not copias.isdigit() or int(copias) <= 0:
        print("Número de cópias inválido. Saindo...")
        return
    copias = int(copias)

    # Gerar ZPL
    zpl_code = gerar_zpl(etiquetas, modelo, copias)
    print("\nZPL Gerado:")
    print(zpl_code)

    # Escolher impressora
    impressora = selecionar_impressora()
    if not impressora:
        print("Nenhuma impressora selecionada. Saindo...")
        return

    # Enviar para impressão
    imprimir_zpl(zpl_code, impressora)

if __name__ == "__main__":
    main()
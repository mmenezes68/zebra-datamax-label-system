import subprocess

def listar_impressoras():
    """Lista impressoras disponíveis no sistema."""
    try:
        resultado = subprocess.check_output("lpstat -p", shell=True, text=True)
        impressoras = [linha.split()[1] for linha in resultado.split("\n") if "impressora" in linha or "printer" in linha]
        if not impressoras:
            print("Nenhuma impressora encontrada.")
        return impressoras
    except subprocess.CalledProcessError as e:
        print(f"Erro ao listar impressoras: {e}")
        return []

def selecionar_impressora():
    """Permite ao usuário selecionar uma impressora."""
    impressoras = listar_impressoras()
    if not impressoras:
        return input("Nenhuma impressora foi encontrada. Digite o nome manualmente: ").strip()
    
    print("\nImpressoras disponíveis:")
    for idx, nome in enumerate(impressoras, start=1):
        print(f"{idx}. {nome}")
    
    try:
        escolha = int(input("Escolha uma impressora pelo número: ").strip())
        if 1 <= escolha <= len(impressoras):
            return impressoras[escolha - 1]
        else:
            print("Opção inválida. Digite um número válido.")
    except ValueError:
        print("Entrada inválida. Digite um número.")

    # Caso nenhuma escolha válida seja feita, retorna None
    return None

def imprimir_zpl(zpl_code, impressora):
    """Envia o código ZPL para a impressora selecionada."""
    try:
        comando = f"echo '{zpl_code}' | lp -d {impressora} -o raw"
        subprocess.run(comando, shell=True, check=True)
        print("Impressão enviada com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao imprimir: {e}")
import subprocess

def listar_impressoras():
    """
    Lista impressoras disponíveis no sistema.
    Retorna uma lista de nomes de impressoras ou None se nenhuma for encontrada.
    """
    print("[LOG] Listando impressoras disponíveis...\n")
    try:
        # Executa o comando lpstat para listar impressoras
        resultado = subprocess.check_output("lpstat -p", shell=True, text=True)
        impressoras = []
        for linha in resultado.splitlines():
            # Verifica se a linha começa com "impressora" (em português)
            palavras = linha.split()
            if len(palavras) > 1 and palavras[0].lower() == "impressora":
                nome = palavras[1]  # O nome da impressora é a segunda palavra
                impressoras.append(nome)
        if impressoras:
            print(f"[LOG] Impressoras detectadas: {impressoras}\n")
            return impressoras
        else:
            print("[ERRO] Nenhuma impressora encontrada pelo comando lpstat.\n")
            return None
    except Exception as e:
        print(f"[ERRO] Erro ao executar lpstat: {e}\n")
        return None

def selecionar_impressora():
    """
    Permite ao usuário selecionar uma impressora.
    Retorna o nome da impressora selecionada ou None.
    """
    impressoras = listar_impressoras()
    if not impressoras:
        print("[ERRO] Nenhuma impressora foi encontrada no sistema.")
        return input("Digite o nome da impressora manualmente: ").strip()

    print("Impressoras disponíveis:")
    for idx, nome in enumerate(impressoras, start=1):
        print(f"{idx}. {nome}")
    print()
    try:
        escolha = int(input("Escolha uma impressora pelo número: ").strip())
        if 1 <= escolha <= len(impressoras):
            return impressoras[escolha - 1]
        else:
            print("[ERRO] Seleção inválida.\n")
            return selecionar_impressora()
    except (ValueError, IndexError):
        print("[ERRO] Entrada inválida. Tente novamente.\n")
        return selecionar_impressora()
import os

def imprimir_teste():
    arquivo_teste = "/Applications/MAMP/htdocs/ZPL_estudos/etiquetas/teste.zpl"
    
    if not os.path.exists(arquivo_teste):
        print(f"Erro: Arquivo '{arquivo_teste}' não encontrado.")
        return
    
    # Configurar a impressora e enviar o arquivo
    impressora = "Datamax_M4206_MarkII"
    comando = f"lp -d {impressora} -o raw {arquivo_teste}"
    
    print("Enviando o arquivo ZPL para a impressora...")
    resultado = os.system(comando)
    
    if resultado == 0:
        print("Impressão enviada com sucesso.")
    else:
        print("Erro ao enviar para a impressora. Verifique as configurações.")

if __name__ == "__main__":
    imprimir_teste()
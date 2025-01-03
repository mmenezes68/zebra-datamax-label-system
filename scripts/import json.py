import json

# Caminho para o arquivo JSON
caminho_json = "/Applications/MAMP/htdocs/ZPL_estudos/etiquetas_config.json"

# Carregar o arquivo de configuração
with open(caminho_json, "r") as file:
    modelos = json.load(file)

# Listar modelos disponíveis com números
print("Modelos disponíveis:")
modelos_lista = list(modelos.keys())
for idx, modelo_nome in enumerate(modelos_lista, start=1):
    print(f"{idx}. {modelo_nome}")

# Solicitar ao usuário que escolha um modelo pelo número
try:
    escolha = int(input("\nDigite o número do modelo que deseja usar: "))
    if escolha < 1 or escolha > len(modelos_lista):
        raise ValueError("Número fora do intervalo válido.")
except ValueError:
    print("Entrada inválida! Certifique-se de digitar um número válido.")
    exit()

# Obter o modelo escolhido
modelo_escolhido = modelos_lista[escolha - 1]
modelo = modelos[modelo_escolhido]

# Solicitar ao usuário a quantidade de etiquetas
try:
    quantidade = int(input(f"Digite a quantidade de etiquetas a serem impressas (padrão por linha: {modelo['num_etiquetas']}): "))
    if quantidade <= 0:
        raise ValueError("A quantidade deve ser maior que 0.")
except ValueError:
    print("Entrada inválida! Certifique-se de digitar um número válido.")
    exit()

# Gerar o código ZPL com base no modelo
zpl_code = ""
linhas = (quantidade + modelo["num_etiquetas"] - 1) // modelo["num_etiquetas"]  # Número de linhas necessárias

for linha in range(linhas):
    zpl_code += "^XA\n"
    zpl_code += f"^PW{modelo['largura_total']}\n"
    zpl_code += f"^LL{modelo['altura']}\n"

    for coluna in range(modelo["num_etiquetas"]):
        etiqueta_num = linha * modelo["num_etiquetas"] + coluna + 1
        if etiqueta_num > quantidade:
            break  # Não imprime mais etiquetas se já atingir a quantidade

        pos_x = modelo["posicoes_horizontais"][coluna]
        zpl_code += f"^FO{pos_x},30\n"
        zpl_code += "^FB224,5,L,10,0\n"
        zpl_code += "^ADN,30,20\n"
        zpl_code += f"^FDMarcos A Menezes^FS\n"

    zpl_code += "^XZ\n"

# Salvar o ZPL gerado
output_path = f"/Applications/MAMP/htdocs/ZPL_estudos/output_{modelo_escolhido}.zpl"
with open(output_path, "w") as output_file:
    output_file.write(zpl_code)

print(f"\nZPL gerado e salvo em: {output_path}")
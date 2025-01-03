def gerar_zpl(etiquetas, modelo, copias):
    """
    Gera o código ZPL para as etiquetas fornecidas, respeitando o número de colunas e ajustando ao sensor.
    """
    largura = modelo["largura"]
    altura = modelo["altura"]
    espaco_vertical = modelo.get("espaco", 0)
    colunas = modelo["colunas"]
    largura_total = modelo["largura_total"]
    posicoes_horizontais = modelo["posicoes_horizontais"]

    zpl_code = ""
    for copia in range(copias):
        for idx, etiqueta in enumerate(etiquetas):
            coluna = idx % colunas
            linha = idx // colunas

            if coluna == 0:
                if idx > 0 or copia > 0:
                    zpl_code += "^XZ\n"
                zpl_code += f"^XA\n^PW{int(largura_total)}\n^LL{int(altura + espaco_vertical)}\n^CI28\n"

            x_atual = posicoes_horizontais[coluna]
            y_atual = 30

            zpl_code += f"^FO{x_atual},{y_atual}^FB{int(largura)},5,L,10,0^A0N,30,20^FD{etiqueta}^FS\n"

    zpl_code += "^XZ\n"
    return zpl_code
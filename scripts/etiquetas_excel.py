import subprocess

def enviar_zpl_direto(impressora, zpl_comando):
    """
    Envia um comando ZPL diretamente para a impressora configurada.

    :param impressora: Nome da impressora no sistema.
    :param zpl_comando: Comando ZPL em formato de string.
    """
    try:
        # Envia o comando ZPL diretamente usando subprocess
        processo = subprocess.run(
            ["lpr", "-P", impressora],
            input=zpl_comando.encode('utf-8'),
            check=True
        )
        print(f"Comando ZPL enviado para a impressora {impressora}.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao enviar o comando ZPL: {e}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

# Configuração
impressora = "Datamax_M4206_MarkII"  # Substitua pelo nome correto da sua impressora
zpl_comando = """
^XA
^FO50,50^ADN,36,20^FDTeste ZPL Direto^FS
^XZ
"""

# Envia o comando ZPL para a impressora
enviar_zpl_direto(impressora, zpl_comando)
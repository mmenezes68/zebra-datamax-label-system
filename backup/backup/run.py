import sys
import os

# Adiciona o diretório correto ao caminho de busca do Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, 'scripts', 'core'))  # Garante que 'scripts/core' seja incluído

# Agora podemos importar a função corretamente
from zpl_generator import gerar_zpl  # Verifique se a função 'gerar_zpl' está no arquivo zpl_generator.py
import scripts.features.imprimir_etiqueta_v6 as main_script  # Deve chamar a versão v6

if __name__ == "__main__":
    main_script.main()  # Executa a função main da versão v6
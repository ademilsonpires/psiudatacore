import subprocess

# Nome do arquivo de requisitos
requirements_file = 'requirements.txt'

# Comando para instalar as bibliotecas a partir do arquivo de requisitos
install_command = f'pip install -r {requirements_file}'

# Executa o comando pip para instalar as bibliotecas
try:
    subprocess.check_call(install_command, shell=True)
    print("Todas as bibliotecas foram instaladas com sucesso.")
except subprocess.CalledProcessError as e:
    print(f"Erro ao instalar bibliotecas: {e}")

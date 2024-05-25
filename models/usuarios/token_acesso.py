from itsdangerous import TimestampSigner
from datetime import datetime
from cryptography.fernet import Fernet

import bcrypt

# Chave secreta para criptografar os dados do usuário
chave_criptografia = Fernet.generate_key()
fernet = Fernet(chave_criptografia)

def gerar_token(usuario, senha):
    # Criando uma chave secreta base para assinar o token
    chave_secreta_base = '%_t;*6&!i^kaqn,`~#>tdpp`$bz=ii~15n_(^:0%]i]e6un[]v>&hx)jm^si.8&'

    # Concatenando a chave base com a data e hora atual
    chave_secreta = f"{chave_secreta_base}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Criptografando os dados do usuário
    dados_usuario = f"{usuario}:{senha}"
    dados_usuario_criptografados = fernet.encrypt(dados_usuario.encode()).decode()

    # Criando um signer com a chave secreta
    signer = TimestampSigner(chave_secreta)

    # Gerando o token
    token = signer.sign(dados_usuario_criptografados)

    return token




# Função para criptografar a senha

def criptografar_senha(senha: str) -> str:
    # Hash da senha usando bcrypt
    hashed_senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    return hashed_senha.decode()

# Função para verificar a senha
def verificar_senha(senha: str, senha_criptografada: str) -> bool:
    return bcrypt.checkpw(senha.encode(), senha_criptografada.encode())

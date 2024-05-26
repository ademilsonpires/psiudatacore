from itsdangerous import TimestampSigner
from datetime import datetime
from cryptography.fernet import Fernet
import base64
import hashlib

import bcrypt

# Chave secreta para criptografar os dados do usuário
chave_criptografia = Fernet.generate_key()
fernet = Fernet(chave_criptografia)

# def gerar_token(usuario, senha):
#     # Criando uma chave secreta base para assinar o token
#     chave_secreta_base = 'tdpp$bz=ii~15n_(^:0%]i]e6un[]v'
#
#     # Concatenando a chave base com a data e hora atual
#     chave_secreta = f"{chave_secreta_base}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#
#     # Criptografando os dados do usuário
#     dados_usuario = f"{usuario}:{senha}"
#     dados_usuario_criptografados = fernet.encrypt(dados_usuario.encode()).decode()
#
#     # Criando um signer com a chave secreta
#     signer = TimestampSigner(chave_secreta)
#
#     # Gerando o token
#     token = signer.sign(dados_usuario_criptografados)
#
#     return token


def gerar_token(usuario, senha):
    # Concatenando usuário e senha
    dados_usuario = f"{usuario}:{senha}"

    # Hash SHA-256 dos dados do usuário
    hash_dados = hashlib.sha256(dados_usuario.encode()).digest()

    # Codificando o hash em base64 de forma segura para URL
    token = base64.urlsafe_b64encode(hash_dados).decode()

    return token

# Função para criptografar a senha

def criptografar_senha(senha: str) -> str:
    # Hash da senha usando bcrypt
    hashed_senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
    return hashed_senha.decode()

# Função para verificar a senha
def verificar_senha(senha: str, senha_criptografada: str) -> bool:
    return bcrypt.checkpw(senha.encode(), senha_criptografada.encode())

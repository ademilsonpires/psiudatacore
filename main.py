from urllib.request import Request
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
#from pydantic.types import Optional
from cliente import * # Importe a classe Cliente do arquivo cliente.py
from user import *
from conexao_ora import *
from conexao_mysql import *


from sqlalchemy import create_engine, Column, Integer, String, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, session
from fastapi import Depends, Header
from sqlalchemy.orm import mapper

import jwt
from datetime import datetime, timedelta
import bcrypt

# Geração do salt (valor aleatório usado na criptografia)
salt = bcrypt.gensalt()

import json

from starlette.responses import JSONResponse

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class UserCredentials(BaseModel):
    username: str
    password: str



app = FastAPI(docs_url="/docs", redoc_url="/redoc",title="API | PSIU - DataCore", description="Esta é uma API que fornece dados dos sistemas Psiu Bebidas.")

SECRET_KEY = "%_t;*6&!i^kaqn,`~#>tdpp`$bz=ii~15n_(^:0%]i]e6un[]v>&hx)jm^si.8&" #+ datetime()  # Chave secreta para assinar o token
ALGORITHM = "HS256"  # Algoritmo de criptografia do token
#ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Tempo de expiração do token (em minutos)

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




# Função para gerar um token JWT
def create_access_token(data: dict):# expires_delta: timedelta):
    # Define a data de expiração do token
    #expire = datetime.utcnow() + expires_delta
    # Adiciona a data de expiração ao payload do token
    #data["exp"] = expire
    # Gera o token com os dados e a chave secreta
    token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    # Retorna o token como string
    return token.decode("utf-8")




# Configurar as origens permitidas
origins = ["*"]  # ou especificar as origens permitidas ['http://example.com', 'https://example.com']



# Adicionar o middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#-----------------------------------------------------------------------------

def salvar_token(db: Session, user: userDB, token: str):
    db.refresh(user)


@app.post("/login", tags=["Login"])
async def login(credentials: UserCredentials, db: Session = Depends(get_db)):
    """
    Login - Autenticação
    ---
    Resumo: Autenticação e recuperação de token

    Descrição: Realiza login do usuário devolvendo um token de acesso seguro que é atualizado a cada login..
    ---
    Descrição:
       Realiza login do usuário devolvendo um token de acesso seguro que é atualizado a cada login..

    """
    username = credentials.username
    password = credentials.password

    # Recupera o usuário do banco de dados com base no nome de usuário fornecido
    user_bd = db.query(userDB).filter(userDB.login == text("'" + username + "'")).first()

    # Verifica se o usuário existe e se a senha fornecida é correta
    if user_bd is not None and bcrypt.checkpw(password.encode('utf-8'), user_bd.senha.encode('utf-8')):
        # Login bem-sucedido
        # Cria o payload do token com os dados do usuário
        payload = {"user_id": user_bd.id, "login": user_bd.login}
        # Gera o token com o payload e o tempo de expiração
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        # Salva ou atualiza o token no banco de dados
        salvar_token(db, user_bd, token)
        # Retorna o token como resposta
        return {"access_token": token, "status": "sucesso"}
    else:
        # Credenciais inválidas
        return {"access_token": "invalido", "status": "negado"}


def verificar_token(func):
    def wrapper(token: str = Header(...), db: Session = Depends(get_db)):
        user = db.query(userDB).filter(userDB.token == token).first()

        if not user:
            raise HTTPException(status_code=401, detail="Token inválido")

        return func(token, db)

    return wrapper


#
# @app.post("/adduser/", tags=["Usuários"])
# def add_usuario(user: user):
#
#
#     if not user:
#         #credencial inválida
#         raise HTTPException(status_code=401, detail="Token inválido")
#     else:
#         # Credenciais ok
#         return add_user(user)
#

@app.get("/buscacliente/{id_cliente}")
def buscacliente(id_cliente: int):
    return buscarcli(id_cliente)



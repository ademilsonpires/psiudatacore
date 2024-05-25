from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from cliente import * # Importe a classe Cliente do arquivo cliente.py
from models.usuarios.token_acesso import *
from models.usuarios.usuarios import *
from models.inadimplencia.inadimplencia import *
from conexao_ora import *


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

#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Classe Pydantic para validar a entrada do usuário
class NovoUsuario(BaseModel):
    nome: str
    senha: str
    status: str

class LoginUsuario(BaseModel):
    nome: str
    senha: str

app = FastAPI(docs_url="/docs", redoc_url="/redoc",title="API | PSIU - DataCore", description="Esta é uma API que fornece dados dos sistemas Psiu Bebidas.")

# Função para obter a sessão do banco de dados
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


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



@app.post("/adicionar-usuarios/", tags=["Usuários"])
async def criar_usuario(usuario: NovoUsuario, token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Criptografar a senha antes de inserir no banco de dados
    senha_criptografada = criptografar_senha(usuario.senha)

    # Criar uma instância do objeto Usuario
    novo_usuario = Usuario(nome_usuario=usuario.nome, senha=senha_criptografada, token=None, status=usuario.status)

    # Criar uma instância do objeto UsuarioDB e inserir o usuário no banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_id = db.insert_usuario(novo_usuario)
    db.close()

    # Retornar o ID do novo usuário criado
    return {"id": usuario_id}



# Endpoint de login
@app.post("/login/", tags=["Usuários"])
async def login(usuario: LoginUsuario):
    db = UsuarioDB('bd.sqlite3')
    usuario_db = db.get_usuario_by_nome_usuario(usuario.nome)

    if usuario_db is None:
        db.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario_stored = Usuario(*usuario_db)

    if not verificar_senha(usuario.senha, usuario_stored.senha):
        db.close()
        raise HTTPException(status_code=401, detail="Senha incorreta")

    if not usuario_stored.token:
        token = gerar_token(usuario_stored.nome_usuario, usuario.senha)
        db.update_usuario_campo(usuario_stored.id, 'token', token)
        usuario_stored.token = token
        db.close()

    db.close()

    return {"token": usuario_stored.token}

# @app.get("/buscacliente/{id_cliente}")
# def buscacliente(id_cliente: int):
#     return buscarcli(id_cliente)

@app.get("/busca-inadimplencia/", tags=["Inadimplencia"])
async def inadimplencia(token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    resultado_json = busca_inadimplencia()

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)
    # Retornar a consulta
    return resultado_objeto




# import bcrypt
# from pydantic import BaseModel
# #from pydantic.types import Optional
# from sqlalchemy import create_engine, Column, Integer, String, text
# from sqlalchemy.exc import SQLAlchemyError
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session, session
# import json
#
# from starlette.exceptions import HTTPException
# from starlette.responses import JSONResponse
#
# from conexao_mysql import engine
#
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# # Geração do salt (valor aleatório usado na criptografia)
# salt = bcrypt.gensalt()
#
# class user(BaseModel):
#     id: int = None
#     nome: str = None
#     nivel: str = None
#     validade: str = None
#     login: str = None
#     senha: str = None
#     token: str = None
#
#
#
#
# Base = declarative_base()
# class userDB(Base):
#     __tablename__ = "user_coletor_g20"  # Defina o nome da tabela
#     id = Column(Integer, primary_key=True, index=True)
#     nome = Column(String(50))
#     nivel = Column(String(50))
#     validade = Column(String(50))
#     login = Column(String(30))
#     senha = Column(String(12))
#     token = Column(String(300))
#
#     def as_dict(self):
#         return {
#             "id": self.id,
#             "nome": self.nome,
#             "nivel": self.nivel,
#             "validade": self.validade,
#             "login": self.login,
#             "senha" : self.senha,
#             "token" : self.token,
#
#         }
#
# #metodos
# # - 1 retorna usuário
#
# def get_all_users():
#     """
#     Rota para ler todos os registros de usuarios.
#
#     """
#     db = SessionLocal()
#     user = db.query(userDB).all()
#     json_results = json.dumps([user.as_dict() for user in user])
#     parsed_results = json.loads(json_results)
#     return parsed_results
#
# #2-add usuario
# def add_user(user: user):
#     db = SessionLocal()
#     db_user = userDB(nome=user.nome, nivel=user.nivel, validade=user.validade, login=user.login, senha=bcrypt.hashpw(user.senha.encode('utf-8'), salt))
#
#
#     if db_user:
#
#         db.add(db_user)
#         db.commit()
#         db.refresh(db_user)
#         return {"message": "success add"}
#     else:
#         raise HTTPException(status_code=404, detail="not add")
#

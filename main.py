from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from fastapi.responses import HTMLResponse
from fastapi import Header, HTTPException, Query
from starlette.responses import JSONResponse
from pydantic import BaseModel
from conexao_ora import *

from models.usuarios.token_acesso import *
from models.usuarios.usuarios import *
from models.inadimplencia.inadimplencia import *
from models.calendario.calendario import *
from models.custos_mp.custos_mp import *
from models.custos_mp.produtos_custos import *
from models.clientes.cliente import *
from models.clientes.clientes_geo_express import *
from models.producao.ordem_producao import *
from models.producao.apontamento_producao import *
from models.logistica.transferencias import *
from models.suprimentos.ordens_de_compra import *

from fastapi import Depends, Header, Body

import bcrypt

# Geração do salt (valor aleatório usado na criptografia)
salt = bcrypt.gensalt()

import json


# Classe Pydantic para validar a entrada do usuário
class NovoUsuario(BaseModel):
    nome: str
    senha: str
    status: str
    tipo: str
    user_saib: int

class LoginUsuario(BaseModel):
    nome: str
    senha: str


class ApontamentoProducao(BaseModel):
    linha_producao: int
    ordem_producao: int
    sku_producao: int
    data_producao: str
    hora_producao: str
    qtde_produzida: int
    empresa_producao: int
    gap: int
    obs: str

# Definindo o modelo de dados esperado no corpo da requisição
class AprovacaoRequest(BaseModel):
    status: str
    empresa: int
    id_ordem: int
    id_aprovador: int



class CheckMP(BaseModel):
    linha_producao: int
    ordem_producao: int
    cod_sku_producao: int
    empresa_producao: int
    cod_mat_prima: int
    status: str


app = FastAPI(docs_url="/docs", redoc_url="/redoc",title="API | PSIU - DataCore", description="Esta é uma API que fornece dados dos sistemas Psiu Bebidas.")




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
class Filtros(BaseModel):
    codigos_produto: str
    data_inicial: str
    data_final: str





# Montar diretório de arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/graficos", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request, products: str, startDate: str, endDate: str):
    return templates.TemplateResponse("graficos.html", {"request": request, "products": products, "startDate": startDate, "endDate": endDate})

@app.get("/filtrar-analise-mp", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse("filtrar-analise-mp.html", {"request": request})

@app.get("/filtrar-analise-cliente", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse("filtrar-analise-cliente.html", {"request": request})

@app.get("/mapa-psiuex", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse("mapa-psiuex.html", {"request": request})

@app.get("/teste", response_class=HTMLResponse, include_in_schema=False)
async def read_root(request: Request):
    return templates.TemplateResponse("teste.html", {"request": request})




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
    novo_usuario = Usuario(nome_usuario=usuario.nome, senha=senha_criptografada, token=None, status=usuario.status, tipo=usuario.tipo, user_saib=usuario.user_saib)

    # Criar uma instância do objeto UsuarioDB e inserir o usuário no banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_id = db.insert_usuario(novo_usuario)
    db.close()

    # Retornar o ID do novo usuário criado
    return {"id": usuario_id}

@app.post("/atualiza-senha-usuarios/", tags=["Usuários"])
async def atualizar_senha(id_usuario: int, nova_senha: str, token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Conexão com o banco de dados
    db = UsuarioDB('bd.sqlite3')

    # Verificar se o token é válido e buscar o usuário associado ao token
    usuario_stored = db.get_usuario_by_token(token)

    # Fechar a conexão com o banco após a consulta
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Verificar se o id_usuario recebido é o mesmo do usuário autenticado
    if usuario_stored[0] != id_usuario:
        raise HTTPException(status_code=403, detail="Acesso não autorizado")

    # Criptografar a nova senha antes de atualizá-la
    senha_criptografada = criptografar_senha(nova_senha)

    # Abrir conexão com o banco de dados novamente
    db = UsuarioDB('bd.sqlite3')

    try:
        # Atualizar a senha do usuário no banco de dados
        resultado_update_senha = db.update_usuario_campo(id_usuario, "senha", senha_criptografada)

        if resultado_update_senha == 0:
            raise HTTPException(status_code=400, detail="Erro ao atualizar a senha. Nenhuma linha foi afetada.")

        # Limpar o token após a atualização de senha
        resultado_update_token = db.update_usuario_campo(id_usuario, "token", None)

        if resultado_update_token == 0:
            raise HTTPException(status_code=400, detail="Erro ao limpar o token. Nenhuma linha foi afetada.")

    except Exception as e:
        db.close()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar a senha: {str(e)}")

    # Fechar conexão com o banco
    db.close()

    # Retornar uma resposta de sucesso
    return {"status": "sucesso", "message": "Senha atualizada com sucesso"}

@app.get("/usuarios/", tags=["Usuários"], include_in_schema=False)
async def listar_usuarios(token: str = Header(...), usuario_id: Optional[int] = None):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token.strip())

    if not usuario_stored:
        db.close()
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Obter usuário(s)
    usuarios = db.get_usuarios(usuario_id)
    db.close()

    if not usuarios:
        raise HTTPException(status_code=404, detail="Usuário(s) não encontrado(s)")

    return usuarios


@app.delete("/deletar-usuarios/{usuario_id}", tags=["Usuários"], include_in_schema=False)
async def excluir_usuario(usuario_id: int, token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)

    if not usuario_stored:
        db.close()
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Verificar se o usuário a ser excluído existe
    usuario = db.get_usuarios(usuario_id)
    if not usuario:
        db.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Excluir o usuário
    db.delete_usuario(usuario_id)
    db.close()

    return {"detail": "Usuário excluído com sucesso"}
# Endpoint de login
@app.post("/logar-api/", tags=["Usuários"])
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

    return {"token": usuario_stored.token,"id_usuario":usuario_stored.id, "id_usuario_aprovador":usuario_stored.user_saib, "tipo":usuario_stored.tipo, "status":usuario_stored.status}

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



@app.get("/busca-calendario/", tags=["Calendario"])
async def calendarios(token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    resultado_json = busca_calendario()

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)
    # Retornar a consulta
    return resultado_objeto


@app.get("/busca-custos-mp/", tags=["Custos"])
async def custos_mp(
    request: Request,
    token: str = Header(...),
    codigos_produto: str = Query(...),
    data_inicial: str = Query(...),
    data_final: str = Query(...)
):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Converter os códigos de produto para uma lista de inteiros
    codigos_produto = [int(codigo) for codigo in codigos_produto.split(",")]

    # Chamar a função busca_custos_mp() passando os parâmetros
    resultado_json = busca_custos_mp(codigos_produto, data_inicial, data_final)

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)
    # Retornar a consulta
    return resultado_objeto
@app.get("/busca-variacao-custos-mp/", tags=["Custos"])
async def variacao_custos_mp(
    request: Request,
    token: str = Header(...),
    #codigos_produto: str = Query(...),
    data_inicial: str = Query(...),
    data_final: str = Query(...)
):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Converter os códigos de produto para uma lista de inteiros
    #codigos_produto = [int(codigo) for codigo in codigos_produto.split(",")]

    # Chamar a função busca_custos_mp() passando os parâmetros
    resultado_json = busca_variacao_custos_mp_c_mes_de_ref(data_inicial, data_final)

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)
    # Retornar a consulta
    return resultado_objeto



@app.get("/busca-produtos-custos-mp/", tags=["Custos"])
async def produtos_custos_mp(token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    resultado_json = busca_produtos_custos_mp()

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)
    # Retornar a consulta
    return resultado_objeto


@app.get("/buscacliente/{id_cliente}", tags=["Clientes"])
def buscacliente(id_cliente: int):
    return buscarcli(id_cliente)

@app.get("/buscaclientesporID/{id_cliente}", tags=["Clientes"])
async def buscaclientesproximosporID(id_cliente: int, token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    clientes_proximos = buscarClientesProximosporID(conn, id_cliente)
    return JSONResponse(content=clientes_proximos)

# @app.get("/buscaclientesproximos/{id_cliente}", tags=["Clientes"])
# def buscaclientesproximos(id_cliente: int):
#     return buscarClientesProximos(conn, id_cliente)
@app.get("/buscaclientesproximos/{id_cliente}", tags=["Clientes"])
async def buscaclientesproximos(id_cliente: int, token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    clientes_proximos = buscarClientesProximos(conn, id_cliente)
    return JSONResponse(content=clientes_proximos)
@app.get("/busca-clientes-cvto-fatura/", tags=["Clientes"])
async def busca_clientes_fatura(token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    resultado_json = buscarCliFatura25()

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)
    # Retornar a consulta
    return resultado_objeto



@app.get("/busca-linhas-producao/", tags=["Produção"])
async def linhas(token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    resultado_json = busca_linhas_producao_com_ordens()

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)
    # Retornar a consulta
    return resultado_objeto



@app.get("/busca-ordens-old/", tags=["Produção"])
async def ordens(token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    resultado_json = busca_ordens()

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)
    # Retornar a consulta
    return resultado_objeto



@app.get("/busca-ordens/", tags=["Produção"])
async def ordens(token: str = Header(...), orpr_lipr_id: int = None):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Buscar ordens com ou sem filtro
    resultado_json = busca_ordens(orpr_lipr_id)

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)

    # Retornar a consulta
    return resultado_objeto

@app.get("/busca-ordem-id/", tags=["Produção"])
async def busca_ordem_por_id(token: str = Header(...), id_ordem: int = None):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Buscar ordens com ou sem filtro
    resultado_json = busca_ordem_id(id_ordem)

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)

    # Retornar a consulta
    return resultado_objeto

@app.get("/busca-serie-ordem-id/", tags=["Produção"])
async def busca_serie_da_ordem_por_id(token: str = Header(...), id_ordem: int=None):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Buscar ordens com ou sem filtro
    resultado_json = busca_serie_ordem_id(id_ordem)

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)

    # Retornar a consulta
    return resultado_objeto


@app.get("/busca-check-serie-ordem-id/", tags=["Produção"])
async def busca_check_serie_da_ordem_por_id(token: str = Header(...), id_ordem: int=None):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Buscar ordens com ou sem filtro
    resultado_json = busca_check_serie_ordem_id(id_ordem)

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)

    # Retornar a consulta
    return resultado_objeto


@app.get("/busca-check-serie-ordem-id/", tags=["Produção"])
async def busca_apontamento_ordem_por_id(token: str = Header(...), id_ordem: int=None):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Buscar ordens com ou sem filtro
    resultado_json = busca_hist_apontamento_ordem_id(id_ordem)

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)

    # Retornar a consulta
    return resultado_objeto


@app.post("/inserir-apontamento-producao/", tags=["Produção"])
async def endpoint_inserir_apontamento_producao(
        apontamento: ApontamentoProducao,
        token: str = Header(...)
):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Criar uma instância do objeto ApontamentoDB
    apontamento_db = ApontamentoDB(conn)

    # Inserir os dados no banco de dados
    resultado = apontamento_db.inserir_apontamento(apontamento)

    return resultado



@app.post("/inserir-check-mp/", tags=["Produção"])
async def inserir_check_mp(
    check_mp: CheckMP,
    token: str = Header(...)
):
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    check_mp_db = CheckMPDB(conn)
    resultado = check_mp_db.inserir_check_mp(check_mp)

    return resultado


@app.get("/busca-transferencias/", tags=["Logística"])
async def ordens(token: str = Header(...)):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    resultado_json = busca_transferencias_em_aberto()

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)
    # Retornar a consulta
    return resultado_objeto



@app.get("/busca-ordens-de-compra-por-aprovador/", tags=["Suprimentos"])
async def busca_ordens_de_compra_por_aprovadores(token: str = Header(...), aprovador: int = None):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Buscar ordens com ou sem filtro
    resultado_json = busca_ordens_de_compra_por_aprovador(aprovador)

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)

    # Retornar a consulta
    return resultado_objeto


@app.get("/busca-itens-ordens-de-compra-por-ordem/", tags=["Suprimentos"])
async def busca_itens_ordens_da_ordem_compra(token: str = Header(...), empresa: int = None, id_ordem: int = None):
    # Verificar se o token está presente no cabeçalho da requisição
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Verificar se o token é válido consultando o banco de dados
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Buscar ordens com ou sem filtro
    resultado_json = busca_itens_ordens_de_compra_por_ordem(empresa,id_ordem)

    # Deserializando a string JSON de volta para um objeto Python
    resultado_objeto = json.loads(resultado_json)

    # Retornar a consulta
    return resultado_objeto

# Endpoint para gravar a aprovação do aprovador
@app.post("/grava-aprovacao-aprovador/", tags=["Suprimentos"])
async def grava_aprovacao_aprovador(
    aprovacao_data: AprovacaoRequest,
    token: str = Header(...)
):
    # Verificar se o token está presente e válido (usando sua função já existente)
    if not token:
        raise HTTPException(status_code=401, detail="Token de autenticação ausente")

    # Substituir pela sua lógica de autenticação existente
    db = UsuarioDB('bd.sqlite3')
    usuario_stored = db.get_usuario_by_token(token)
    db.close()

    if not usuario_stored:
        raise HTTPException(status_code=401, detail="Acesso negado. Token inválido ou usuário inativo")

    # Chamar a função grava_aprovacao_do_aprovador passando os dados recebidos no JSON
    resultado = grava_aprovacao_do_aprovador(
        status=aprovacao_data.status,
        empresa=aprovacao_data.empresa,
        id_ordem=aprovacao_data.id_ordem,
        id_aprovador=aprovacao_data.id_aprovador
    )

    # Se a função retornar sucesso
    if resultado["status"] == "success":
        return {"message": "Aprovação registrada com sucesso", "resultado": resultado}

    # Se houver algum erro ou a ordem ainda não estiver totalmente aprovada
    raise HTTPException(status_code=400, detail=resultado["message"])
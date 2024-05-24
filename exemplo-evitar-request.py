from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# Defina uma lista com os caminhos dos endpoints existentes na sua aplicação
endpoints = ['/items', '/users', '/orders']

# Middleware personalizado para verificar se o caminho da requisição corresponde a um endpoint existente
@app.middleware("http")
async def check_endpoint(request, call_next):
    if request.url.path not in endpoints:
        raise HTTPException(status_code=404, detail="Endpoint não encontrado")
    response = await call_next(request)
    return response

# Exemplo de um endpoint existente
@app.get("/items")
async def read_items():
    return {"message": "Lista de itens"}

# Exemplo de um endpoint existente
@app.get("/users")
async def read_users():
    return {"message": "Lista de usuários"}

import sqlite3

def conectar():
    try:
        # Conectar ao banco de dados
        conexao = sqlite3.connect('db.sqlite3')
        print("Conexão estabelecida com sucesso!")
        return conexao
    except sqlite3.Error as erro:
        print("Erro ao conectar ao banco de dados:", erro)
        return None

def desconectar(conexao):
    try:
        # Fechar a conexão com o banco de dados
        conexao.close()
        print("Conexão encerrada.")
    except sqlite3.Error as erro:
        print("Erro ao encerrar conexão:", erro)

# Testar a conexão
if __name__ == "__main__":
    conexao = conectar()
    if conexao:
        desconectar(conexao)


from conexao_ora import *

def buscarcli(idcliente):
    try:
        # Crie um cursor para executar consultas
        cursor = conn.cursor()

        # Execute a consulta para buscar o nome fantasia do cliente com base no idcliente
        cursor.execute(
            "SELECT CLIENTE.CLI_FANTASIA FROM CLIENTE WHERE CLIENTE.CLI_EMP_ID = 20 AND CLIENTE.CLI_ID = :idcliente",
            idcliente=idcliente)

        # Obtenha o resultado
        row = cursor.fetchone()

        if row:
            # O cliente foi encontrado, retorne o nome fantasia em um formato JSON
            return {"Nome Fantasia": row[0]}
        else:
            # Cliente não encontrado, retorne um JSON com a mensagem de erro
            return {"Mensagem": "Cliente não encontrado."}

    except cx_Oracle.DatabaseError as e:
        # Em caso de erro, você pode optar por levantar uma exceção ou retornar uma mensagem de erro
        # Neste exemplo, estamos retornando um JSON com a mensagem de erro.
        return {"Erro": f"Erro ao conectar ou executar consulta: {e}"}

    finally:
        # Certifique-se de fechar o cursor e a conexão, independentemente do resultado
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


from conexao_ora import *
import json

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


def buscarCliFatura25():
    try:

        # Crie um cursor para executar consultas
        cursor = conn.cursor()

        # Execute a consulta para buscar os dados dos clientes
        cursor.execute(
            """SELECT 
                T.d_cod_cliente,
                T.d_fantasia,
                T.d_cidade,
                T.d_latitude,
                T.d_longitude
            FROM
                VIEW_BASE_CLIENTE_25 T,
                (SELECT CLI.CLI_ID,
                        CLI.CLI_EMP_ID,
                        CLI.cli_gen_id_tp_docum_de AS FORMA_PGTO,
                        CLI.CLI_GEN_ID_TP_FATURA_DE AS COND_PGTO
                 FROM CLIENTE CLI
                 WHERE CLI.CLI_EMP_ID = 25
                   AND CLI.CLI_GEN_ID_TP_FATURA_DE = 2
                   AND CLI.cli_gen_id_tp_docum_de = 3) B
            WHERE T.empresa = B.CLI_EMP_ID
              AND T.d_cod_cliente = B.CLI_ID"""
        )

        # Obtenha o resultado
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "d_cod_cliente": row[0],
                "d_fantasia": row[1],
                "d_cidade": row[2],
                "d_latitude": float(row[3]),
                "d_longitude": float(row[4])
            }
            results.append(result_dict)

        # Feche o cursor e a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Converta a lista de dicionários em formato JSON e retorne
        return json.dumps(results)

    except cx_Oracle.DatabaseError as e:
        # Em caso de erro, retorne uma mensagem de erro
        return json.dumps({"Erro": f"Erro ao conectar ou executar consulta: {e}"})
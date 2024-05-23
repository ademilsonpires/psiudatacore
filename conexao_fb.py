# conexao_fb.py
import firebirdsql
from config_fb import host, port, database, user, password

def executar_consulta(sql_query):
    try:
        con = firebirdsql.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )

        # Criando um cursor para executar a consulta
        cur = con.cursor()

        # Executando a consulta
        cur.execute(sql_query)

        # Recuperando os resultados da consulta
        results = cur.fetchall()

        return results

    except Exception as e:
        print("Ocorreu um erro durante a conexão ou a consulta:", e)

    finally:
        con.close()

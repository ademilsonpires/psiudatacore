import cx_Oracle
import json
from conexao_ora import userOra, password, dsn

# def busca_custos_mp():
#     try:
#         # Crie a conexão
#         conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)
#
#         # Crie um cursor para executar a consulta
#         cursor = conn.cursor()
#
#         # Execute a consulta SQL para buscar a inadimplência
#         cursor.execute("""
#         SELECT
#             EMPRESA,
#             COD_PRODUTO,
#             DATA_MOV,
#             DATA_CADASTRO,
#             TIPO_ENTRAD_SAIDA,
#             TO_NUMBER(MOV_QUANT) AS MOV_QUANT,
#             TO_NUMBER(MOV_CUSTO_TOTAL) AS MOV_CUSTO_TOTAL,
#             SALDOS_QUANT_ANTERIOR,
#             TO_NUMBER(SALDOS_QUANT_TOTAL) AS SALDOS_QUANT_TOTAL,
#             TO_NUMBER(SALDOS_CUSTO_TOTAL) AS SALDOS_CUSTO_TOTAL,
#             CASE
#                 WHEN TO_NUMBER(SALDOS_QUANT_TOTAL) <> 0 THEN TO_NUMBER(SALDOS_CUSTO_TOTAL) / TO_NUMBER(SALDOS_QUANT_TOTAL)
#                 ELSE 0  -- Substitua 0 pelo valor padrão desejado quando a quantidade total for zero
#             END AS CUSTO_MEDIO,
#             SUBGRUPO_DESCRICAO,
#             GRUPO
#         FROM
#             VIEW_KARDEX_INDUSTRIA t
#         WHERE
#             t.EMPRESA = 4
#             AND t.COD_PRODUTO IN (
#                 aqui entra uma lista de codigos separadas por ,
#             )
#             AND T.DATA_MOV >= 'aqui entrada um intervalo de datas'
#             AND T.DATA_MOV <= 'aqui entrada um intervalo de datas'
#         """)
#
#         # Obtenha todos os resultados da consulta
#         rows = cursor.fetchall()
#
#         # Converta os resultados em uma lista de dicionários
#         results = []
#         for row in rows:
#             result_dict = {
#                 "EMPRESA": row[0],
#                 "COD_PRODUTO": row[1],
#                 "DATA_MOV": row[2].strftime('%d/%m/%Y') if row[2] else None,
#                 "DATA_CADASTRO": row[3].strftime('%d/%m/%Y') if row[3] else None,
#                 "TIPO_ENTRAD_SAIDA": row[4],
#                 "MOV_QUANT": row[5],
#                 "MOV_CUSTO_TOTAL": row[6],
#                 "SALDOS_QUANT_ANTERIOR": row[7],
#                 "SALDOS_QUANT_TOTAL": row[8],
#                 "SALDOS_CUSTO_TOTAL": row[9],
#                 "CUSTO_MEDIO": row[10],
#                 "SUBGRUPO_DESCRICAO": row[11],
#                 "GRUPO": row[12]
#             }
#             results.append(result_dict)
#
#         # Feche o cursor e a conexão com o banco de dados
#         cursor.close()
#         conn.close()
#
#         # Converta a lista de dicionários em formato JSON e retorne
#         return json.dumps(results)
#
#     except cx_Oracle.DatabaseError as e:
#         # Em caso de erro, retorne uma mensagem de erro
#         return json.dumps({"Erro": f"Erro ao conectar ou executar consulta: {e}"})





def busca_custos_mp(codigos_produto, data_inicial, data_final):
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Construa a string com os códigos de produto
        codigos_str = ','.join(map(str, codigos_produto))

        # Execute a consulta SQL para buscar os custos
        sql = f"""
        SELECT 
            EMPRESA,
            COD_PRODUTO,
            DATA_MOV,
            DATA_CADASTRO,
            TIPO_ENTRAD_SAIDA,
            TO_NUMBER(MOV_QUANT) AS MOV_QUANT,                     
            TO_NUMBER(MOV_CUSTO_TOTAL) AS MOV_CUSTO_TOTAL,
            SALDOS_QUANT_ANTERIOR,
            TO_NUMBER(SALDOS_QUANT_TOTAL) AS SALDOS_QUANT_TOTAL,
            TO_NUMBER(SALDOS_CUSTO_TOTAL) AS SALDOS_CUSTO_TOTAL,
            CASE 
                WHEN TO_NUMBER(SALDOS_QUANT_TOTAL) <> 0 THEN TO_NUMBER(SALDOS_CUSTO_TOTAL) / TO_NUMBER(SALDOS_QUANT_TOTAL)
                ELSE 0  -- Substitua 0 pelo valor padrão desejado quando a quantidade total for zero
            END AS CUSTO_MEDIO,
            SUBGRUPO_DESCRICAO,
            GRUPO
        FROM 
            VIEW_KARDEX_INDUSTRIA t 
        WHERE 
            t.EMPRESA = 4
            AND t.COD_PRODUTO IN ({codigos_str})  -- Inserir diretamente aqui
            AND (T.DATA_MOV BETWEEN TO_DATE(:data_inicial, 'DD/MM/YYYY') AND TO_DATE(:data_final, 'DD/MM/YYYY'))
        """

        # Execute a consulta SQL com os parâmetros de data
        cursor.execute(sql, {'data_inicial': data_inicial, 'data_final': data_final})

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "EMPRESA": row[0],
                "COD_PRODUTO": row[1],
                "DATA_MOV": row[2].strftime('%d/%m/%Y') if row[2] else None,
                "DATA_CADASTRO": row[3].strftime('%d/%m/%Y') if row[3] else None,
                "TIPO_ENTRAD_SAIDA": row[4],
                "MOV_QUANT": row[5],
                "MOV_CUSTO_TOTAL": row[6],
                "SALDOS_QUANT_ANTERIOR": row[7],
                "SALDOS_QUANT_TOTAL": row[8],
                "SALDOS_CUSTO_TOTAL": row[9],
                "CUSTO_MEDIO": row[10],
                "SUBGRUPO_DESCRICAO": row[11],
                "GRUPO": row[12]
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

# # Exemplo de uso da função
# codigos_produto = [2092, 2067]  # Lista de códigos de produto como uma string
# data_inicial = '01/01/2024'  # Data inicial no formato 'DD/MM/YYYY'
# data_final = '31/05/2024'  # Data final no formato 'DD/MM/YYYY'
#
# resultado = busca_custos_mp(codigos_produto, data_inicial, data_final)
# print(resultado)


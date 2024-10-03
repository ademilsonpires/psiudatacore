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



def busca_variacao_custos_mp(codigos_produto, data_inicial, data_final):
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Construa a string com os códigos de produto
        codigos_str = ','.join(map(str, codigos_produto))

        # Execute a consulta SQL para buscar os custos
        sql = f"""
            SELECT * FROM (
                SELECT
                    MIN_DATA_MOV,
                    MAX_DATA_MOV,
                    COD_PRODUTO,
                    SUBGRUPO_DESCRICAO,
                    GRUPO,
                    CUSTO_MEDIO_INICIAL,
                    CUSTO_MEDIO_FINAL,
                    VARIACAO
            
                FROM (
                    SELECT DISTINCT
                        MIN_DATA_MOV,
                        MAX_DATA_MOV,
                        COD_PRODUTO,
                        SUBGRUPO_DESCRICAO,
                        GRUPO,
                        CUSTO_MEDIO_INICIAL,
                        CUSTO_MEDIO_FINAL,
                        CASE 
                            WHEN NVL(CUSTO_MEDIO_INICIAL, 0) = 0 THEN 0
                            ELSE ROUND(((NVL(CUSTO_MEDIO_FINAL, 0) / NVL(CUSTO_MEDIO_INICIAL, 0)) - 1) * 100, 2)
                        END AS VARIACAO
                    FROM (
                        SELECT
                            t.DATA_MOV,
                            t.COD_PRODUTO,
                            t.SUBGRUPO_DESCRICAO,
                            t.GRUPO,
                            MIN(t.DATA_MOV) OVER (PARTITION BY t.COD_PRODUTO) AS MIN_DATA_MOV,
                            MAX(t.DATA_MOV) OVER (PARTITION BY t.COD_PRODUTO) AS MAX_DATA_MOV,
                            FIRST_VALUE(CASE
                                            WHEN TO_NUMBER(t.SALDOS_QUANT_TOTAL) <> 0 THEN TO_NUMBER(t.SALDOS_CUSTO_TOTAL) / TO_NUMBER(t.SALDOS_QUANT_TOTAL)
                                            ELSE 0
                                        END) OVER (PARTITION BY t.COD_PRODUTO ORDER BY t.DATA_MOV
                                                    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS CUSTO_MEDIO_INICIAL,
                            LAST_VALUE(CASE
                                           WHEN TO_NUMBER(t.SALDOS_QUANT_TOTAL) <> 0 THEN TO_NUMBER(t.SALDOS_CUSTO_TOTAL) / TO_NUMBER(t.SALDOS_QUANT_TOTAL)
                                           ELSE 0
                                       END) OVER (PARTITION BY t.COD_PRODUTO ORDER BY t.DATA_MOV
                                                   ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS CUSTO_MEDIO_FINAL
                        FROM
                            (
                                SELECT DISTINCT
                                    K.KDEX_EMP_ID AS EMPRESA,
                                    K.KDEX_PROD_ID AS COD_PRODUTO,
                                    K.KDEX_DATA AS DATA_MOV,
                                    K.KDEX_DTA_CAD AS DATA_CADASTRO,
                                    K.KDEX_ENTR_SAI AS TIPO_ENTRAD_SAIDA,
                                    K.KDEX_QTD AS MOV_QUANT,
                                    K.KDEX_CTO AS MOV_CUSTO_TOTAL,
                                    K.KDEX_QTDE_ANT AS SALDOS_QUANT_ANTERIOR,
                                    K.KDEX_CTO_ANT AS SALDOS_CTO_TOTAL_ANTERIOR,
                                    K.KDEX_QTDE_MEDIA AS SALDOS_QUANT_TOTAL,
                                    K.KDEX_CUSTO_TOTAL AS SALDOS_CUSTO_TOTAL,
                                    P.PROD_DESC AS SUBGRUPO_DESCRICAO,
                                    GRP.GRUPO AS GRUPO
                                FROM
                                    KARDEX K
                                    JOIN PRODUTO P ON K.KDEX_PROD_EMP_ID = P.PROD_EMP_ID AND K.KDEX_PROD_ID = P.PROD_ID
                                    JOIN (
                                        SELECT DISTINCT
                                            P.PROD_ID AS COD_PRODUTO,
                                            P.PROD_DESC AS NOME_PRODUTO,
                                            A.GENA_GEN_TGEN_ID AS TABELA_GENERICA,
                                            A.GENA_GEN_ID AS COD_ITEM_TABELA,
                                            A.GENA_GEN_TGEN_ID_PROPRIETARIO_ AS ID_SUBGRUPO,
                                            G.GEN_DESCRICAO AS SUBGRUPO,
                                            A.GENA_GEN_ID_PROPRIETARIO_DE AS ID_GRUPO,
                                            (SELECT DECODE(
                                                A.GENA_GEN_ID_PROPRIETARIO_DE,
                                                1, 'MATERIA PRIMA',
                                                2, 'EMBALAGEM',
                                                3, 'MATERIAL SECUNDARIO',
                                                4, 'ESTOQUES DIVERSOS',
                                                5, 'IMOBILIZADO',
                                                6, 'MANUTENCAO INDUSTRIAL',
                                                9, 'PRODUTOS ACABADOS',
                                                10, 'PRODUTOS EM ELABORAÇÃO',
                                                99, 'DIVERSOS',
                                                'NÃO INFORMADO') FROM DUAL) AS GRUPO
                                        FROM
                                            GENER G
                                            JOIN GENER_A A ON A.GENA_GEN_TGEN_ID = G.GEN_TGEN_ID AND A.GENA_GEN_EMP_ID = G.GEN_EMP_ID AND A.GENA_GEN_ID = G.GEN_ID
                                            JOIN PRODUTO_AL AL ON AL.PROA_PROD_EMP_ID = A.GENA_GEN_EMP_ID AND AL.PROA_GEN_ID = G.GEN_ID
                                            JOIN PRODUTO P ON P.PROD_ID = AL.PROA_PROD_ID
                                        WHERE
                                            A.GENA_GEN_TGEN_ID = 926
                                            AND A.GENA_GEN_EMP_ID = 4
                                            AND G.GEN_EMP_ID = 4
                                    ) GRP ON GRP.COD_PRODUTO = K.KDEX_PROD_ID
                                WHERE
                                    K.KDEX_EMP_ID = 4
                                    AND K.KDEX_DATA >= TO_DATE(:data_inicial, 'DD/MM/YYYY')
                                    AND K.KDEX_DATA <= TO_DATE(:data_final, 'DD/MM/YYYY')
                                    AND NVL(P.PROD_SITUACAO, 'H') = 'H'
                            ) t
                        WHERE
                            t.EMPRESA = 4
                             AND (T.DATA_MOV BETWEEN TO_DATE(:data_inicial, 'DD/MM/YYYY') AND TO_DATE(:data_final, 'DD/MM/YYYY'))
                    )
                    WHERE DATA_MOV = MIN_DATA_MOV OR DATA_MOV = MAX_DATA_MOV
                )
            )
            WHERE VARIACAO <> 0
            AND GRUPO IN ('MATERIA PRIMA','EMBALAGEM')
            ORDER BY VARIACAO DESC;

         """

        # Execute a consulta SQL com os parâmetros de data
        cursor.execute(sql, {'data_inicial': data_inicial, 'data_final': data_final})

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "DATA_INICIAL": row[0].strftime('%d/%m/%Y') if row[0] else None,
                "DATA_FINAL": row[1].strftime('%d/%m/%Y') if row[1] else None,
                "COD_PRODUTO": row[2],
                "SUBGRUPO_DESCRICAO": row[3],
                "GRUPO": row[4],
                "CUSTO_MEDIO_INICIAL": row[5],
                "CUSTO_MEDIO_FINAL": row[6],
                "VARIACAO": row[7]

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


def busca_variacao_custos_mp_c_mes_de_ref(data_inicial, data_final):
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Construa a string com os códigos de produto
       # codigos_str = ','.join(map(str, codigos_produto))

        # Execute a consulta SQL para buscar os custos
        sql = f"""
            SELECT
             I1.FIM_MES_ANTERIOR,	

             I1.CST_PRC_MD	CUSTO_FIM_MES_ANTERIOR,

             V1.*
FROM
(
 SELECT * FROM (
    SELECT
        MIN_DATA_MOV,
        MAX_DATA_MOV,
        COD_PRODUTO,
        SUBGRUPO_DESCRICAO,
        GRUPO,
        CUSTO_MEDIO_INICIAL,

       CASE
                WHEN NVL(CUSTO_MEDIO_FINAL, 0) = 0 THEN CUSTO_MEDIO_INICIAL
                ELSE CUSTO_MEDIO_FINAL
        END AS CUSTO_MEDIO_FINAL,
        CASE
                WHEN VARIACAO = -100 THEN 0
                ELSE VARIACAO
        END AS VARIACAO

    FROM (
        SELECT DISTINCT
            MIN_DATA_MOV,
            MAX_DATA_MOV,
            COD_PRODUTO,
            SUBGRUPO_DESCRICAO,
            GRUPO,
            CUSTO_MEDIO_INICIAL,
            CUSTO_MEDIO_FINAL,
            CASE
                WHEN NVL(CUSTO_MEDIO_INICIAL, 0) = 0 THEN 0
                ELSE ROUND(((NVL(CUSTO_MEDIO_FINAL, 0) / NVL(CUSTO_MEDIO_INICIAL, 0)) - 1) * 100, 2)
            END AS VARIACAO
        FROM (
            SELECT
                t.DATA_MOV,
                t.COD_PRODUTO,
                t.SUBGRUPO_DESCRICAO,
                t.GRUPO,
                MIN(t.DATA_MOV) OVER (PARTITION BY t.COD_PRODUTO) AS MIN_DATA_MOV,
                MAX(t.DATA_MOV) OVER (PARTITION BY t.COD_PRODUTO) AS MAX_DATA_MOV,
                FIRST_VALUE(CASE
                                WHEN TO_NUMBER(t.SALDOS_QUANT_TOTAL) <> 0 THEN TO_NUMBER(t.SALDOS_CUSTO_TOTAL) / TO_NUMBER(t.SALDOS_QUANT_TOTAL)
                                ELSE 0
                            END) OVER (PARTITION BY t.COD_PRODUTO ORDER BY t.DATA_MOV
                                        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS CUSTO_MEDIO_INICIAL,
                LAST_VALUE(CASE
                               WHEN TO_NUMBER(t.SALDOS_QUANT_TOTAL) <> 0 THEN TO_NUMBER(t.SALDOS_CUSTO_TOTAL) / TO_NUMBER(t.SALDOS_QUANT_TOTAL)
                               ELSE 0
                           END) OVER (PARTITION BY t.COD_PRODUTO ORDER BY t.DATA_MOV
                                       ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS CUSTO_MEDIO_FINAL
            FROM
                (
                    SELECT DISTINCT
                        K.KDEX_EMP_ID AS EMPRESA,
                        K.KDEX_PROD_ID AS COD_PRODUTO,
                        K.KDEX_DATA AS DATA_MOV,
                        K.KDEX_DTA_CAD AS DATA_CADASTRO,
                        K.KDEX_ENTR_SAI AS TIPO_ENTRAD_SAIDA,
                        K.KDEX_QTD AS MOV_QUANT,
                        K.KDEX_CTO AS MOV_CUSTO_TOTAL,
                        K.KDEX_QTDE_ANT AS SALDOS_QUANT_ANTERIOR,
                        K.KDEX_CTO_ANT AS SALDOS_CTO_TOTAL_ANTERIOR,
                        K.KDEX_QTDE_MEDIA AS SALDOS_QUANT_TOTAL,
                        K.KDEX_CUSTO_TOTAL AS SALDOS_CUSTO_TOTAL,
                        P.PROD_DESC AS SUBGRUPO_DESCRICAO,
                        GRP.GRUPO AS GRUPO
                    FROM
                        KARDEX K
                        JOIN PRODUTO P ON K.KDEX_PROD_EMP_ID = P.PROD_EMP_ID AND K.KDEX_PROD_ID = P.PROD_ID
                        JOIN (
                            SELECT DISTINCT
                                P.PROD_ID AS COD_PRODUTO,
                                P.PROD_DESC AS NOME_PRODUTO,
                                A.GENA_GEN_TGEN_ID AS TABELA_GENERICA,
                                A.GENA_GEN_ID AS COD_ITEM_TABELA,
                                A.GENA_GEN_TGEN_ID_PROPRIETARIO_ AS ID_SUBGRUPO,
                                G.GEN_DESCRICAO AS SUBGRUPO,
                                A.GENA_GEN_ID_PROPRIETARIO_DE AS ID_GRUPO,
                                (SELECT DECODE(
                                    A.GENA_GEN_ID_PROPRIETARIO_DE,
                                    1, 'MATERIA PRIMA',
                                    2, 'EMBALAGEM',
                                    3, 'MATERIAL SECUNDARIO',
                                    4, 'ESTOQUES DIVERSOS',
                                    5, 'IMOBILIZADO',
                                    6, 'MANUTENCAO INDUSTRIAL',
                                    9, 'PRODUTOS ACABADOS',
                                    10, 'PRODUTOS EM ELABORAÇÃO',
                                    99, 'DIVERSOS',
                                    'NÃO INFORMADO') FROM DUAL) AS GRUPO
                            FROM
                                GENER G
                                JOIN GENER_A A ON A.GENA_GEN_TGEN_ID = G.GEN_TGEN_ID AND A.GENA_GEN_EMP_ID = G.GEN_EMP_ID AND A.GENA_GEN_ID = G.GEN_ID
                                JOIN PRODUTO_AL AL ON AL.PROA_PROD_EMP_ID = A.GENA_GEN_EMP_ID AND AL.PROA_GEN_ID = G.GEN_ID
                                JOIN PRODUTO P ON P.PROD_ID = AL.PROA_PROD_ID
                            WHERE
                                A.GENA_GEN_TGEN_ID = 926
                                AND A.GENA_GEN_EMP_ID = 4
                                AND G.GEN_EMP_ID = 4
                        ) GRP ON GRP.COD_PRODUTO = K.KDEX_PROD_ID
                    WHERE
                        K.KDEX_EMP_ID = 4
                        AND K.KDEX_DATA >= TO_DATE(:data_inicial, 'DD/MM/YYYY')
                        AND K.KDEX_DATA <= TO_DATE(:data_final, 'DD/MM/YYYY')
                        AND NVL(P.PROD_SITUACAO, 'H') = 'H'
                ) t
            WHERE
                t.EMPRESA = 4
                
                AND (T.DATA_MOV BETWEEN TO_DATE(:data_inicial, 'DD/MM/YYYY') AND TO_DATE(:data_final, 'DD/MM/YYYY'))

        )
        WHERE DATA_MOV = MIN_DATA_MOV OR DATA_MOV = MAX_DATA_MOV
    )
)
WHERE VARIACAO <> 0
ORDER BY VARIACAO DESC



)    V1,
(
SELECT TO_CHAR(ACME_DATA, 'MM/YYYY') FIM_MES_ANTERIOR, ACME_PROD_ID, ACME_DATA, CST_PRC_MD
FROM (
    SELECT
        ACME_PROD_ID,
        ACME_DATA,
        DECODE((NVL(ACUM_ESTOQVM_ST.ACME_QTD_INI, 0) + NVL(ACUM_ESTOQVM_ST.ACME_QTD_ENTR, 0) - NVL(ACUM_ESTOQVM_ST.ACME_QTD_SAI, 0)),
               0, 0,
               (NVL(ACUM_ESTOQVM_ST.ACME_PRC_MD_INI, 0) + NVL(ACUM_ESTOQVM_ST.ACME_VLR_ENTR, 0) - NVL(ACUM_ESTOQVM_ST.ACME_VLR_SAI, 0)) /
               (NVL(ACUM_ESTOQVM_ST.ACME_QTD_INI, 0) + NVL(ACUM_ESTOQVM_ST.ACME_QTD_ENTR, 0) - NVL(ACUM_ESTOQVM_ST.ACME_QTD_SAI, 0))
              ) AS CST_PRC_MD,
        ROW_NUMBER() OVER (PARTITION BY ACME_PROD_ID ORDER BY ACME_DATA DESC) AS RN
    FROM ACUM_ESTOQVM_ST
    WHERE
        EXTRACT(YEAR FROM ACUM_ESTOQVM_ST.ACME_DATA) = EXTRACT(YEAR FROM ADD_MONTHS(:data_inicial, -1))
        AND EXTRACT(MONTH FROM ACUM_ESTOQVM_ST.ACME_DATA) = EXTRACT(MONTH FROM ADD_MONTHS(:data_final, -1))
        AND ACUM_ESTOQVM_ST.ACME_EMP_ID = 4
        AND DECODE((NVL(ACUM_ESTOQVM_ST.ACME_QTD_INI, 0) + NVL(ACUM_ESTOQVM_ST.ACME_QTD_ENTR, 0) - NVL(ACUM_ESTOQVM_ST.ACME_QTD_SAI, 0)),
                   0, 0,
                   (NVL(ACUM_ESTOQVM_ST.ACME_PRC_MD_INI, 0) + NVL(ACUM_ESTOQVM_ST.ACME_VLR_ENTR, 0) - NVL(ACUM_ESTOQVM_ST.ACME_VLR_SAI, 0)) /
                   (NVL(ACUM_ESTOQVM_ST.ACME_QTD_INI, 0) + NVL(ACUM_ESTOQVM_ST.ACME_QTD_ENTR, 0) - NVL(ACUM_ESTOQVM_ST.ACME_QTD_SAI, 0))
                  ) > 0
)
WHERE RN = 1
---and ACME_PROD_ID = 2012
)    I1

 WHERE

V1.COD_PRODUTO  = I1.ACME_PROD_ID
AND V1.GRUPO IN ('MATERIA PRIMA','EMBALAGEM')

         """

        # Execute a consulta SQL com os parâmetros de data
        cursor.execute(sql, {'data_inicial': data_inicial, 'data_final': data_final})

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "DATA_INICIAL": row[0].strftime('%d/%m/%Y') if row[0] else None,
                "DATA_FINAL": row[1].strftime('%d/%m/%Y') if row[1] else None,
                "COD_PRODUTO": row[2],
                "SUBGRUPO_DESCRICAO": row[3],
                "GRUPO": row[4],
                "CUSTO_MEDIO_INICIAL": row[5],
                "CUSTO_MEDIO_FINAL": row[6],
                "VARIACAO": row[7]

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


from conexao_ora import *
import json

def busca_calendario():
    try:
        #crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Execute a consulta SQL para buscar a inadimplência
        cursor.execute("""
SELECT
    CAL.DATA,
    TO_NUMBER(TO_CHAR(CAL.DATA, 'DD')) AS Dia,
    TO_NUMBER(TO_CHAR(CAL.DATA, 'MM')) AS Mes,
    TO_NUMBER(TO_CHAR(CAL.DATA, 'YY')) AS "AnoYY",
    TO_NUMBER(TO_CHAR(CAL.DATA, 'YYYY')) AS "AnoYYYY",
    TO_CHAR(CAL.DATA, 'day') AS "Descr_Dia",
    TO_CHAR(CAL.DATA, 'dy') AS "Descr_Dia_abrev",
    TO_CHAR(CAL.DATA, 'Month') AS "Descr_Mes",
    TO_CHAR(CAL.DATA, 'Mon') AS "Descr_Mes_abrev",
    TO_CHAR(CAL.DATA, 'dd month yyyy') AS Data_texto,
    TO_NUMBER(TO_CHAR(CAL.DATA, 'WW')) AS "Semana_do_Ano"
FROM (
    SELECT
        (TO_DATE(SEQ.MM || SEQ.YYYY, 'MM/YYYY') - 1) + SEQ.NUM AS "DATA"
    FROM (
        SELECT
            RESULT NUM,
            TO_CHAR(
                (TO_DATE('01/01/2024', 'DD/MM/YYYY')),
                'MM'
            ) AS "MM",
            TO_CHAR(
                (TO_DATE('01/01/2024', 'DD/MM/YYYY')),
                'YYYY'
            ) AS "YYYY"
        FROM (
            SELECT ROWNUM RESULT
            FROM DUAL
            CONNECT BY LEVEL <= (
                (
                    LAST_DAY(TO_DATE('31/12/2028', 'DD/MM/YYYY'))
                    - TRUNC(TO_DATE('01/01/2024', 'DD/MM/YYYY'))
                ) + 1
            )
        )
    ) SEQ
) CAL
        """)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "DATA": row[0].strftime('%d/%m/%y'),
                "DIA": row[1],
                "MES": row[2],
                "ANOYY": row[3],
                "ANOYYYY": row[4],
                "DESCR_DIA": row[5],
                "DESCR_DIA_ABREV": row[6],
                "DESCR_MES": row[7],
                "DESCR_MES_ABREV": row[8],
                "DATA_TEXTO": row[9],
                "SEMANA_DO_ANO": row[10]

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
# resultado_json = busca_calendario()
# print(resultado_json)

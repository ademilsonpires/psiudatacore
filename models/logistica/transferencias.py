from conexao_ora import *
import json
import cx_Oracle
from datetime import datetime


def busca_transferencias_em_aberto():
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Execute a consulta SQL para buscar a inadimplência
        cursor.execute("""
           ---CREATE OR REPLACE VIEW VIEW_TRANSFERENCIAS_DTA_FORMAT AS
SELECT
 TRUNC(PF.PEDF_DTA_EMIS)  DATA_EMISSAO,
 CASE 
        WHEN TRIM(C.CLI_FANTASIA) = 'PRESIDENTE DUTRA' THEN 'PSIU EXPRESS'
        WHEN PF.PEDF_OBS2 = 'EXPRESS' THEN 'PSIU EXPRESS'
        ELSE 'FATURAMENTO P/ ROTA'
 END AS TIPO, 
 'MATRIZ SAO LUIS' ORIGEM,
 C.CLI_FANTASIA DESTINO,
 PF.PEDF_LIQU_ID,
 PF.PEDF_ID,
 PP.PEDF_PROD_ID,
 PRO.PROD_DESC,
 SUM(PP.PEDF_QTDE) VOLUME
 
 
FROM 

PEDIDO_FAT PF,
PEDIDO_FAT_P PP,
PRODUTO PRO,
LIQUIDACAO L,
CLIENTE C
WHERE
PF.PEDF_EMP_ID       = 20
AND PF.PEDF_OPER_ID  = 4
AND PF.PEDF_SITUACAO = 0
AND PP.PEDF_PROD_ID NOT IN (14372, 14486)
AND PF.PEDF_EMP_ID  = PP.PEDF_PEDF_EMP_ID
AND PF.PEDF_ID      = PP.PEDF_PEDF_ID
AND PRO.PROD_EMP_ID = PP.PEDF_PROD_EMP_ID
AND PRO.PROD_ID     = PP.PEDF_PROD_ID
AND L.LIQU_ID       = PF.PEDF_LIQU_ID
AND L.LIQU_EMP_ID   = PF.PEDF_EMP_ID
AND L.LIQU_DTA_LIB IS NULL
AND PF.PEDF_NR_NF  IS NOT NULL
AND C.CLI_EMP_ID = PF.PEDF_EMP_ID
AND C.CLI_ID = PF.PEDF_CLI_ID

GROUP BY
  
 TRUNC(PF.PEDF_DTA_EMIS),
 PF.PEDF_OBS2,
 PF.PEDF_EMP_ID,
 PF.PEDF_LIQU_ID,
 PF.PEDF_ID,
 PP.PEDF_PROD_ID,
 PRO.PROD_DESC,
 C.CLI_FANTASIA

ORDER BY TRUNC(PF.PEDF_DTA_EMIS)
 

        """)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {

                "DATA_EMISSAO": row[0].strftime('%Y-%m-%d') if isinstance(row[2], datetime) else None,
                "TIPO": row[1],
                "ORIGEM": row[2],
                "DESTINO": row[3],
                "PEDF_LIQU_ID": row[4],
                "PEDF_ID": row[5],
                "PEDF_PROD_ID": row[6],
                "PROD_DESC": row[7],
                "VOLUME": row[8]

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


#
# print(busca_transferencias_em_aberto())


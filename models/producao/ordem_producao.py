from conexao_ora import *
import json
import cx_Oracle
from datetime import datetime
from typing import Dict



def busca_ordens_old():
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Execute a consulta SQL para buscar a inadimplência
        cursor.execute("""
           SELECT
           OP.ORPR_EMP_ID                         EMPRESA
        ,  OP.ORPR_NR_ORDEM                       NR_ORDEM
        ,  OP.ORPR_DTA_PROGRAMADA                 DATA_PROGRAMADA 
        ,  OP.ORPR_DTA_CAD                        DATA_CADASTRO 
        ,  OP.ORPR_LIPR_ID                        LINHA   
        ,  OP.ORPR_HORA_SEQUENCIADA
        ,  OP.ORPR_STATUS
        ,  OP.ORPR_DTA_REALIZADA                  DATA_REALIZADA
        ,  OP.ORPR_HORA_INI_REALIZADA             HORA_INICIAL
        ,  OP.ORPR_HORA_FIM_REALIZADA             HORA_FINAL
        ,  OPP.ORPR_PROD_ID                       COD_PRODUTO
        ,  P.PROD_DESC                            NOME_PRODUTO
        ,  OPP.ORPR_QTDE	                      QTDE_PROGRAMADA
        ,  OPP.ORPR_PROV_SERIE                    SERIE
        ,  U.USR_NOME                             USUARIO_CADASTRO 
        
        FROM 
        
        ORDEM_DE_PRODUCAO OP,
        ORDEM_PRODUCAO_P  OPP,
        PRODUTO           P,  
        USUARIO           U
        
        WHERE OP.ORPR_EMP_ID = 4
        AND OP.ORPR_DTA_PROGRAMADA >= TO_DATE(sysdate,'DD/MM/YYYY') ---'25/06/2024'
        AND OP.ORPR_STATUS   = 'A'
        AND OP.ORPR_USR_ID   = U.USR_ID 
        AND OP.ORPR_NR_ORDEM = OPP.ORPR_ORPROD_NR_ORDEM
        AND OP.ORPR_EMP_ID   = OPP.ORPR_ORPROD_EMP_ID
        AND OPP.ORPR_PROD_EMP_ID = P.PROD_EMP_ID
        AND OPP.ORPR_PROD_ID     = P.PROD_ID
    
        """)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "EMPRESA": row[0],
                "NR_ORDEM": row[1],
                "DATA_PROGRAMADA": row[2].strftime('%Y-%m-%d') if isinstance(row[2], datetime) else None,
                "DATA_CADASTRO": row[3].strftime('%Y-%m-%d') if isinstance(row[3], datetime) else None,
                "LINHA": row[4],
                "ORPR_HORA_SEQUENCIADA": row[5],
                "ORPR_STATUS": row[6],
                "DATA_REALIZADA": row[7].strftime('%Y-%m-%d') if isinstance(row[7], datetime) else None,
                "HORA_INICIAL": row[8],
                "HORA_FINAL": row[9],
                "COD_PRODUTO": row[10],
                "NOME_PRODUTO": row[11],
                "QTDE_PROGRAMADA": row[12],
                "SERIE": row[13],
                "USUARIO_CADASTRO": row[14]
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




def busca_ordens(orpr_lipr_id=None):
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Consulta SQL com filtro opcional
        sql_query = """
           SELECT
           OP.ORPR_EMP_ID                         EMPRESA
        ,  OP.ORPR_NR_ORDEM                       NR_ORDEM
        ,  OP.ORPR_DTA_PROGRAMADA                 DATA_PROGRAMADA 
        ,  OP.ORPR_DTA_CAD                        DATA_CADASTRO 
        ,CASE 
           WHEN OP.ORPR_LIPR_ID = 6 THEN 3
           WHEN OP.ORPR_LIPR_ID = 4 THEN 2
           ELSE OP.ORPR_LIPR_ID
        END AS LINHA   
        ,  OP.ORPR_HORA_SEQUENCIADA
        ,  OP.ORPR_STATUS
        ,  OP.ORPR_DTA_REALIZADA                  DATA_REALIZADA
        ,  OP.ORPR_HORA_INI_REALIZADA             HORA_INICIAL
        ,  OP.ORPR_HORA_FIM_REALIZADA             HORA_FINAL
        ,  OPP.ORPR_PROD_ID                       COD_PRODUTO
        ,  P.PROD_DESC                            NOME_PRODUTO
        ,  OPP.ORPR_QTDE                          QTDE_PROGRAMADA
        ,  OPP.ORPR_PROV_SERIE                    SERIE
        ,  U.USR_NOME                             USUARIO_CADASTRO 
        FROM 
        ORDEM_DE_PRODUCAO OP,
        ORDEM_PRODUCAO_P  OPP,
        PRODUTO           P,  
        USUARIO           U
        WHERE OP.ORPR_EMP_ID = 4
        AND OP.ORPR_DTA_PROGRAMADA >= TO_DATE(sysdate,'DD/MM/YYYY')
        AND OP.ORPR_STATUS   = 'A'
        AND OP.ORPR_USR_ID   = U.USR_ID 
        AND OP.ORPR_NR_ORDEM = OPP.ORPR_ORPROD_NR_ORDEM
        AND OP.ORPR_EMP_ID   = OPP.ORPR_ORPROD_EMP_ID
        AND OPP.ORPR_PROD_EMP_ID = P.PROD_EMP_ID
        AND OPP.ORPR_PROD_ID     = P.PROD_ID
        """
        #permuta de codigo das linhas de produção, existem codigos diferentes no saib para nomeclatura usada pelos usuárioos
        if orpr_lipr_id == 3:
            orpr_lipr_id = 6

        if orpr_lipr_id == 2:
            orpr_lipr_id = 4


        # Adicione o filtro ORPR_LIPR_ID se fornecido
        if orpr_lipr_id is not None:
            sql_query += " AND OP.ORPR_LIPR_ID = :orpr_lipr_id"

        # Execute a consulta SQL
        if orpr_lipr_id is not None:
            cursor.execute(sql_query, orpr_lipr_id=orpr_lipr_id)
        else:
            cursor.execute(sql_query)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "EMPRESA": row[0],
                "NR_ORDEM": row[1],
                "DATA_PROGRAMADA": row[2].strftime('%Y-%m-%d') if isinstance(row[2], datetime) else None,
                "DATA_CADASTRO": row[3].strftime('%Y-%m-%d') if isinstance(row[3], datetime) else None,
                "LINHA": row[4],
                "ORPR_HORA_SEQUENCIADA": row[5],
                "ORPR_STATUS": row[6],
                "DATA_REALIZADA": row[7].strftime('%Y-%m-%d') if isinstance(row[7], datetime) else None,
                "HORA_INICIAL": row[8],
                "HORA_FINAL": row[9],
                "COD_PRODUTO": row[10],
                "NOME_PRODUTO": row[11],
                "QTDE_PROGRAMADA": row[12],
                "SERIE": row[13],
                "USUARIO_CADASTRO": row[14]
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


#busca ordens por id
def busca_ordem_id(id_ordem=None):
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Consulta SQL com filtro opcional
        sql_query = """
            SELECT
    OP.ORPR_EMP_ID                          EMPRESA,
    OP.ORPR_NR_ORDEM                        NR_ORDEM,
    OP.ORPR_DTA_PROGRAMADA                  DATA_PROGRAMADA,
    OP.ORPR_DTA_CAD                         DATA_CADASTRO,
    CASE 
        WHEN OP.ORPR_LIPR_ID = 6 THEN 3
        WHEN OP.ORPR_LIPR_ID = 4 THEN 2
        ELSE OP.ORPR_LIPR_ID
    END AS LINHA,
    OP.ORPR_HORA_SEQUENCIADA,
    OP.ORPR_STATUS,
    OP.ORPR_DTA_REALIZADA                   DATA_REALIZADA,
    OP.ORPR_HORA_INI_REALIZADA              HORA_INICIAL,
    OP.ORPR_HORA_FIM_REALIZADA              HORA_FINAL,
    OPP.ORPR_PROD_ID                        COD_PRODUTO,
    P.PROD_DESC                             NOME_PRODUTO,
    OPP.ORPR_QTDE                           QTDE_PROGRAMADA,
    OPP.ORPR_PROV_SERIE                     SERIE,
    U.USR_NOME                              USUARIO_CADASTRO,
    DAP.QTDE_PRODUZIDA,
    DAP.GAP
FROM 
    ORDEM_DE_PRODUCAO OP,
    ORDEM_PRODUCAO_P OPP,
    PRODUTO P,
    USUARIO U,
    (
        SELECT
            EMPRESA_PRODUCAO,
            CASE 
                WHEN LINHA_PRODUCAO = 3 THEN 6
                WHEN LINHA_PRODUCAO = 2 THEN 4
                ELSE LINHA_PRODUCAO
            END AS LINHA_PRODUCAO,
            ORDEM_PRODUCAO,
            SUM(QTDE_PRODUZIDA) QTDE_PRODUZIDA,
            SUM(GAP) GAP
        FROM
            DATACORE_APONT_PRODUCAO
        GROUP BY
            EMPRESA_PRODUCAO,
            CASE 
                WHEN LINHA_PRODUCAO = 3 THEN 6
                WHEN LINHA_PRODUCAO = 2 THEN 4
                ELSE LINHA_PRODUCAO
            END,
            ORDEM_PRODUCAO
    ) DAP
WHERE
    OP.ORPR_NR_ORDEM = OPP.ORPR_ORPROD_NR_ORDEM
    AND OPP.ORPR_PROD_EMP_ID = P.PROD_EMP_ID
    AND OPP.ORPR_PROD_ID = P.PROD_ID
    AND OP.ORPR_USR_ID = U.USR_ID
    AND OP.ORPR_EMP_ID = 4
    AND OP.ORPR_DTA_PROGRAMADA >= TO_DATE(sysdate, 'DD/MM/YYYY')
    AND OP.ORPR_STATUS = 'A'
    ---AND OP.ORPR_NR_ORDEM = 29965 clausula para testes
    AND DAP.EMPRESA_PRODUCAO = OP.ORPR_EMP_ID
    AND DAP.ORDEM_PRODUCAO = OP.ORPR_NR_ORDEM
    AND DAP.LINHA_PRODUCAO = OP.ORPR_LIPR_ID

        """

        # Adicione o filtro ORPR_LIPR_ID se fornecido
        if id_ordem is not None:
            sql_query += " AND OP.ORPR_NR_ORDEM = :id_ordem"

        # Execute a consulta SQL
        if id_ordem is not None:
            cursor.execute(sql_query, id_ordem=id_ordem)
        else:
            cursor.execute(sql_query)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "EMPRESA": row[0],
                "NR_ORDEM": row[1],
                "DATA_PROGRAMADA": row[2].strftime('%Y-%m-%d') if isinstance(row[2], datetime) else None,
                "DATA_CADASTRO": row[3].strftime('%Y-%m-%d') if isinstance(row[3], datetime) else None,
                "LINHA": row[4],
                "ORPR_HORA_SEQUENCIADA": row[5],
                "ORPR_STATUS": row[6],
                "DATA_REALIZADA": row[7].strftime('%Y-%m-%d') if isinstance(row[7], datetime) else None,
                "HORA_INICIAL": row[8],
                "HORA_FINAL": row[9],
                "COD_PRODUTO": row[10],
                "NOME_PRODUTO": row[11],
                "QTDE_PROGRAMADA": row[12],
                "SERIE": row[13],
                "USUARIO_CADASTRO": row[14],
                "QTDE_PRODUZIDA": row[15],
                "GAP": row[16]
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


def busca_serie_ordem_id(id_ordem=None):
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Consulta SQL com filtro opcional
        sql_query = """
       SELECT B.PROD_EMP_ID EMPRESA,                                           

       PP.PROV_PROD_ID_PRODUTO_FILHO_DE COD_SKU,                              

       B.PROD_DESC SKU,                                                 

       B.PROD_UN_VDA UNIDADE,                                                 

       (NVL(OP.ORPR_QTDE, 0) * NVL(PP.PROV_CONVERSOR, 0)) SUB_NECESSARIO,     

       (NVL(OP.ORPR_QTDE, 0) * NVL(PP.PROV_CONVERSOR, 0)) +                   

       ((NVL(OP.ORPR_QTDE, 0) * NVL(PP.PROV_CONVERSOR, 0)) *                  

       NVL(D.PROA_PERC_PERDA_TOL, 0) / 100) TOT_NECESSARIO                    

  FROM                                                                        

       PRODUTO_EV_SERIE P,         ------PRODUTO PAI                          

       PRODUTO_EV       PP,        -------Filhos                              

       PRODUTO          B,                                                    

       PRODUTO          B1,                                                   

       PRODUTO_TP       C,                                                    

       PRODUTO_AL       D,                                                    

       ACUM_ESTOQ       E,                                                    

       GENER            SUB_GRUPO,                                            

       GENER            GRUPO,                                                

       GENER_A          F,                                                    

       EMPRESA          G,                                                    

       ORDEM_PRODUCAO_P OP                                                    

 WHERE                                                                        

     P.PROV_EMP_ID        = PP.PROV_EMP_ID                                    

 AND P.PROV_PROD_EMP_ID   = PP.PROV_PROD_EMP_ID                               

 AND P.PROV_PROD_ID       = PP.PROV_PROD_ID                                   

 AND P.PROV_SERIE         = PP.PROV_SERIE                                     

 AND PP.PROV_HABILITADO   = 'S'                                             

 AND P.PROV_SERIE         = OP.ORPR_PROV_SERIE                                

 AND B.PROD_EMP_ID = PP.PROV_PROD_EMP_ID_PRODUTO_FILHO                        

 AND B.PROD_ID = PP.PROV_PROD_ID_PRODUTO_FILHO_DE                             

 AND OP.ORPR_ORPROD_EMP_ID = 4

 AND OP.ORPR_ORPROD_NR_ORDEM = :id_ordem

 AND OP.ORPR_PROD_EMP_ID = 4

 AND B1.PROD_EMP_ID = P.PROV_PROD_EMP_ID                                      

 AND B1.PROD_ID = P.PROV_PROD_ID                                              

 AND C.PROT_PROD_EMP_ID = B.PROD_EMP_ID                                       

 AND C.PROT_PROD_ID = B.PROD_ID                                               

 AND D.PROA_PROD_EMP_ID(+) = B.PROD_EMP_ID                                    

 AND D.PROA_PROD_ID(+) = B.PROD_ID                                            

 AND E.ACME_PROD_EMP_ID(+) = B.PROD_EMP_ID                                    

 AND E.ACME_PROD_ID(+) = B.PROD_ID                                            

 AND SUB_GRUPO.GEN_TGEN_ID(+) = D.PROA_GEN_TGEN_ID                            

 AND SUB_GRUPO.GEN_EMP_ID(+) = D.PROA_GEN_EMP_ID                             

 AND SUB_GRUPO.GEN_ID(+) = D.PROA_GEN_ID                                      

 AND F.GENA_GEN_TGEN_ID(+) = D.PROA_GEN_TGEN_ID                               

 AND F.GENA_GEN_EMP_ID(+) = D.PROA_GEN_EMP_ID                                 

 AND F.GENA_GEN_ID(+) = D.PROA_GEN_ID                                         

 AND GRUPO.GEN_TGEN_ID(+) = F.GENA_GEN_TGEN_ID_PROPRIETARIO_                  

 AND GRUPO.GEN_EMP_ID(+) = F.GENA_GEN_EMP_ID_PROPRIETARIO_D                   

 AND GRUPO.GEN_ID(+) = F.GENA_GEN_ID_PROPRIETARIO_DE                          

 AND G.EMP_ID = B.PROD_EMP_ID                                                 

 AND P.PROV_PROD_EMP_ID = 4

 AND B1.PROD_ID = OP.ORPR_PROD_ID                                             

 GROUP BY B.PROD_EMP_ID,                                                      

          PP.PROV_PROD_ID_PRODUTO_FILHO_DE,                                    

          B.PROD_DESC,                                                        

          B.PROD_UN_VDA,                                                      

          OP.ORPR_QTDE,                                                       

          PP.PROV_CONVERSOR,                                                   

          D.PROA_PERC_PERDA_TOL                                               
                                                    

        """
        # Execute a consulta SQL
        if id_ordem is not None:
            cursor.execute(sql_query, id_ordem=id_ordem)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "EMPRESA": row[0],
                "COD_SKU": row[1],
                "SKU": row[2],
                "UNIDADE": row[3],
                "SUB_NECESSARIO": row[4],
                "TOT_NECESSARIO": row[5],

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


def busca_check_serie_ordem_id(id_ordem=None):
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Consulta SQL com filtro opcional
        sql_query = """
            SELECT
                COD_MAT_PRIMA,
                STATUS
            FROM DATACORE_APONT_CHECK_MP T
            WHERE T.ORDEM_PRODUCAO = :id_ordem
            AND T.EMPRESA_PRODUCAO = 4
                                      


        """
        # Execute a consulta SQL
        if id_ordem is not None:
            cursor.execute(sql_query, id_ordem=id_ordem)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "COD_MAT_PRIMA": row[0],
                "STATUS": row[1]

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


def busca_hist_apontamento_ordem_id(id_ordem=None):
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Consulta SQL com filtro opcional
        sql_query = """
            SELECT * FROM DATACORE_APONT_PRODUCAO T WHERE T.ORDEM_PRODUCAO = :id_ordem
            AND T.EMPRESA_PRODUCAO = 4
                   """
        # Execute a consulta SQL
        if id_ordem is not None:
            cursor.execute(sql_query, id_ordem=id_ordem)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "DATA_PRODUCAO": row[0],
                "HORA_PRODUCAO": row[1],
                "QTDE_PRODUZIDA": row[2],
                "GAP": row[3],
                "OBS": row[4]

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



def busca_linhas_producao_com_ordens():
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Execute a consulta SQL para buscar a inadimplência
        cursor.execute("""
                SELECT DISTINCT OP.ORPR_EMP_ID EMPRESA,
                                CASE
                                  WHEN OP.ORPR_LIPR_ID = 6 THEN
                                   3
                                  WHEN OP.ORPR_LIPR_ID = 4 THEN
                                   2
                                  ELSE
                                   OP.ORPR_LIPR_ID
                                END AS LINHA,
                                SUM(OPP.ORPR_QTDE) QTDE_PROGRAMADA,
                                NVL(D.QTDE_PRODUZIDA, 0) QTDE_PRODUZIDA
                
                  FROM ORDEM_DE_PRODUCAO OP
                  JOIN ORDEM_PRODUCAO_P OPP ON OP.ORPR_NR_ORDEM = OPP.ORPR_ORPROD_NR_ORDEM
                                            AND OP.ORPR_EMP_ID = OPP.ORPR_ORPROD_EMP_ID
                  JOIN PRODUTO P ON OPP.ORPR_PROD_EMP_ID = P.PROD_EMP_ID
                                 AND OPP.ORPR_PROD_ID = P.PROD_ID
                  LEFT JOIN (select EMPRESA_PRODUCAO,
                                    LINHA_PRODUCAO,
                                    ORDEM_PRODUCAO,
                                    SUM(QTDE_PRODUZIDA) QTDE_PRODUZIDA
                               from DATACORE_APONT_PRODUCAO
                              GROUP BY EMPRESA_PRODUCAO, LINHA_PRODUCAO, ORDEM_PRODUCAO) D 
                         ON D.EMPRESA_PRODUCAO = OP.ORPR_EMP_ID
                        AND D.LINHA_PRODUCAO = OP.ORPR_LIPR_ID
                
                 WHERE OP.ORPR_EMP_ID = 4
                   AND OP.ORPR_DTA_PROGRAMADA >= TO_DATE(sysdate, 'DD/MM/YYYY')
                   AND OP.ORPR_STATUS = 'A'
                 GROUP BY OP.ORPR_EMP_ID, 
                          OP.ORPR_LIPR_ID, 
                          NVL(D.QTDE_PRODUZIDA, 0)

        """)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "EMPRESA": row[0],
                "LINHA": row[1],
                "QTDE_PROGRAMADA": row[2],
                "QTDE_PRODUZIDA": row[3],

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



def calcular_gap_produto_ordem_id(id_produto=None, id_linha=None, quantidade_produzida=None):
    try:
        # Regras para alterar o valor de id_linha
        if id_linha == 3:
            id_linha = 6
        elif id_linha == 2:
            id_linha = 4

        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Consulta SQL com filtro opcional
        sql_query = """
        SELECT
            CMAQ_VELOC_NOM_EFICIENCIA
        FROM
            CAPAC_MAQ, LINHA_PRO, PRODUTO, USUARIO
        WHERE
            CMAQ_LIPR_EMP_ID = 4
            AND CMAQ_LIPR_ID = :id_linha
            AND CMAQ_PROD_ID = :id_produto
            AND CMAQ_LIPR_EMP_ID = LIPR_EMP_ID
            AND CMAQ_LIPR_ID = LIPR_ID
            AND CMAQ_PROD_EMP_ID = PROD_EMP_ID
            AND CMAQ_PROD_ID = PROD_ID
            AND CMAQ_USR_ID = USR_ID
        """

        # Execute a consulta SQL
        cursor.execute(sql_query, id_produto=id_produto, id_linha=id_linha)
        row = cursor.fetchone()

        if row:
            # Valor da meta de eficiência
            eficiencia_meta = row[0]

            # Calcular o gap
            gap = eficiencia_meta - quantidade_produzida

            # Feche o cursor e a conexão com o banco de dados
            cursor.close()
            conn.close()
            # Retornar o valor do gap em JSON
            return json.dumps({"gap": gap})
        else:
            # Caso não haja dados, retorne uma mensagem apropriada
            cursor.close()
            conn.close()
            return json.dumps({"Erro": "Nenhum dado encontrado para os parâmetros fornecidos"})

    except cx_Oracle.DatabaseError as e:
        # Em caso de erro, retorne uma mensagem de erro
        return json.dumps({"Erro": f"Erro ao conectar ou executar consulta: {e}"})

# resultado = calcular_gap_produto_ordem_id(id_produto=50, id_linha=4, quantidade_produzida=550)
# print(resultado)
# Saída: {"gap": 50}
print(busca_ordem_id(29965))
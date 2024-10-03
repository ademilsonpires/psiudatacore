from conexao_ora import *
import json


def busca_ordens_de_compra_por_aprovador(aprovador:int):
    try:
        # crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Execute a consulta SQL para buscar a inadimplência
        cursor.execute("""
        SELECT
     ORDEM_COM.ORDC_EMP_ID         COD_EMP
    ,ORDEM_COM.ORDC_ID             NR_ORDEM 
    --
    ,ORDEM_COM.ORDC_FORN_ID
    ,FORNECEDOR.FORN_FANTASIA
    --
    ,ORDEM_COM.ORDC_CLASSIF        OBSERVACAO
    ,ORDEM_COM.ORDC_VLR_TOT        VALOR_TOTAL
    ,ORDEM_COM.ORDC_DTA_ENT        DATA_PREV_ENTREGA
    ,ORDEM_COM_A.ORDC_APRO_USR_ID  COD_USU_APROVADOR
    ,USUARIO.USR_NOME              NOME_APROVADOR
FROM 
     ORDEM_COM
    ,ORDEM_COM_A
    ,USUARIO
    ,FORNECEDOR
WHERE
     ORDEM_COM.ORDC_EMP_ID        = ORDEM_COM_A.ORDC_ORDC_EMP_ID
AND  ORDEM_COM.ORDC_ID            = ORDEM_COM_A.ORDC_ORDC_ID
--
AND FORNECEDOR.FORN_ID = ORDEM_COM.ORDC_FORN_ID
--
AND  ORDEM_COM_A.ORDC_APRO_USR_ID = USUARIO.USR_ID
AND  ORDEM_COM.ORDC_ENVIO_APROVADORES = 'S'
--
AND  ORDEM_COM.ORDC_SITUACAO  IS NULL
--BUSCAR ORDENS POR APROVADOR
AND ORDEM_COM_A.ORDC_ASSIN_ELETR IS NULL 

AND ORDEM_COM_A.ORDC_APRO_USR_ID = :APROVADOR ---SERÁ UM PARAMETRO PASSADO NO LOGIN DO USUÁRIO APROVADOR
 
ORDER BY
     ORDEM_COM.ORDC_EMP_ID
    ,ORDEM_COM.ORDC_ID 

        """,aprovador=aprovador)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "COD_EMP": row[0],
                "NR_ORDEM": row[1],
                "ORDC_FORN_ID": row[2],
                "FORN_FANTASIA": row[3],
                "OBSERVACAO": row[4],
                "VALOR_TOTAL": float(row[5]),
                "DATA_PREV_ENTREGA": row[6].strftime('%Y-%m-%d'),
                "COD_USU_APROVADOR": row[7],
                "NOME_APROVADOR": row[8]

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
def busca_itens_ordens_de_compra_por_ordem(empresa:int, id_ordem:int):
    try:
        # crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Execute a consulta SQL para buscar a inadimplência
        cursor.execute("""
        SELECT
     ORDEM_COM_I.ORDC_ORDC_EMP_ID
    ,DECODE(ORDEM_COM_I.ORDC_PROD_ID,NULL,ORDEM_COM_I.ORDC_ID,ORDEM_COM_I.ORDC_PROD_ID) ID_PRODUTO
    ,DECODE(PRODUTO.PROD_DESC,NULL,ORDEM_COM_I.ORDC_DESC,PRODUTO.PROD_DESC) NOME_PRODUTO
    ,DECODE(PRODUTO.PROD_UN_VDA,NULL,ORDEM_COM_I.ORDC_UN,PRODUTO.PROD_UN_VDA) UNIDADE
    ,ORDEM_COM_I.ORDC_QTDE
    ,ORDEM_COM_I.ORDC_VLR 
FROM 
     ORDEM_COM
    ,ORDEM_COM_I
    ,PRODUTO 
WHERE
     ORDEM_COM.ORDC_EMP_ID        = ORDEM_COM_I.ORDC_ORDC_EMP_ID
AND  ORDEM_COM.ORDC_ID            = ORDEM_COM_I.ORDC_ORDC_ID
--
AND  ORDEM_COM_I.ORDC_PROD_EMP_ID = PRODUTO.PROD_EMP_ID(+)
AND  ORDEM_COM_I.ORDC_PROD_ID     = PRODUTO.PROD_ID(+)
--
AND  ORDEM_COM_I.ORDC_ORDC_EMP_ID = :empresa
AND  ORDEM_COM_I.ORDC_ORDC_ID     = :id_ordem

 

        """,empresa=empresa, id_ordem=id_ordem)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
            "ORDC_ORDC_EMP_ID": row[0],
            "ID_PRODUTO": row[1],
            "NOME_PRODUTO": row[2],
            "UNIDADE": row[3],
            "ORDC_QTDE": float(row[4]),
            "ORDC_VLR": float(row[5]),

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


def verifica_status_aprovadores(empresa: int, id_ordem: int):
    try:
        # crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Execute a consulta SQL para buscar a inadimplência
        cursor.execute("""
            SELECT 
                ORDC_ORDC_EMP_ID,
                ORDC_ORDC_ID,
                ORDC_APRO_USR_ID,
                ORDC_ASSIN_ELETR,
                ORDC_DTA_APROV
            FROM 
                ordem_com_a A
            WHERE 
                (A.ORDC_ASSIN_ELETR IS NULL OR A.ORDC_ASSIN_ELETR = 'N')
                AND A.ordc_ordc_emp_id = :empresa
                AND A.ordc_ordc_id = :id_ordem

        """, empresa=empresa, id_ordem=id_ordem)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {

                "ORDC_ORDC_EMP_ID": row[0],
                "ORDC_ORDC_ID": row[1],
                "ORDC_APRO_USR_ID": row[2],
                "ORDC_ASSIN_ELETR": row[3],
                "ORDC_DTA_APROV": row[4],

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


def verifica_aprovacao_de_aprovadores(empresa: int, id_ordem: int):
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Execute a consulta SQL para buscar a inadimplência
        cursor.execute("""
            SELECT 
                ORDC_ORDC_EMP_ID,
                ORDC_ORDC_ID,
                ORDC_APRO_USR_ID,
                ORDC_ASSIN_ELETR,
                ORDC_DTA_APROV
            FROM 
                ordem_com_a A
            WHERE 
                (A.ORDC_ASSIN_ELETR IS NULL OR A.ORDC_ASSIN_ELETR = 'N')
                AND A.ordc_ordc_emp_id = :empresa
                AND A.ordc_ordc_id = :id_ordem

        """, empresa=empresa, id_ordem=id_ordem)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Feche o cursor e a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Verifique se há registros
        if rows:
            # Se existirem registros, a aprovação ainda não está completa
            return json.dumps({"status": "nao_aprovada_totalmente"})
        else:
            # Se não houver registros, todos os aprovadores já aprovaram
            return json.dumps({"status": "aprovada_totalmente"})

    except cx_Oracle.DatabaseError as e:
        # Em caso de erro, retorne uma mensagem de erro
        return json.dumps({"Erro": f"Erro ao conectar ou executar consulta: {e}"})


def grava_status_aprovacao_ordem(empresa: int, id_ordem: int):
    try:
        # Verifica a aprovação dos aprovadores
        status_aprovacao_str = verifica_aprovacao_de_aprovadores(empresa, id_ordem)

        # Converte a string JSON retornada em um dicionário
        status_aprovacao = json.loads(status_aprovacao_str)

        # Verifica se a ordem foi totalmente aprovada
        if status_aprovacao.get("status") == "aprovada_totalmente":
            # Crie a conexão
            conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

            # Crie um cursor para executar o update
            cursor = conn.cursor()

            # Execute o comando de UPDATE para alterar o status da ordem
            cursor.execute("""
                UPDATE ORDEM_COM ORDC 
                SET ORDC.ORDC_SITUACAO = 'A'
                WHERE ORDC.ORDC_EMP_ID = :empresa
                AND ORDC.ORDC_ID = :id_ordem
            """, empresa=empresa, id_ordem=id_ordem)

            # Confirme a transação (commit)
            conn.commit()

            # Feche o cursor e a conexão com o banco de dados
            cursor.close()
            conn.close()

            # Retorne uma mensagem de sucesso
            return {"status": "success", "message": "Ordem atualizada com sucesso"}

        else:
            # Se ainda houver aprovadores pendentes, não atualiza
            return {"status": "pendente", "message": "Ordem não foi atualizada, ainda há aprovadores pendentes"}

    except cx_Oracle.DatabaseError as e:
        # Em caso de erro, retorne uma mensagem de erro
        return {"status": "error", "message": f"Erro ao atualizar ordem: {e}"}

def grava_aprovacao_do_aprovador(status: str, empresa: int, id_ordem: int, id_aprovador: int):
    try:
        # Crie a conexão com o banco de dados
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar o update
        cursor = conn.cursor()

        # Execute o comando de UPDATE para atualizar o status de aprovação do aprovador
        cursor.execute("""
            UPDATE ORDEM_COM_A ORDCA 
            SET ORDCA.ORDC_ASSIN_ELETR = :status, 
                ORDCA.ORDC_DTA_APROV = SYSDATE
            WHERE ORDCA.ORDC_ORDC_EMP_ID = :empresa
            AND ORDCA.ORDC_ORDC_ID = :id_ordem
            AND ORDCA.ORDC_APRO_USR_ID = :id_aprovador
        """, status=status, empresa=empresa, id_ordem=id_ordem, id_aprovador=id_aprovador)

        # Confirme a transação (commit) para a tabela ORDEM_COM_A
        conn.commit()

        # Feche o cursor e a conexão com o banco de dados
        cursor.close()
        conn.close()

        # Chama a função para gravar o status da ordem na tabela ORDEM_COM
        resultado_gravacao_ordem = grava_status_aprovacao_ordem(empresa, id_ordem)

        # Retorne o resultado da atualização do status do aprovador e da ordem
        return {
            "status": "success",
            "message": "Aprovação do aprovador atualizada com sucesso",
            "ordem_status": resultado_gravacao_ordem
        }

    except cx_Oracle.DatabaseError as e:
        # Em caso de erro, retorne uma mensagem de erro
        return {"status": "error", "message": f"Erro ao atualizar aprovação do aprovador: {e}"}

# Exemplo de uso da função
# resultado_json = busca_ordens_de_compra_por_aprovador(505)
#resultado_json =busca_itens_ordens_de_compra_por_ordem(4,63299)
#resultado_json =verifica_aprovacao_de_aprovadores(20,15534)
# resultado_json =grava_aprovacao_do_aprovador('S',20,15534,505)
# print(resultado_json)

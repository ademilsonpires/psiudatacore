from conexao_ora import *
import json

def busca_inadimplencia():
    try:
        #crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Execute a consulta SQL para buscar a inadimplência
        cursor.execute("""
        SELECT TITULO,
       CLI_COD,
       TP_PESSOA,
       ---ROTA_ID AS CODIGO_VENDEDOR,
 ROTA_ID AS ROTA_VENDEDOR,
       SETOR_ID AS SUPERVISOR,
       CLI_RAZAO,
       CLI_FANTASIA,
       --EMP_COD,
       CNPJ_CPF,
              (SELECT MAX(CIDADE.GEN_DESCRICAO) CIDADE_UF
          FROM CLIENTE_E CE, GENER CIDADE, GENER_A GA_UF, GENER UF
         WHERE CE.CLIE_CLI_EMP_ID = EMP_COD
           AND CE.CLIE_CLI_ID = CLI_COD
           AND CE.CLIE_GEN_TGEN_ID_CIDADE_DE = CIDADE.GEN_TGEN_ID
           AND CE.CLIE_GEN_EMP_ID = CIDADE.GEN_EMP_ID
           AND CE.CLIE_GEN_ID_CIDADE_DE = CIDADE.GEN_ID
           AND GA_UF.GENA_GEN_TGEN_ID = CIDADE.GEN_TGEN_ID
           AND GA_UF.GENA_GEN_EMP_ID = CIDADE.GEN_EMP_ID
           AND GA_UF.GENA_GEN_ID = CIDADE.GEN_ID
           AND UF.GEN_TGEN_ID = GA_UF.GENA_GEN_TGEN_ID_PROPRIETARIO_
           AND UF.GEN_EMP_ID = GA_UF.GENA_GEN_EMP_ID_PROPRIETARIO_D
           AND UF.GEN_ID = GA_UF.GENA_GEN_ID_PROPRIETARIO_DE
           AND ROWNUM = 1) AS CIDADE,
       (SELECT MAX(SUBSTR(UF.GEN_DESCRICAO, 1, 2)) CIDADE_UF
          FROM CLIENTE_E CE, GENER CIDADE, GENER_A GA_UF, GENER UF
         WHERE CE.CLIE_CLI_EMP_ID = EMP_COD
           AND CE.CLIE_CLI_ID = CLI_COD
           AND CE.CLIE_GEN_TGEN_ID_CIDADE_DE = CIDADE.GEN_TGEN_ID
           AND CE.CLIE_GEN_EMP_ID = CIDADE.GEN_EMP_ID
           AND CE.CLIE_GEN_ID_CIDADE_DE = CIDADE.GEN_ID
           AND GA_UF.GENA_GEN_TGEN_ID = CIDADE.GEN_TGEN_ID
           AND GA_UF.GENA_GEN_EMP_ID = CIDADE.GEN_EMP_ID
           AND GA_UF.GENA_GEN_ID = CIDADE.GEN_ID
           AND UF.GEN_TGEN_ID = GA_UF.GENA_GEN_TGEN_ID_PROPRIETARIO_
           AND UF.GEN_EMP_ID = GA_UF.GENA_GEN_EMP_ID_PROPRIETARIO_D
           AND UF.GEN_ID = GA_UF.GENA_GEN_ID_PROPRIETARIO_DE
           AND ROWNUM = 1) AS UF,
       
       (SELECT MAX(GEOP.GEN_DESCRICAO)
          FROM CLIENTE_E CE, GENER GEOP
         WHERE CE.CLIE_CLI_EMP_ID = EMP_COD
           AND CE.CLIE_CLI_ID = CLI_COD
           AND CE.CLIE_GEN_TGEN_ID_GEOPOLITICO_D = GEOP.GEN_TGEN_ID
           AND CE.CLIE_GEN_EMP_ID = GEOP.GEN_EMP_ID
           AND CE.CLIE_GEN_ID_GEOPOLITICO_DE = GEOP.GEN_ID
           AND ROWNUM = 1) AS BAIRRO,
           
           
           
           (SELECT MAX(CE.CLIE_ENDERECO)
          FROM CLIENTE_E CE
         WHERE CE.CLIE_CLI_EMP_ID = EMP_COD
           AND CE.CLIE_CLI_ID = CLI_COD
           AND ROWNUM = 1) AS ENDERECO,
           
           
       
       
       DUPLICATA,
       SUBSTR(DUPLICATA, INSTR(DUPLICATA, '/') + 1, 3) AS PARCELA,
       TRUNC(DTA_EMISS) AS DTA_EMISS,
       TRUNC(DTA_VCTO) AS DTA_VCTO,
       (max(VALOR_DUP) - sum(VALOR_PARC)) AS VALOR_ABERTO,
       MAX(VALOR_DUP) AS VALOR_DUP,
       --BANCO,
      -- NOME_BANCO,
       CLI_TELEF1,
       DUPL_OBS
       
  FROM (SELECT 'BOLETO' AS TITULO,
               C.CLI_CGC_CPF AS CNPJ_CPF,
               c.cli_gen_id_tp_pessoa_de AS TP_PESSOA,
               B.BCO_ID AS BANCO,
               B.BCO_DESC AS NOME_BANCO,
               A.AGEN_TELEF AS TELEFONE_BANCO,
               'A' AS TIPO,
               DUPL_EMP_ID AS EMP_COD,
               E.EMP_NOME AS EMP_NOME,
               CID.GEN_DESCRICAO AS FILIAL,
               DUPL_CLI_ID AS CLI_COD,
               C.CLI_RAZAO_SOCIAL AS CLI_RAZAO,
               C.CLI_FANTASIA AS CLI_FANTASIA,
               C.CLI_TELEF1 AS CLI_TELEF1,
               D.DUPL_BCO_ID AS CLI_BCO_ID,
               DM.DUPL_DTA_CAD AS DATA_CAD,
               DUPL_ID AS DUPLICATA,
               DECODE(DD.DUPL_NR_NF, NULL, DUPL_ID, DD.DUPL_NR_NF) AS NR_NF,
               ROUND(((NVL(DM.DUPL_VLR_DESC, 0) /
                     DECODE(D.DUPL_VALOR, NULL, 1, 0, 1)) * 100),
                     2) AS P_DESC,
               TRUNC(D.DUPL_DTA_EMIS) AS DTA_EMISS,
               TRUNC(D.DUPL_DTA_VCTO) AS DTA_VCTO,
               TRUNC(DM.DUPL_DT_MOVIM) AS DTA_MOV,
               TRUNC(D.DUPL_DTA_PGTO) AS DTA_PAG,
               NVL(D.DUPL_VALOR, 0) AS VALOR_DUP,
               D.DUPL_DT_LIB_LIQUI AS DUPL_DT_LIB_LIQUI,
               NVL(ROUND(NVL(P.PEDF_VLR_DESC_BOLETO, 0) /
                         PARCELAS.NR_PARCELAS,
                         2),
                   0) AS VLR_DESC_BOLETO,
               NVL(D.DUPL_VALOR, 0) -
               NVL(ROUND(NVL(D.DUPL_VLR_DESC, 0) / PARCELAS.NR_PARCELAS, 2),
                   0) AS VLR_SALDO_DUPLICATA,
               NVL(P.PEDF_VLR_TOT_PED, 0) AS VL_MERC,
               NVL(DECODE(DM.DUPL_ENTR_SAI, 'S', DM.DUPL_VLR_PGTO, 0), 0) -
               NVL(DM.DUPL_VLR_DESC, 0) + NVL(DM.DUPL_VLR_JURO, 0) AS VALOR_PARC,
               ROTA.GEN_ID AS ROTA_ID,
               ROTA.GEN_TGEN_ID AS ROTA_TGEN,
               ROTA.GEN_EMP_ID AS ROTA_EMP,
               ROTA.GEN_DESCRICAO AS ROTA_DESC,
               SETOR.GEN_TGEN_ID AS SETOR_TGEN,
               SETOR.GEN_EMP_ID AS SETOR_EMP,
               SETOR.GEN_ID AS SETOR_ID,
               SETOR.GEN_DESCRICAO AS SETOR_DESC,
               NVL(DM.DUPL_VLR_JURO, 0) AS JUROS,
               NVL(DM.DUPL_VLR_DESC, 0) AS DESCONTO,
               DM.DUPL_ENTR_SAI AS E_S,
               DM.DUPL_GER_PARC AS SITUACAO,
               D.DUPL_OBS AS OBSERV,
               (SELECT SUM(DMS.DUPL_VLR_PGTO)
                  FROM DUPLICATA_M DMS
                 WHERE DMS.DUPL_DUPL_EMP_ID = D.DUPL_EMP_ID
                   AND DMS.DUPL_DUPL_CLI_ID = D.DUPL_CLI_ID
                   AND DMS.DUPL_DUPL_ID = D.DUPL_ID
                   AND TRUNC(DMS.DUPL_DT_MOVIM) <= TRUNC(DM.DUPL_DT_MOVIM)
                   AND DMS.DUPL_DTA_CAD < DM.DUPL_DTA_CAD
                   AND DMS.DUPL_ENTR_SAI = 'S') AS SALDO_ACUM,
               C.CLI_EMP_ID,
               P.PEDF_SITUACAO,
               DUPL_DTA_PREVISAO,
               DUPL_NR_BLOQUETO,
               RPAD(D.DUPL_OBS,80) DUPL_OBS
          FROM DUPLICATA D,
               BANCO B,
               AGENCIA A,
               DUPLICATA_M DM,
               DUPLICATA_D DD,
               CLIENTE C,
               (SELECT COUNT(CO.CVTO_ID) AS NR_PARCELAS,
                       CO.CVTO_EMP_ID,
                       CO.CVTO_ID
                  FROM COND_VCTO CO, COND_VCTO_P CP
                 WHERE CP.CVTO_CVTO_EMP_ID = CO.CVTO_EMP_ID
                   AND CP.CVTO_CVTO_ID = CO.CVTO_ID
                   AND CO.CVTO_EMP_ID IN (20)
                 GROUP BY CO.CVTO_EMP_ID, CO.CVTO_ID) PARCELAS,
               EMPRESA E,
               GENER CID,
               GENER ROTA,
               GENER_A ROTA_A,
               GENER SETOR,
               GENER_A SETOR_A,
               GENER DISTRITO,
               GENER_A DISTRITO_A,
               GENER AREA,
               PEDIDO_FAT P
         WHERE CID.GEN_EMP_ID = E.EMP_GEN_EMP_ID_CIDADE_DE
           AND CID.GEN_TGEN_ID = E.EMP_GEN_TGEN_ID_CIDADE_DE
           AND CID.GEN_ID = E.EMP_GEN_ID_CIDADE_DE
           AND E.EMP_ID = D.DUPL_EMP_ID
           AND C.CLI_EMP_ID = D.DUPL_CLI_EMP_ID
           AND C.CLI_ID = D.DUPL_CLI_ID
           AND DM.DUPL_DUPL_EMP_ID = D.DUPL_EMP_ID
           AND DM.DUPL_DUPL_CLI_ID = D.DUPL_CLI_ID
           AND DM.DUPL_DUPL_CLI_EMP_ID = D.DUPL_CLI_EMP_ID
           AND DM.DUPL_DUPL_ID = D.DUPL_ID
           AND DD.DUPL_DUPL_EMP_ID(+) = D.DUPL_EMP_ID
           AND DD.DUPL_DUPL_CLI_ID(+) = D.DUPL_CLI_ID
           AND DD.DUPL_DUPL_CLI_EMP_ID(+) = D.DUPL_CLI_EMP_ID
           AND DD.DUPL_DUPL_ID(+) = D.DUPL_ID
           AND DD.DUPL_PEDF_EMP_ID = P.PEDF_EMP_ID(+)
           AND DD.DUPL_PEDF_ID = P.PEDF_ID(+)
           AND PARCELAS.CVTO_ID(+) = P.PEDF_CVTO_ID
           AND PARCELAS.CVTO_EMP_ID(+) = P.PEDF_CVTO_EMP_ID
           AND D.DUPL_BCO_EMP_ID = B.BCO_EMP_ID
           AND D.DUPL_BCO_ID = B.BCO_ID
           AND B.BCO_AGEN_GEN_TGEN_ID = A.AGEN_GEN_TGEN_ID
           AND B.BCO_AGEN_GEN_EMP_ID = A.AGEN_GEN_EMP_ID
           AND B.BCO_AGEN_GEN_ID = A.AGEN_GEN_ID
           AND B.BCO_AGEN_ID = A.AGEN_ID
           AND ROTA.GEN_EMP_ID = D.DUPL_EMP_ID
           AND ROTA.GEN_TGEN_ID = NVL(NVL(NVL(D.DUPL_GEN_TGEN_ID_ROTA,
                                              P.PEDF_GEN_TGEN_ID_ROTA_DE),
                                          920),
                                      920)
           AND ROTA.GEN_ID =
               DECODE(P.PEDF_GEN_ID_ROTA_DE,
                      NULL,
                      (SELECT MIN(CLIV1.CLIV_GEN_ID)
                         FROM CLIENTE_V CLIV1
                        WHERE CLIV1.CLIV_CLI_ID = C.CLI_ID
                          AND CLIV1.CLIV_CLI_EMP_ID = C.CLI_EMP_ID),
                      P.PEDF_GEN_ID_ROTA_DE)
           AND ROTA_A.GENA_GEN_TGEN_ID(+) = ROTA.GEN_TGEN_ID
           AND ROTA_A.GENA_GEN_EMP_ID(+) = ROTA.GEN_EMP_ID
           AND ROTA_A.GENA_GEN_ID(+) = ROTA.GEN_ID
           AND SETOR.GEN_TGEN_ID(+) = ROTA_A.GENA_GEN_TGEN_ID_PROPRIETARIO_
           AND SETOR.GEN_EMP_ID(+) = ROTA_A.GENA_GEN_EMP_ID_PROPRIETARIO_D
           AND SETOR.GEN_ID(+) = ROTA_A.GENA_GEN_ID_PROPRIETARIO_DE
           AND SETOR_A.GENA_GEN_TGEN_ID(+) = SETOR.GEN_TGEN_ID
           AND SETOR_A.GENA_GEN_EMP_ID(+) = SETOR.GEN_EMP_ID
           AND SETOR_A.GENA_GEN_ID(+) = SETOR.GEN_ID
           AND DISTRITO.GEN_TGEN_ID(+) =
               SETOR_A.GENA_GEN_TGEN_ID_PROPRIETARIO_
           AND DISTRITO.GEN_EMP_ID(+) =
               SETOR_A.GENA_GEN_EMP_ID_PROPRIETARIO_D
           AND DISTRITO.GEN_ID(+) = SETOR_A.GENA_GEN_ID_PROPRIETARIO_DE
           AND DISTRITO_A.GENA_GEN_TGEN_ID(+) = DISTRITO.GEN_TGEN_ID
           AND DISTRITO_A.GENA_GEN_EMP_ID(+) = DISTRITO.GEN_EMP_ID
           AND DISTRITO_A.GENA_GEN_ID(+) = DISTRITO.GEN_ID
           AND AREA.GEN_TGEN_ID(+) =
               DISTRITO_A.GENA_GEN_TGEN_ID_PROPRIETARIO_
           AND AREA.GEN_EMP_ID(+) =
               DISTRITO_A.GENA_GEN_EMP_ID_PROPRIETARIO_D
           AND AREA.GEN_ID(+) = DISTRITO_A.GENA_GEN_ID_PROPRIETARIO_DE
           AND ((DM.DUPL_ENTR_SAI = 'S') OR
               ((DM.DUPL_ENTR_SAI = 'E') AND
               (D.DUPL_EMP_ID, D.DUPL_CLI_ID, D.DUPL_CLI_EMP_ID, D.DUPL_ID) NOT IN
               (SELECT DISTINCT DM.DUPL_DUPL_EMP_ID,
                                  DM.DUPL_DUPL_CLI_ID,
                                  DM.DUPL_DUPL_CLI_EMP_ID,
                                  DM.DUPL_DUPL_ID
                    FROM DUPLICATA_M DM
                   WHERE DM.DUPL_DUPL_EMP_ID IN (20)
                     AND DM.DUPL_ENTR_SAI = 'S')))
           AND D.DUPL_EMP_ID IN (20)
           AND TRUNC(D.DUPL_DTA_PGTO) IS NULL
           AND (P.PEDF_SITUACAO = 0 AND P.PEDF_ID_DEVOL IS NULL AND
               NOT EXISTS
                (SELECT FAT.PEDF_ID
                   FROM PEDIDO_FAT FAT
                  WHERE FAT.PEDF_EMP_ID = P.PEDF_EMP_ID
                    AND FAT.PEDF_ID_DEVOL = P.PEDF_ID
                    AND FAT.PEDF_SITUACAO = 0) OR (P.PEDF_ID IS NULL))
        UNION
        SELECT 'CHEQUE' AS TITULO,
               C.CLI_CGC_CPF AS CNPJ_CPF,
               c.cli_gen_id_tp_pessoa_de AS TP_PESSOA,
               B.BCO_ID AS BANCO,
               B.BCO_DESC AS NOME_BANCO,
               A.AGEN_TELEF AS TELEFONE_BANCO,
               'B',
               CQ.CHQP_EMP_ID,
               E.EMP_NOME,
               NULL,
               CQ.CHQP_CLI_ID,
               C.CLI_RAZAO_SOCIAL,
               C.CLI_FANTASIA,
               C.CLI_TELEF1,
               CQ.CHQP_BCO_ID,
               CQ.CHQP_DTA_CAD,
               CQ.CHQP_NR_CHEQ || '-CH',
               TO_CHAR(P.PEDF_NR_NF),
               NULL,
               TRUNC(CQ.CHQP_DTA_EMIS),
               TRUNC(CQ.CHQP_DTA_VCTO),
               TRUNC(CQ.CHQP_DTA_SIT),
               TRUNC(CQ.CHQP_DTA_BAIXA),
               NVL(CQ.CHQP_VALOR, 0),
               NULL,
               NVL(CQ.CHQP_VALOR, 0) VLR_SALDO_DUPLICATA,
               NVL(P.PEDF_VLR_TOT_PED, 0),
               CQ.CHQP_VLR_BAIXA,
               0 AS VALOR_PARC,
               ROTA.GEN_ID,
               ROTA.GEN_TGEN_ID,
               ROTA.GEN_EMP_ID,
               ROTA.GEN_DESCRICAO,
               SETOR.GEN_TGEN_ID,
               SETOR.GEN_EMP_ID,
               SETOR.GEN_ID,
               SETOR.GEN_DESCRICAO,
               NVL(CQ.CHQP_VLR_JURO, 0),
               NVL(CQ.CHQP_VLR_DESC, 0),
               NULL,
               ST.GEN_DESCRICAO,
               NULL,
               0,
               C.CLI_EMP_ID,
               0 PEDF_SITUACAO,
               NULL,
               NULL,
               NULL
          FROM CHEQUE_PRE CQ,
               CHEQUE_D   D,
               BANCO      B,
               AGENCIA    A,
               PEDIDO_FAT P,
               EMPRESA    E,
               CLIENTE    C,
               GENER      ST,
               GENER      ROTA,
               GENER_A    ROTA_A,
               GENER      SETOR,
               GENER_A    SETOR_A,
               GENER      DISTRITO,
               GENER_A    DISTRITO_A,
               GENER      AREA
         WHERE E.EMP_ID IN (20)
           AND CQ.CHQP_BCO_EMP_ID = B.BCO_EMP_ID
           AND CQ.CHQP_BCO_ID = B.BCO_ID
           AND CQ.CHQP_EMP_ID = E.EMP_ID
           AND CQ.CHQP_SITC_GEN_ID NOT IN (20) -- SITUAÇÃO CHEQUE
           AND CQ.CHQP_SITC_GEN_ID IN (4,5,7,8,12) -- situaçõs de inadimplencia
           AND CQ.CHQP_CLI_EMP_ID = C.CLI_EMP_ID
           AND CQ.CHQP_CLI_ID = C.CLI_ID
           AND D.CHQD_CHQP_EMP_ID(+) = CQ.CHQP_EMP_ID
           AND D.CHQD_CHQP_BCO_EMP_ID(+) = CQ.CHQP_BCO_EMP_ID
           AND D.CHQD_CHQP_BCO_ID(+) = CQ.CHQP_BCO_ID
           AND D.CHQD_CHQP_CLI_ID(+) = CQ.CHQP_CLI_ID
           AND D.CHQD_CHQP_CLI_EMP_ID(+) = CQ.CHQP_CLI_EMP_ID
           AND D.CHQD_CHQP_NR_CHEQ(+) = CQ.CHQP_NR_CHEQ
           AND D.CHQD_CHQP_SEQ(+) = CQ.CHQP_SEQ
           AND D.CHQD_PEDF_EMP_ID = P.PEDF_EMP_ID(+)
           AND D.CHQD_PEDF_ID = P.PEDF_ID(+)
           AND ST.GEN_TGEN_ID = CQ.CHQP_SITC_GEN_TGEN_ID
           AND ST.GEN_EMP_ID = CQ.CHQP_SITC_GEN_EMP_ID
           AND ST.GEN_ID = CQ.CHQP_SITC_GEN_ID
           AND ROTA.GEN_TGEN_ID = 920
           AND ROTA.GEN_ID =
               NVL(P.PEDF_GEN_ID_ROTA_DE,
                   (SELECT MIN(CLIV1.CLIV_GEN_ID)
                      FROM CLIENTE_V CLIV1
                     WHERE CLIV1.CLIV_CLI_ID = C.CLI_ID
                       AND CLIV1.CLIV_CLI_EMP_ID = C.CLI_EMP_ID))
           AND ROTA.GEN_EMP_ID = CQ.CHQP_EMP_ID
           AND ROTA_A.GENA_GEN_TGEN_ID = ROTA.GEN_TGEN_ID
           AND ROTA_A.GENA_GEN_EMP_ID = ROTA.GEN_EMP_ID
           AND ROTA_A.GENA_GEN_ID = ROTA.GEN_ID
           AND SETOR.GEN_TGEN_ID = ROTA_A.GENA_GEN_TGEN_ID_PROPRIETARIO_
           AND SETOR.GEN_EMP_ID = ROTA_A.GENA_GEN_EMP_ID_PROPRIETARIO_D
           AND SETOR.GEN_ID = ROTA_A.GENA_GEN_ID_PROPRIETARIO_DE
           AND SETOR_A.GENA_GEN_TGEN_ID = SETOR.GEN_TGEN_ID
           AND SETOR_A.GENA_GEN_EMP_ID = SETOR.GEN_EMP_ID
           AND SETOR_A.GENA_GEN_ID = SETOR.GEN_ID
           AND DISTRITO.GEN_TGEN_ID = SETOR_A.GENA_GEN_TGEN_ID_PROPRIETARIO_
           AND DISTRITO.GEN_EMP_ID = SETOR_A.GENA_GEN_EMP_ID_PROPRIETARIO_D
           AND DISTRITO.GEN_ID = SETOR_A.GENA_GEN_ID_PROPRIETARIO_DE
           AND DISTRITO_A.GENA_GEN_TGEN_ID = DISTRITO.GEN_TGEN_ID
           AND DISTRITO_A.GENA_GEN_EMP_ID = DISTRITO.GEN_EMP_ID
           AND DISTRITO_A.GENA_GEN_ID = DISTRITO.GEN_ID
           AND AREA.GEN_TGEN_ID = DISTRITO_A.GENA_GEN_TGEN_ID_PROPRIETARIO_
           AND AREA.GEN_EMP_ID = DISTRITO_A.GENA_GEN_EMP_ID_PROPRIETARIO_D
           AND AREA.GEN_ID = DISTRITO_A.GENA_GEN_ID_PROPRIETARIO_DE
           AND B.BCO_AGEN_GEN_TGEN_ID = A.AGEN_GEN_TGEN_ID
           AND B.BCO_AGEN_GEN_EMP_ID = A.AGEN_GEN_EMP_ID
           AND B.BCO_AGEN_GEN_ID = A.AGEN_GEN_ID
           AND B.BCO_AGEN_ID = A.AGEN_ID
           AND TRUNC(CQ.CHQP_DTA_BAIXA) IS NULL
           AND (P.PEDF_SITUACAO = 0 AND P.PEDF_ID_DEVOL IS NULL AND
               NOT EXISTS
                (SELECT FAT.PEDF_ID
                   FROM PEDIDO_FAT FAT
                  WHERE FAT.PEDF_EMP_ID = P.PEDF_EMP_ID
                    AND FAT.PEDF_ID_DEVOL = P.PEDF_ID
                    AND FAT.PEDF_SITUACAO = 0) OR (P.PEDF_ID IS NULL)))
 WHERE CLI_COD NOT IN (94781) -- dep nao identificado
 AND   CLI_COD NOT IN (23086, --CLIENTES NAO COBRAR

184332, 
76480,
107895,
180380,
180288,
178536,
153285,
178667,
62351,
24883,
23089,
178316,
56466,
176339,
23086,
157097,
184333,
184739,
41,
85275,
177575,
177576,
108671,
157096,
67319,
96416,
182819,
96411,
180062,
106025,
181869,
157838,
44021,
182764,
56467,
81533,
184417,
177497,
24954,
106156,
153052,
178666,
157907,
181836,
56472,
75176,
94427,
176925,
76479,
7668,
181837,
184952,
85729,
182432,
178358,
25096,
27675,
40,
90559,
182144,
88942,
14262,
156979,
178357,
178535,
24910,
11261,
29701,
7673,
182650,
184418,
183552,
56468,
180379,

24954,
81533,
90563,
153285,
106025,
27675,
23089,
29701,
14262,
25096,
22325,
88942,
157838,
62351,
71179,
40,
56468,
56472,
24883,
36214,
85729,
90559,
56466,
61286,
29011,
7673,
75176,
82478,
107895,
153052,
67319,
9395,
96411,
56467,
157096,
108671,
67317,
76480,
85275,
90560,
94427,
176339,
71180,
76479,
10336,
41,
11261,
7668,
44021,
96416,
157097,
108186,
157907,
106156,
40454,
29486,
7690,
83359,
75319,
62486,
64510)
 --AND SETOR_ID    IN (1,2,3,4,5,6,7,8,9,10) -- SETOR
AND SUBSTR(DUPLICATA,0,3) NOT IN ('REN')
 
 AND SETOR_ID IN (3, 4, 6, 7, 8, 10, 80 )
 AND DTA_VCTO >= TO_DATE('01/01/2010','DD/MM/RRRR') 


 AND DTA_VCTO <  TO_DATE((TO_CHAR('01')|| '/'||(TO_CHAR(sysdate, 'MM')-2)|| '/'|| TO_CHAR('2023')),'DD/MM/RRRR')
 

-- Não considerar os emitidos e vencimento na mesma data.
       AND TO_DATE(DTA_EMISS,'DD/MM/YYYY') <> TO_DATE(DTA_VCTO,'DD/MM/YYYY')
-- Não considerar os emitidos e vencimento na mesma data.
 
 GROUP BY TITULO,
          CLI_COD,
          TP_PESSOA,
          ROTA_ID,
          SETOR_ID,
          CLI_RAZAO,
          CLI_FANTASIA,
          CNPJ_CPF,
          EMP_COD,
          DUPLICATA,
          SUBSTR(DUPLICATA, INSTR(DUPLICATA, '/') + 1, 3),
          TRUNC(DTA_EMISS),
          TRUNC(DTA_VCTO),
       --   BANCO,
       --   NOME_BANCO,
          CLI_TELEF1,
          DUPL_OBS
          
 ORDER BY EMP_COD, DUPLICATA

        """)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "TITULO": row[0],
                "CLI_COD": row[1],
                "TP_PESSOA": row[2],
                "ROTA_VENDEDOR": row[3],
                "SUPERVISOR": row[4],
                "CLI_RAZAO": row[5],
                "CLI_FANTASIA": row[6],
                "CNPJ_CPF": row[7],
                "CIDADE_UF": row[8],
                "UF": row[9],
                "BAIRRO": row[10],
                "ENDERECO": row[11],
                "DUPLICATA": row[12],
                "PARCELA": row[13],
                "DTA_EMISS": row[14].strftime('%Y-%m-%d'),
                "DTA_VCTO": row[15].strftime('%Y-%m-%d'),
                "VALOR_ABERTO": float(row[16]),
                "VALOR_DUP": float(row[17]),
                "CLI_TELEF1": row[18],
                "DUPL_OBS": row[19]
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

# Exemplo de uso da função
# resultado_json = busca_inadimplencia()
# print(resultado_json)

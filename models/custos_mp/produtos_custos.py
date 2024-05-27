import cx_Oracle
import json
from conexao_ora import userOra, password, dsn

def busca_produtos_custos_mp():
    try:
        # Crie a conexão
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

        # Crie um cursor para executar a consulta
        cursor = conn.cursor()

        # Execute a consulta SQL para buscar a inadimplência
        cursor.execute("""
SELECT DISTINCT COD_PRODUTO CODIGO, MATERIA_PRIMA, GRUPO FROM (
select
COD_PRODUTO
,COD_PRODUTO||' - '||SUBGRUPO_DESCRICAO MATERIA_PRIMA

,GRUPO

from
VIEW_KARDEX_INDUSTRIA t where t.EMPRESA = 4
and t.COD_PRODUTO IN (

    2001
,  2002
,  2003
,  2004
,  2006
,  2008
,  2009
,  2011
,  2012
,  2013
,  2014
,  2015
,  2016
,  2017
,  2018
,  2020
,  2021
,  2022
,  2023
,  2024
,  2025
,  2026
,  2027
,  2028
,  2029
,  2031
,  2032
,  2033
,  2034
,  2035
,  2036
,  2042
,  2043
,  2045
,  2046
,  2047
,  2048
,  2049
,  2062
,  2063
,  2064
,  2065
,  2066
,  2067
,  2068
,  2069
,  2070
,  2071
,  2092
,  2093
,  2103
,  2104
,  2107
,  2108
,  2109
,  2110
,  2111
,  2112
,  2113
,  2114
,  2115
,  2116
,  2117
,  2118
,  2119
,  2120
,  2121
,  2122
,  2123
,  2124
,  2125
,  2126
,  2127
,  2128
,  2129
,  2130
,  2131
,  2132
,  2134
,  2135
,  2136
,  2137
,  2138
,  2140
,  2169
,  2170
,  2178
,  2180
,  2185
,  2186
,  2187
,  2189
,  2190
,  2191
,  2192
,  2193
,  2194
,  2195
,  2196
,  2197
,  2198
,  2199
,  2200
,  2221
,  2225
,  2226
,  2227
,  2234
,  2235
,  2236
,  2237
,  2249
,  2250
,  2274
,  2275
,  2280
,  2281
,  2282
,  2294
,  2341
,  2343
,  2346
,  2357
,  2358
,  2361
,  2362
,  2364
,  2367
,  2368
,  2369
,  2370
,  2371
,  2372
,  2373
,  2374
,  2375
,  2400
,  2401
,  2402
,  2403
,  2404
,  2405
,  2450
,  2451
,  2457
,  2461
,  2470
,  2471
,  2472
,  2473
,  3376
,  3395
,  10650
,  10651
,  10653
,  10654
,  10655
,  10656
,  10664
,  10665
,  10746
,  10749
,  10790
,  11923
,  11924
,  12064
,  12065
,  12066
,  12081
,  12096
,  12097
,  12747
,  12748
,  14966
,  16312
,  16313
,  16314
,  16315
,  16316
,  16317
,  16318
,  16319
,  16320
,  16321
,  16322
,  16323
,  16324
,  16325
,  16326
,  16328
,  16329
,  16340
,  16342
,  16343
,  16345
,  16572
,  16640
,  16664
,  16665
,  16755
,  16831
,  16832
,  16833
,  16882
,  16944
,  16976
,  16977
,  16978
,  17031
,  17082
,  17083
,  17084
,  17285
,  17482
,  17483
,  17583
,  17585
,  17586
,  17765
,  17788
,  17830
,  17831
,  17882
,  17904
,  17905
,  18007
,  18008
,  18025
,  18158
,  18173
,  18215
,  18248
,  18275
,  18379
,  18381
,  18382
,  18444
,  18448
,  18449
,  18893
,  18987
,  18988
,  18997
,  18998
,  19031
,  19111
,  19175
,  19243
,  19304
,  19305
,  19391
,  19480
,  19502
,  19558


)

AND TO_CHAR(T.DATA_MOV,'MM') = TO_CHAR(sysdate,'MM')
---AND T.DATA_MOV >= '01/02/2024'
---AND T.DATA_MOV <= '29/02/2024'
---AND T.GRUPO IN ('MATERIA PRIMA', 'EMBALAGEM')
)
        """)

        # Obtenha todos os resultados da consulta
        rows = cursor.fetchall()

        # Converta os resultados em uma lista de dicionários
        results = []
        for row in rows:
            result_dict = {
                "CODIGO": row[0],
                "MATERIA_PRIMA": row[1],
                "GRUPO": row[2]

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
# resultado_json = busca_custos_mp()
# print(resultado_json)

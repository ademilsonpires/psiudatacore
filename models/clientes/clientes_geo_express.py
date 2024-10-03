from conexao_ora import *
import math
#calcula distancia
from math import radians, sin, cos, sqrt, atan2
import json
#from models.clientes.cliente import buscarCliFatura25



def haversine(lon1, lat1, lon2, lat2):
    # Conversão de graus para radianos
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # Fórmula Haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Raio da Terra em quilômetros
    return c * r

def buscarClientePrincipal(conn, codigo_cliente):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
             SELECT 
                c.d_cod_cliente,
                c.d_fantasia,
                c.d_cidade,
                c.d_latitude,
                c.d_longitude
            FROM (select * from VIEW_BASE_CLIENTE_25 union all select * from VIEW_BASE_CLIENTE union all select * from VIEW_BASE_CLIENTE_21) c
            WHERE c.empresa||c.d_cod_cliente = :codigo_cliente""",
            codigo_cliente=codigo_cliente
        )
        cliente = cursor.fetchone()
        cursor.close()
        if cliente:
            return {
                "d_cod_cliente": cliente[0],
                "d_fantasia": cliente[1],
                "d_cidade": cliente[2],
                "d_latitude": float(cliente[3]),
                "d_longitude": float(cliente[4])
            }
        else:
            return None
    except cx_Oracle.DatabaseError as e:
        return {"Erro": f"Erro ao conectar ou executar consulta: {e}"}

#busca clientes com fatura
def buscarCliFatura25(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
SELECT 
    s.D_COD_CLIENTE,
    s.D_FANTASIA,
    s.D_CIDADE,
    s.D_LATITUDE,
    s.D_LONGITUDE,
    s.RECEITA,
    s.VOLUME
FROM
(SELECT 
    
    T.EMPRESA||T.d_cod_cliente d_cod_cliente,
    T.d_fantasia,
    T.d_cidade,
    T.d_latitude,
    T.d_longitude,
    VENDA.RECEITA,
    VENDA.VOLUME,
    T.empresa||'-'||T.d_cod_cliente CLIENTE_EMPRESA
FROM
    (SELECT * FROM VIEW_BASE_CLIENTE_25 WHERE VIEW_BASE_CLIENTE_25.D_SETOR <> 'AUTO SERVICO'  UNION ALL SELECT * FROM VIEW_BASE_CLIENTE_21 UNION ALL SELECT * FROM VIEW_BASE_CLIENTE WHERE VIEW_BASE_CLIENTE.D_SETOR <> 'AUTO SERVICO'  ) T,
    (
    SELECT
    D_EMPRESA,
    D_COD_CLIENTE,
    AVG(VOLUME) AS VOLUME,
    AVG(RECEITA) AS RECEITA
FROM (
    SELECT
        TT00.D_EMPRESA,
        TT00.D_COD_CLIENTE,
        TT00.D_NR_NOTA,
        SUM(TT00.M_QTDE_VENDA) AS VOLUME,
        SUM(TT00.M_VLR_VENDA) AS RECEITA
    FROM
        VIEW_VDA_DTA_FORMATADA TT00
    WHERE
        TT00.D_EMPRESA IN (25, 20, 21)
        AND TT00.D_DATA >= TRUNC(ADD_MONTHS(SYSDATE, -6))
        AND TT00.M_QTDE_VENDA IS NOT NULL
        AND TT00.D_COD_PROD <> 153
    GROUP BY
        TT00.D_EMPRESA,
        TT00.D_COD_CLIENTE,
        TT00.D_NR_NOTA
) SUBQUERY
 
GROUP BY
    D_EMPRESA,
    D_COD_CLIENTE
HAVING
    AVG(VOLUME) > 100

    
) VENDA,
    (SELECT CLI.CLI_ID,
            CLI.CLI_EMP_ID,
            CLI.cli_gen_id_tp_docum_de AS FORMA_PGTO,
            CLI.CLI_GEN_ID_TP_FATURA_DE AS COND_PGTO
     FROM CLIENTE CLI
     WHERE CLI.CLI_EMP_ID IN (25, 20, 21)
       AND CLI.CLI_GEN_ID_TP_FATURA_DE = 2
       AND CLI.cli_gen_id_tp_docum_de = 3) B



WHERE T.empresa = B.CLI_EMP_ID
  AND T.d_cod_cliente = B.CLI_ID
  --
  AND T.empresa = VENDA.D_EMPRESA
  AND T.d_cod_cliente = VENDA.D_COD_CLIENTE

  AND t.empresa||'-'||t.d_cod_cliente NOT IN(
              
              SELECT DISTINCT R.D_EMPRESA||'-'|| R.D_COD_CLIENTE   CLIENTE_EMPRESA
  FROM (SELECT TT.D_EMPRESA,
               TT.D_COD_CLIENTE,
               TT.D_FANTASIA
        
          FROM VIEW_VDA_DTA_FORMATADA TT
         WHERE TT.D_EMPRESA IN (20, 25, 21)
           AND TT.D_ANO IN ('2024', '2023')
           AND TT.D_COD_PROD <> 153
           AND TT.D_COD_CLIENTE not in ('104305', '66173')
           and TT.D_PROCEDENCIA in 'Faturamento'
        ---  
          and TT.D_NR_PEDIDO not in
                                     ('670183',
                                     '677673',
                                     '671333',
                                     '677616',
                                     '668163',
                                     '685907',
                                     '683024',
                                     '688855',
                                     '161055',
                                     --'693937',
                                     '162386',
                                     '694029',
                                     '694264',
                                     '714732',
                                     '714708',
                                     '714712',
                                     '673282',
                                     '721799',
                                     '690602',
                                     '665587',
                                     '652787',
                                     '660857',
                                     '656612',
                                     '714735',
                                     '714737',
                                     '714743',
                                     '714725',
                                     '714728',
                                     '714727',
                                     '714749',
                                     '714755',
                                     '714721',
                                     '714719',
                                     '714715',
                                     '687653',
                                     '714729',
                                     '714711',
                                     '673289',
                                     '656611',
                                     '714745',
                                     '714750',
                                     '714724',
                                     '714723',
                                     '714718',
                                     '665603',
                                     '687652',
                                     '665582',
                                     '652785',
                                     '652786',
                                     '714739',
                                     '714757',
                                     '714717',
                                     '665585',
                                     '714733',
                                     '694029',
                                     '658133',
                                     '660855',
                                     '665589',
                                     '656614',
                                     '652784',
                                     '714744',
                                     '694265',
                                     '660853',
                                     '657289',
                                     '665591',
                                     '656613',
                                     '714751',
                                     '665592',
                                     '660856',
                                     '714722',
                                     '706083',
                                     '665590',
                                     '652788',
                                     '714736',
                                     '714740',
                                     '714710',
                                     '721800',
                                     '660854',
                                     '656615',
                                     '744496'))R
          
              )) s where
              
             
   s.CLIENTE_EMPRESA NOT IN (
  
  SELECT
  TT2.D_EMPRESA||'-'||TT2.D_COD_CLIENTE
FROM
    VIEW_VDA_DTA_FORMATADA TT2
WHERE
    TT2.D_EMPRESA IN (25, 20, 21)
    AND TT2.D_DATA >= TRUNC(ADD_MONTHS(SYSDATE, -6)) 
    AND TT2.D_COD_PROD <> 153
   
GROUP BY
    TT2.D_EMPRESA,
    TT2.D_COD_CLIENTE
HAVING
    SUM(TT2.M_QTDE_VENDA) < 100)
            """
        )
        rows = cursor.fetchall()
        cursor.close()

        results = []
        for row in rows:
            d_latitude = row[3]
            d_longitude = row[4]
            if d_latitude is not None and d_longitude is not None:
                result_dict = {
                    "d_cod_cliente": row[0],
                    "d_fantasia": row[1],
                    "d_cidade": row[2],
                    "d_latitude": float(d_latitude),
                    "d_longitude": float(d_longitude),
                    "m_receita": float(row[5]),
                    "m_volume": float(row[6])
                }
                results.append(result_dict)

        return results

    except cx_Oracle.DatabaseError as e:
        return {"Erro": f"Erro ao conectar ou executar consulta: {e}"}



#caclcula distancia
def calcular_distancia(lat1, lon1, lat2, lon2):
    # Converte latitude e longitude de graus para radianos
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Calcula a diferença entre as latitudes e longitudes
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula de Haversine
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Raio da Terra em quilômetros (6371)
    distancia = 6371 * c
    return distancia


def buscarClientesProximosporID(conn, codigo_cliente):
    cliente_principal = buscarClientePrincipal(conn, codigo_cliente)
    if cliente_principal is None:
        return {"Erro": "Cliente não encontrado"}


    for cliente in cliente_principal:
        return cliente_principal



def obterMenorDistancia(distancias_json):
    distancias = json.loads(distancias_json)
    menor_distancia = min(distancia['distancia_km'] for distancia in distancias)
    return menor_distancia


def buscarClientesProximos(conn, codigo_cliente):
    cliente_principal = buscarClientePrincipal(conn, codigo_cliente)
    if cliente_principal is None:
        return {"Erro": "Cliente principal não encontrado"}

    # Obter distâncias do cliente principal para os centros de distribuição
    distancias_centros_json_principal = buscarDistanciasClientesProximosporID(conn, codigo_cliente)
    distancias_centros_principal = json.loads(distancias_centros_json_principal)

    # Identificar o centro de distribuição mais próximo do cliente principal
    centro_mais_proximo = min(distancias_centros_principal, key=lambda x: x['distancia_km'])

    clientes_boleto = buscarCliFatura25(conn)
    if isinstance(clientes_boleto, dict) and "Erro" in clientes_boleto:
        return clientes_boleto

    clientes_proximos = []
    for cliente in clientes_boleto:
        distancia_cliente_principal = calcular_distancia(
            cliente_principal['d_latitude'],
            cliente_principal['d_longitude'],
            cliente['d_latitude'],
            cliente['d_longitude']
        )

        # Obter distâncias do cliente próximo para os centros de distribuição
        distancias_centros_json_cliente = calcularDistanciasCentrosDistribuicao(cliente)
        distancias_centros_cliente = json.loads(distancias_centros_json_cliente)

        # Encontrar a distância do cliente próximo ao mesmo centro de distribuição
        distancia_cliente_centro_mais_proximo = next(
            (centro['distancia_km'] for centro in distancias_centros_cliente if
             centro['centro'] == centro_mais_proximo['centro']),
            float('inf')  # Se não encontrar, assume infinito
        )

        # Verificar a geoviabilidade
        if distancia_cliente_centro_mais_proximo > centro_mais_proximo['distancia_km']:
            geoviabilidade = "vermelho"
        else:
            geoviabilidade = "verde"

        if distancia_cliente_principal <= centro_mais_proximo['distancia_km']:
            cliente['m_distancia'] = distancia_cliente_principal
            cliente['raio'] = centro_mais_proximo['distancia_km']
            cliente['geoviabilidade'] = geoviabilidade
            cliente['distancia_centro_mais_proximo'] = distancia_cliente_centro_mais_proximo
            clientes_proximos.append(cliente)

    return clientes_proximos

# def buscarClientesProximos(conn, codigo_cliente):
#     cliente_principal = buscarClientePrincipal(conn, codigo_cliente)
#     if cliente_principal is None:
#         return {"Erro": "Cliente principal não encontrado"}
#
#     distancias_centros_json = buscarDistanciasClientesProximosporID(conn, codigo_cliente)
#     menor_distancia = obterMenorDistancia(distancias_centros_json)
#
#     clientes_boleto = buscarCliFatura25(conn)
#     if isinstance(clientes_boleto, dict) and "Erro" in clientes_boleto:
#         return clientes_boleto
#
#     clientes_proximos = []
#     for cliente in clientes_boleto:
#         distancia = calcular_distancia(
#             cliente_principal['d_latitude'],
#             cliente_principal['d_longitude'],
#             cliente['d_latitude'],
#             cliente['d_longitude']
#         )
#         if distancia <= menor_distancia:
#             cliente['m_distancia'] = distancia
#             cliente['raio'] = menor_distancia  # Adiciona o campo "raio" com o valor de menor_distancia
#             clientes_proximos.append(cliente)
#
#     return clientes_proximos
#

# def buscarClientesProximos(conn, codigo_cliente):
#     cliente_principal = buscarClientePrincipal(conn, codigo_cliente)
#     if cliente_principal is None:
#         return {"Erro": "Cliente principal não encontrado"}
#
#     distancias_centros_json = buscarDistanciasClientesProximosporID(conn, codigo_cliente)
#     menor_distancia = obterMenorDistancia(distancias_centros_json)
#
#     clientes_boleto = buscarCliFatura25(conn)
#     if isinstance(clientes_boleto, dict) and "Erro" in clientes_boleto:
#         return clientes_boleto
#
#     clientes_proximos = []
#     for cliente in clientes_boleto:
#         distancia = calcular_distancia(
#             cliente_principal['d_latitude'],
#             cliente_principal['d_longitude'],
#             cliente['d_latitude'],
#             cliente['d_longitude']
#         )
#         if distancia <= menor_distancia:
#             cliente['m_distancia'] = distancia
#             clientes_proximos.append(cliente)
#
#     return clientes_proximos

#
#



#exemplo

# # Código do cliente principal
# codigo_cliente_principal = 177671
#
# # Buscar clientes próximos
# clientes_proximos_json = buscarClientesProximosporID(conn, codigo_cliente_principal)
# print(clientes_proximos_json)


def calcularDistanciasCentrosDistribuicao(cliente):
    centros_distribuicao = [
        { 'lat': -2.669792948234241, 'lng': -44.28876912765947, 'name': "FABRICA MATRIZ", 'city': "SÃO LUIS" },
        { 'lat': -3.553391855465225, 'lng': -44.81956530820351, 'name': "CD SANTA INÊS", 'city': "SANTA INÊS" },
        { 'lat': -5.292037616822134, 'lng': -44.49188268714008, 'name': "CD PRESIDENTE DUTRA", 'city': "PRESIDENTE DUTRA" }
    ]

    distancias = []

    cliente_lat = cliente['d_latitude']
    cliente_lng = cliente['d_longitude']

    for centro in centros_distribuicao:
        distancia = haversine(cliente_lng, cliente_lat, centro['lng'], centro['lat'])
        distancias.append({
            'centro': centro['name'],
            'cidade': centro['city'],
            'distancia_km': distancia
        })

    return json.dumps(distancias, indent=4, ensure_ascii=False)

def buscarDistanciasClientesProximosporID(conn, codigo_cliente):
    cliente_principal = buscarClientePrincipal(conn, codigo_cliente)
    if cliente_principal is None:
        return {"Erro": "Cliente não encontrado"}

    cliente = cliente_principal
    distancias = calcularDistanciasCentrosDistribuicao(cliente)
    return distancias




# # Exemplo de uso
# codigo_cliente = 25177671  # ID do cliente
# distancias = buscarDistanciasClientesProximosporID(conn, codigo_cliente)
# print(distancias)

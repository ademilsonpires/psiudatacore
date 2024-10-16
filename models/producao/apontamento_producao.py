import cx_Oracle
import json
from typing import Dict
from pydantic import BaseModel
from models.producao.ordem_producao import calcular_gap_produto_ordem_id
from conexao_ora import userOra, password, dsn  # Importar as credenciais do banco de dados


class ApontamentoProducao(BaseModel):
    linha_producao: int
    ordem_producao: int
    sku_producao: int
    data_producao: str
    hora_producao: str
    qtde_produzida: int
    empresa_producao: int
    gap: int
    obs: str


class CheckMP(BaseModel):
    linha_producao: int
    ordem_producao: int
    cod_sku_producao: int
    empresa_producao: int
    cod_mat_prima: int
    status: str


class ApontamentoDB:

    def inserir_apontamento(self, apontamento: ApontamentoProducao) -> Dict:
        try:
            # Abre uma nova conexão para cada operação
            conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

            # Calcular o gap antes de inserir
            gap_result = calcular_gap_produto_ordem_id(
                id_produto=apontamento.sku_producao,
                id_linha=apontamento.linha_producao,
                quantidade_produzida=apontamento.qtde_produzida
            )

            gap_data = json.loads(gap_result)

            if "gap" in gap_data:
                apontamento.gap = gap_data["gap"]
            else:
                return {"status": "error", "message": "Erro ao calcular o gap: dado não encontrado"}

            cursor = conn.cursor()

            sql = '''
            INSERT INTO DATACORE_APONT_PRODUCAO (LINHA_PRODUCAO, ORDEM_PRODUCAO, SKU_PRODUCAO, DATA_PRODUCAO, HORA_PRODUCAO, QTDE_PRODUZIDA, EMPRESA_PRODUCAO, GAP, OBS)
            VALUES (:linha_producao, :ordem_producao, :sku_producao, TO_DATE(:data_producao, 'DD/MM/YYYY'), :hora_producao, :qtde_produzida, :empresa_producao, :gap, :obs)
            '''

            cursor.execute(sql, {
                'linha_producao': apontamento.linha_producao,
                'ordem_producao': apontamento.ordem_producao,
                'sku_producao': apontamento.sku_producao,
                'data_producao': apontamento.data_producao,
                'hora_producao': apontamento.hora_producao,
                'qtde_produzida': apontamento.qtde_produzida,
                'empresa_producao': apontamento.empresa_producao,
                'gap': apontamento.gap,
                'obs': apontamento.obs
            })

            conn.commit()
            cursor.close()
            conn.close()
            return {"status": "success", "message": "Dados inseridos com sucesso"}

        except cx_Oracle.DatabaseError as e:
            return {"status": "error", "message": str(e)}

    def listar_apontamentos(self, ordem_producao: int) -> Dict:
        try:
            # Abre uma nova conexão para cada operação
            conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

            cursor = conn.cursor()

            sql = '''
            SELECT LINHA_PRODUCAO, ORDEM_PRODUCAO, SKU_PRODUCAO, TO_CHAR(DATA_PRODUCAO, 'DD/MM/YYYY'), HORA_PRODUCAO, QTDE_PRODUZIDA, EMPRESA_PRODUCAO, GAP, OBS
            FROM DATACORE_APONT_PRODUCAO
            WHERE ORDEM_PRODUCAO = :ordem_producao
            '''

            cursor.execute(sql, {'ordem_producao': ordem_producao})
            rows = cursor.fetchall()

            apontamentos = []
            for row in rows:
                apontamento = {
                    "linha_producao": row[0],
                    "ordem_producao": row[1],
                    "sku_producao": row[2],
                    "data_producao": row[3],
                    "hora_producao": row[4],
                    "qtde_produzida": row[5],
                    "empresa_producao": row[6],
                    "gap": row[7],
                    "obs": row[8]
                }
                apontamentos.append(apontamento)

            cursor.close()
            conn.close()

            return {"status": "success", "data": apontamentos}

        except cx_Oracle.DatabaseError as e:
            return {"status": "error", "message": str(e)}


class CheckMPDB:

    def inserir_check_mp(self, check_mp: CheckMP) -> Dict:
        try:
            # Abre uma nova conexão para cada operação
            conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

            cursor = conn.cursor()
            sql = '''
            INSERT INTO DATACORE_APONT_CHECK_MP (LINHA_PRODUCAO, ORDEM_PRODUCAO, COD_SKU_PRODUCAO, EMPRESA_PRODUCAO, COD_MAT_PRIMA, STATUS)
            VALUES (:linha_producao, :ordem_producao, :cod_sku_producao, :empresa_producao, :cod_mat_prima, :status)
            '''
            cursor.execute(sql, {
                'linha_producao': check_mp.linha_producao,
                'ordem_producao': check_mp.ordem_producao,
                'cod_sku_producao': check_mp.cod_sku_producao,
                'empresa_producao': check_mp.empresa_producao,
                'cod_mat_prima': check_mp.cod_mat_prima,
                'status': check_mp.status
            })
            conn.commit()
            cursor.close()
            conn.close()
            return {"status": "success", "message": "Dados inseridos com sucesso"}

        except cx_Oracle.DatabaseError as e:
            return {"status": "error", "message": str(e)}

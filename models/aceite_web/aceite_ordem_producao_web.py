from pydantic import BaseModel
from typing import Dict
import cx_Oracle
from conexao_ora import userOra, password, dsn  # Importar as credenciais do banco de dados


# Modelo para os dados da tabela aceite_ordem_pro_web
class AceiteOrdemPro(BaseModel):
    ordem_w_emp_id: int
    ordem_w_ordem_id: int
    ordem_w_data_aceite: str  # A data pode ser passada como string, mas será convertida para o formato de TIMESTAMP
    ordem_w_user_id: int
    ordem_w_prod_id: int
    ordem_w_qtde: int


class AceiteOrdemProDB:

    def inserir_aceite_ordem_pro(self, aceite_ordem: AceiteOrdemPro) -> Dict:
        try:
            # Abre uma nova conexão para cada operação
            conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

            cursor = conn.cursor()

            # Atualizamos a query para usar SYSDATE para a data e hora
            sql = '''
            INSERT INTO aceite_ordem_pro_web (
                ordem_w_emp_id, ordem_w_ordem_id, ordem_w_data_aceite, 
                ordem_w_user_id, ordem_w_prod_id, ordem_w_qtde
            ) 
            VALUES (
                :ordem_w_emp_id, :ordem_w_ordem_id, SYSDATE, 
                :ordem_w_user_id, :ordem_w_prod_id, :ordem_w_qtde
            )
            '''

            # Removemos o campo ordem_w_data_aceite do dicionário de parâmetros
            cursor.execute(sql, {
                'ordem_w_emp_id': aceite_ordem.ordem_w_emp_id,
                'ordem_w_ordem_id': aceite_ordem.ordem_w_ordem_id,
                'ordem_w_user_id': aceite_ordem.ordem_w_user_id,
                'ordem_w_prod_id': aceite_ordem.ordem_w_prod_id,
                'ordem_w_qtde': aceite_ordem.ordem_w_qtde
            })

            conn.commit()
            cursor.close()
            conn.close()
            return {"status": "success", "message": "Dados inseridos com sucesso"}

        except cx_Oracle.DatabaseError as e:
            return {"status": "error", "message": str(e)}

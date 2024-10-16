import qrcode
import cx_Oracle
from io import BytesIO
from pydantic import BaseModel
from datetime import datetime
from conexao_ora import userOra, password, dsn

class QRTagAceite(BaseModel):
    tag_emp_id: int
    tag_ordem_id: int
    tag_ordem_num: int
    tag_user_id: int
    tag_obs: str
    tag_qtde: int


class QRTagAceiteDB:

    def gerar_qrcode(self, url: str) -> str:
        """
        Gera o QR code a partir de uma URL e retorna a imagem gerada como bytes.
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')

        # Salvar a imagem em um buffer e retornar a imagem como bytes
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Retornar os bytes da imagem
        qrcode_data = buffer.getvalue()
        return qrcode_data

    def inserir_tag_aceite(self, tag: QRTagAceite) -> dict:
        """
        Insere os dados da tag na tabela qrtag_aceite_web e gera o QR code.
        """
        try:
            # Abre uma nova conexão para cada operação
            conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)
            cursor = conn.cursor()

            # Montar o SQL de inserção com a cláusula RETURNING para pegar o tag_id gerado
            sql = '''
            INSERT INTO qrtag_aceite_web (
                tag_emp_id, tag_data, tag_qrtag, tag_ordem_id, tag_ordem_num, 
                tag_user_id, tag_situacao, tag_obs, tag_qtde
            ) VALUES (
                :tag_emp_id, SYSDATE, :tag_qrtag, :tag_ordem_id, :tag_ordem_num, 
                :tag_user_id, 'A', :tag_obs, :tag_qtde
            ) RETURNING tag_id INTO :tag_id
            '''

            # Criamos uma variável para armazenar o tag_id gerado
            tag_id = cursor.var(cx_Oracle.NUMBER)

            # Executar a query com os valores fornecidos
            cursor.execute(sql, {
                'tag_emp_id': tag.tag_emp_id,
                'tag_qrtag': '',  # Inicialmente vazio, pois vamos atualizar após gerar o link
                'tag_ordem_id': tag.tag_ordem_id,
                'tag_ordem_num': tag.tag_ordem_num,
                'tag_user_id': tag.tag_user_id,
                'tag_obs': tag.tag_obs,
                'tag_qtde': tag.tag_qtde,
                'tag_id': tag_id  # Variável que vai armazenar o tag_id gerado
            })

            # Obter o tag_id gerado e garantir que seja um número inteiro
            tag_id_value = int(tag_id.getvalue()[0])  # Converte o valor para inteiro

            # Agora, podemos gerar o link correto do QR code usando o tag_id
            url_qr_code = f"meusite.com.br/aceite_web?id_tag={tag_id_value}"
            qrcode_image = self.gerar_qrcode(url_qr_code)

            # Atualizar a tag_qrtag com o link gerado
            cursor.execute('UPDATE qrtag_aceite_web SET tag_qrtag = :tag_qrtag WHERE tag_id = :tag_id', {
                'tag_qrtag': url_qr_code,
                'tag_id': tag_id_value
            })

            # Commit das alterações
            conn.commit()
            cursor.close()
            conn.close()

            return {
                "status": "success",
                "message": "Dados inseridos com sucesso e QR code gerado.",
                "qr_code": url_qr_code  # Retorna o link gerado para o QR code
            }

        except cx_Oracle.DatabaseError as e:
            return {"status": "error", "message": str(e)}

    def atualizar_situacao(self, tag_id: int, nova_situacao: str) -> dict:
        """
        Atualiza o campo situação na tabela qrtag_aceite_web com base no tag_id.
        """
        try:
            # Abre uma nova conexão
            conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)
            cursor = conn.cursor()

            # Verificar se a nova_situacao tem apenas 1 caractere
            if len(nova_situacao) != 1:
                return {"status": "error", "message": "O campo situação deve conter 1 caractere."}

            # Montar o SQL de update
            sql = '''
            UPDATE qrtag_aceite_web
            SET tag_situacao = :nova_situacao
            WHERE tag_id = :tag_id
            '''

            # Executar o update
            cursor.execute(sql, {
                'nova_situacao': nova_situacao,
                'tag_id': tag_id
            })

            # Verificar se o update foi bem-sucedido
            if cursor.rowcount == 0:
                return {"status": "error", "message": "Nenhuma linha foi atualizada. Verifique o tag_id."}

            # Commit das alterações
            conn.commit()
            cursor.close()
            conn.close()

            return {"status": "success", "message": "Situação atualizada com sucesso"}

        except cx_Oracle.DatabaseError as e:
            return {"status": "error", "message": str(e)}

    def listar_tags(self, tag_id: int = None) -> dict:
        """
        Lista os dados das tags. Se o tag_id for passado, retorna o registro específico,
        caso contrário, retorna todos os registros.
        """
        try:
            # Abre uma nova conexão
            conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)
            cursor = conn.cursor()

            # SQL para buscar os dados
            if tag_id:
                sql = '''
                SELECT tag_id, tag_emp_id, tag_data, tag_qrtag, tag_ordem_id, tag_ordem_num, 
                       tag_user_id, tag_situacao, tag_obs, tag_qtde
                FROM qrtag_aceite_web
                WHERE tag_id = :tag_id
                '''
                cursor.execute(sql, {'tag_id': tag_id})
            else:
                sql = '''
                SELECT tag_id, tag_emp_id, tag_data, tag_qrtag, tag_ordem_id, tag_ordem_num, 
                       tag_user_id, tag_situacao, tag_obs, tag_qtde
                FROM qrtag_aceite_web
                '''
                cursor.execute(sql)

            # Fetch all results
            rows = cursor.fetchall()

            # Montar a lista de tags
            tags = []
            for row in rows:
                tag = {
                    "tag_id": row[0],
                    "tag_emp_id": row[1],
                    "tag_data": row[2],
                    "tag_qrtag": row[3],
                    "tag_ordem_id": row[4],
                    "tag_ordem_num": row[5],
                    "tag_user_id": row[6],
                    "tag_situacao": row[7],
                    "tag_obs": row[8],
                    "tag_qtde": row[9]
                }
                tags.append(tag)

            cursor.close()
            conn.close()

            return {"status": "success", "data": tags}

        except cx_Oracle.DatabaseError as e:
            return {"status": "error", "message": str(e)}
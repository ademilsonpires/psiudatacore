import cx_Oracle

def inserir_dados_oracle(dados):
    userOra = "saib2000"
    password = "s@!b20"
    dsn = "BDTESTE"

    try:
        conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)
        cursor = conn.cursor()

        # Inserir os dados na tabela Oracle
        for row in dados:
            cursor.execute("""
                INSERT INTO EXPORT_FORTES_SAIB_BI
                (DATA, CDEMPRESA, CDESTABELECIMENTO, NMESTABELECIMENTO, CDLOTACAO, NMLOTACAO, CDEVENTO, NMEVENTO, VLEVENTO, TPEVENTO, ORIGEM)
                VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11)""", row)

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Ocorreu um erro durante a inserção no Oracle:", e)

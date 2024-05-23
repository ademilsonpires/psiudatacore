import conexao_fb
import inserir_oracle
from  folhaFortes import export

# # Consulta SQL
# sql_query = """
# -- Sua consulta SQL completa aqui
# """

resultados = export

# Inserindo os resultados no Oracle
inserir_oracle.inserir_dados_oracle(resultados)

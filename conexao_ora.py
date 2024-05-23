import cx_Oracle

# Defina os detalhes da conexão
userOra = "saib2000"
password = "SAIB"
dsn = "BDTESTE"

# Estabeleça uma conexão
conn = cx_Oracle.connect(user=userOra, password=password, dsn=dsn)

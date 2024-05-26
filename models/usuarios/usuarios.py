import sqlite3

class Usuario:
    def __init__(self, id=None, nome_usuario=None, senha=None, token=None, status=None):
        self.id = id
        self.nome_usuario = nome_usuario
        self.senha = senha
        self.token = token
        self.status = status

class UsuarioDB:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nome_usuario TEXT NOT NULL,
                            senha TEXT NOT NULL,
                            token TEXT,
                            status TEXT
                          )''')
        self.conn.commit()

    def insert_usuario(self, usuario):
        self.c.execute('''INSERT INTO usuarios (nome_usuario, senha, token, status)
                           VALUES (?, ?, ?, ?)''', (usuario.nome_usuario, usuario.senha, usuario.token, usuario.status))
        self.conn.commit()
        return self.c.lastrowid

    # def get_usuario_by_id(self, usuario_id):
    #     self.c.execute('''SELECT * FROM usuarios WHERE id = ?''', (usuario_id,))
    #     return self.c.fetchone()
    def get_usuarios(self, usuario_id=None):
        if usuario_id:
            self.c.execute('''SELECT * FROM usuarios WHERE id = ?''', (usuario_id,))
        else:
            self.c.execute('''SELECT * FROM usuarios''')
        return self.c.fetchall() if not usuario_id else self.c.fetchone()

    def get_usuario_by_nome_usuario(self, nome_usuario):
        self.c.execute('''SELECT * FROM usuarios WHERE nome_usuario = ?''', (nome_usuario,))
        return self.c.fetchone()

    def update_usuario(self, usuario):
        self.c.execute('''UPDATE usuarios SET nome_usuario = ?, senha = ?, token = ?, status = ? 
                           WHERE id = ?''', (usuario.nome_usuario, usuario.senha, usuario.token, usuario.status, usuario.id))
        self.conn.commit()

    def update_usuario_campo(self, usuario_id, campo, valor):
        self.c.execute(f'''UPDATE usuarios SET {campo} = ? WHERE id = ?''', (valor,) + (usuario_id,))
        self.conn.commit()

    def delete_usuario(self, usuario_id):
        self.c.execute('''DELETE FROM usuarios WHERE id = ?''', (usuario_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def get_usuario_by_token(self, token):
        self.c.execute('''SELECT * FROM usuarios WHERE token = ?''', (token,))
        return self.c.fetchone()


    def verificar_status_por_token(self, token):
        self.c.execute('''SELECT status FROM usuarios WHERE token = ?''', (token,))
        resultado = self.c.fetchone()
        if resultado:
            status = resultado[0]
            return status == '1'
        return False
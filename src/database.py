import sqlite3

class Database:

    def __init__(self, nome_arquivo):
        self.conexao = sqlite3.connect(nome_arquivo)
        self.cursor = self.conexao.cursor()

    def inicializar_tabela(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id_linha INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente TEXT,
            tag_empresa TEXT,
            origem TEXT,
            timestamp TEXT,
            log_raw TEXT
        )
    """)
        self.conexao.commit()
        db = Database("cyber_security.db")
        db.inicializar_tabela()

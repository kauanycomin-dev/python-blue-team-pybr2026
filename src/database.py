import sqlite3  # Importa a biblioteca nativa do Python para interagir com o banco de dados SQLite

class Database:
    """
    Classe responsável pela gestão e persistência de dados no SQLite.
    """

    def __init__(self, nome_arquivo="cyber_security.db"):
        # Guarda apenas o nome/caminho do arquivo do banco na variável de instância.
        self.nome_arquivo = nome_arquivo

    def _get_connection(self):
        """
        Método privado (indicado pelo _ no início).
        Cria e retorna uma conexão temporária para uma única operação, evitando travamentos.
        WAL mode permite leitura e escrita simultâneas sem conflito.
        """
        conexao = sqlite3.connect(self.nome_arquivo)
        conexao.execute("PRAGMA journal_mode=WAL")
        return conexao

    def inicializar_tabela(self):
        """
        Garante a criação da tabela 'logs' e dos índices no banco de dados.
        """
        with self._get_connection() as conexao:
            cursor = conexao.cursor()

            # Cria a tabela
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id_logs INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_cliente TEXT NOT NULL,
                    tag_empresa TEXT,
                    origem TEXT,
                    timestamp TIMESTAMP NOT NULL,
                    log_raw TEXT NOT NULL
                )
            """)

            # Cria os índices para buscas rápidas
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON logs(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_id_cliente ON logs(id_cliente)")

    def salvar_log(self, pacote):
        """
        Valida os campos obrigatórios e insere o pacote como nova linha no banco.
        """
        # Verifica se os campos críticos existem e não estão vazios antes de inserir
        campos_obrigatorios = ["id_cliente", "log_raw", "timestamp"]
        for campo in campos_obrigatorios:
            if not pacote.get(campo):
                raise ValueError(f"Campo obrigatório ausente ou vazio: {campo}")

        with self._get_connection() as conexao:
            cursor = conexao.cursor()

            # Utiliza '?' como placeholders por segurança contra ataques de SQL Injection
            cursor.execute("""
                INSERT INTO logs (id_cliente, tag_empresa, origem, log_raw, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                pacote["id_cliente"],
                pacote["tag_empresa"],
                pacote["origem"],
                pacote["log_raw"],
                pacote["timestamp"]
            ))

    def buscar_logs(self, limite=100):
        """
        Retorna as últimas linhas de log armazenadas, ordenadas da mais recente para a mais antiga.
        """
        with self._get_connection() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?
            """, (limite,))

            # coleta todos os resultados da consulta e retorna como uma lista de tuplas. Cada tupla representa uma linha da tabela, ex:
            # (1, 'cli_ambev_01', 'Ambev', 'nginx_main', '2026-08-15T14:32:10', '192.168.1.105 - - ...')
            return cursor.fetchall()
            
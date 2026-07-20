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
        """
        return sqlite3.connect(self.nome_arquivo)

    def inicializar_tabela(self):
        """
        Garante a criação da tabela 'logs' no banco de dados, caso ela ainda não exista.
        """
        # O bloco 'with' garante o encerramento automático da conexão no final do processo
        with self._get_connection() as conexao:
            # O cursor é o objeto encarregado de executar instruções SQL no banco
            cursor = conexao.cursor()
            
            # Executa o comando SQL DDL para criar a tabela com os campos da arquitetura
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id_linha INTEGER PRIMARY KEY AUTOINCREMENT,  -- Identificador único autoincrementado
                    id_cliente TEXT,                             -- Identificador do cliente
                    tag_empresa TEXT,                            -- Rótulo da empresa
                    origem TEXT,                                 -- Origem do log (ex: nginx_main)
                    timestamp TEXT,                              -- Carimbo de data/hora da ingestão
                    log_raw TEXT                                 -- Linha de log bruta enviada pelo servidor
                )
            """)
            
            # Grava e confirma as alterações no arquivo do banco de dados
            conexao.commit()

    def salvar_log(self, pacote):
        """
        Recebe o dicionário 'pacote' enviado pelo leitor e insere como nova linha no banco.
        """
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
            
            # Efetiva a gravação do registro no banco de dados
            conexao.commit()
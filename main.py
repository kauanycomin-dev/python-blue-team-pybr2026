from src.reader import LogReader
from src.database import Database

db = Database("cyber_security.db")
db.inicializar_tabela()

log = LogReader("logs/mock_nginx.log", "id_cliente", "tag_empresa", "origem")
for pacote in log.monitorar():
    db.cursor.execute(
        "INSERT INTO logs (id_cliente, tag_empresa, origem, log_raw, timestamp) VALUES (?, ?, ?, ?, ?)",
        (pacote["id_cliente"], pacote["tag_empresa"], pacote["origem"], pacote["log_raw"], pacote["timestamp"])
    )
    db.conexao.commit()
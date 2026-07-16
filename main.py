from src.reader import LogReader
from src.database import Database

db = Database("cyber_security.db")
db.inicializar_tabela()

log = LogReader("logs/mock_nginx.log", "id_cliente")
for pacote in log.monitorar():
    db.cursor.execute(
        "INSERT INTO logs (id_cliente, log_raw, timestamp) VALUES (?, ?, ?)",
        (pacote["id_cliente"], pacote["log_raw"], pacote["timestamp"])
    )
    db.conexao.commit()
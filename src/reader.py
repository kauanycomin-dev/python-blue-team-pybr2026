import time 
from datetime import datetime

class LogReader:

    def __init__(self, caminho_arquivo, id_cliente):
        self.id_cliente = id_cliente 
        self.arquivo = open(caminho_arquivo, "r")
        self.arquivo.seek(0, 2)

    def monitorar(self):
        while True:
            linha = self.arquivo.readline()
            if linha:
                linha_limpa = linha.strip()
                if linha_limpa:
                    yield {
                        "id_cliente": self.id_cliente,
                        "log_raw": linha_limpa,
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                time.sleep(0.1)

                 

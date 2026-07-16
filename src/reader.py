import time 
from datetime import datetime

class LogReader:

    def __init__(self, caminho_arquivo, id_cliente):
        self.id_cliente = id_cliente 
        self.caminho_arquivo = caminho_arquivo

    def monitorar(self):
        with open(self.caminho_arquivo, "r") as arquivo:
            arquivo.seek(0, 2)
            while True:
                linha = arquivo.readline()
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

                 

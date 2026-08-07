import time
from datetime import datetime

class LogReader:
    """
    Classe responsável pelo monitoramento contínuo de arquivos de log em tempo real.
    """
    def __init__(self, caminho_arquivo: str, id_cliente: str, tag_empresa: str, origem: str):
        # Guarda o caminho local do arquivo de log (.log)
        self.caminho_arquivo = caminho_arquivo
        
        # Guarda os metadados associados ao servidor/cliente monitorado
        self.id_cliente = id_cliente
        self.tag_empresa = tag_empresa
        self.origem = origem

    def monitorar(self):
        """
        Lê o arquivo de forma contínua atuando como um GERADOR (utilizando yield).
        """
        # encoding="utf-8" e errors="ignore" evitam interrupções por caracteres inválidos ou maliciosos
        with open(self.caminho_arquivo, "r", encoding="utf-8", errors="ignore") as arquivo:
            
            # Move o ponteiro direto para o final do arquivo
            # Permite monitorar eventos novos sem reprocessar o histórico
            arquivo.seek(0, 2)
            
            # Loop infinito para monitoramento contínuo
            while True:
                linha = arquivo.readline()
                
                # Remove espaços e quebras de linha, verifica se há conteúdo
                if linha_limpa := linha.strip():
                    # O 'yield' pausa a função e envia um pacote por vez, economizando RAM
                    yield {
                        "id_cliente": self.id_cliente,
                        "log_raw": linha_limpa,
                        "tag_empresa": self.tag_empresa,
                        "origem": self.origem,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    time.sleep(0.1)

                 

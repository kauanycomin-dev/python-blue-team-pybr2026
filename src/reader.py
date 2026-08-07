import os # tudo que envolve o sistema de arquivos do computador passa pelo os
import time
from datetime import datetime

class LogReader:
    """
    Classe responsável pelo monitoramento contínuo de arquivos de log em tempo real.
    """
    def __init__(self, caminho_arquivo: str, id_cliente: str, tag_empresa: str, origem: str, intervalo: float = 0.1):
        # Guarda o caminho local do arquivo de log (.log)
        self.caminho_arquivo = caminho_arquivo
        
        # Guarda os metadados associados ao servidor/cliente monitorado
        self.id_cliente = id_cliente
        self.tag_empresa = tag_empresa
        self.origem = origem
        
        # Intervalo de espera entre verificações quando não há linha nova
        self.intervalo = intervalo
        
        # Contador de linhas processadas desde o início do monitoramento
        self.linhas_processadas = 0

    def monitorar(self):
        """
        Lê o arquivo de forma contínua atuando como um GERADOR (utilizando yield).
        """
        # Verifica se o arquivo existe antes de tentar abrir
        if not os.path.exists(self.caminho_arquivo):
            raise FileNotFoundError(f"Arquivo de log não encontrado: {self.caminho_arquivo}")

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
                    self.linhas_processadas += 1
                    # O 'yield' pausa a função e envia um pacote por vez, economizando RAM
                    yield {
                        "id_cliente": self.id_cliente,
                        "log_raw": linha_limpa,
                        "tag_empresa": self.tag_empresa,
                        "origem": self.origem,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # Se não houver linha nova, descansa para não sobrecarregar o processador
                    time.sleep(self.intervalo)
import time             # Biblioteca para controle de pausas e consumo de CPU (sleep)
from datetime import datetime  # Biblioteca para gerar data e hora exatas do sistema

class LogReader:
    """
    Classe responsável pelo monitoramento contínuo de arquivos de log em tempo real.
    """

    def __init__(self, caminho_arquivo, id_cliente, tag_empresa, origem):
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
            
            # Move o ponteiro direto para o final do arquivo (seek 0 a partir do fim - offset 2)
            # Permite monitorar eventos novos em tempo real sem reprocessar o histórico
            arquivo.seek(0, 2)
            
            # Loop infinito para monitoramento contínuo
            while True:
                # Tenta ler a linha seguinte do arquivo de log
                linha = arquivo.readline()
                
                if linha:
                    # Remove espaços desnecessários e quebras de linha (\n) do texto
                    linha_limpa = linha.strip()
                    
                    if linha_limpa:
                        # O 'yield' pausa a função e envia um pacote por vez, economizando RAM
                        yield {
                            "id_cliente": self.id_cliente,
                            "log_raw": linha_limpa,
                            "tag_empresa": self.tag_empresa,
                            "origem": self.origem,
                            "timestamp": datetime.now().isoformat()  # Timestamp no padrão ISO 8601
                        }
                else:
                    # Se não houver linha nova, descansa por 0.1s para não sobrecarregar o processador
                    time.sleep(0.1)

                 

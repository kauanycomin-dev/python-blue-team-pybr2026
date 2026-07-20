# Importação das classes desacopladas mantidas na pasta src/
from src.reader import LogReader
from src.database import Database

def main():
    """
    Função principal responsável por orquestrar a ingestão contínua de logs.
    """
    # 1. Instancia a base de dados e garante a presença da tabela 'logs'
    db = Database("cyber_security.db")
    db.inicializar_tabela()

    # 2. Instancia o leitor definindo o arquivo e os metadados do cliente
    log_reader = LogReader(
        caminho_arquivo="logs/mock_nginx.log", 
        id_cliente="cli_ambev_01", 
        tag_empresa="Ambev", 
        origem="nginx_main"
    )

    print("🚀 Motor de Ingestão de Logs iniciado. Pressione Ctrl+C para encerrar.\n")

    # Estrutura de prevenção e tratamento de exceções
    try:
        # O loop consome linha por linha enviada pelo gerador 'yield' do leitor
        for pacote in log_reader.monitorar():
            # Grava o registro recebido no banco de dados SQLite
            db.salvar_log(pacote)
            
            # Exibe o status da operação no console
            print(f"[LOG INGERIDO] [{pacote['timestamp']}] {pacote['log_raw'][:60]}...")

    except KeyboardInterrupt:
        # Trata o encerramento manual via 'Ctrl + C' de forma limpa
        print("\n🛑 Encerramento solicitado. Finalizando o pipeline de ingestão...")
        
    except Exception as e:
        # Trata falhas imprevisíveis durante o processamento do pipeline
        print(f"\n❌ Erro imprevisto no pipeline: {e}")
        
    finally:
        # Executa obrigatoriamente no encerramento da aplicação
        print("✅ Processo finalizado com segurança.")

# Garante a execução apenas quando o script for chamado diretamente
if __name__ == "__main__":
    main()
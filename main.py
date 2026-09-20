from urllib.parse import unquote

# Importação das classes desacopladas mantidas na pasta src/
from src.reader import LogReader
from src.database import Database
from src.analyzer import analisar_requisicao, extrair_ip
from src.notifier import DiscordNotifier


def main():
    """
    Função principal responsável por orquestrar a ingestão contínua de logs.
    """
    # 1. Instancia a base de dados e garante a presença da tabela 'logs'
    db = Database("cyber_security.db")
    db.inicializar_tabela()

    # instancia o despachante de alertas para o discord
    notifier = DiscordNotifier()

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
        for pacote in log_reader.monitorar():

            log_raw = pacote.get("log_raw", "")

            # decodifica o log bruto para análise
            log_decodificado = unquote(log_raw)

            # analisa o log decodificado e retorna um objeto ResultadoAnalise
            resultado = analisar_requisicao(log_decodificado)

            # grava o registro recebido no banco de dados SQLite
            db.salvar_log(pacote)

            if resultado.eh_ameaca():
                print(
                    f"🚨 [AMEAÇA DETECTADA] [{resultado.severidade.value}] "
                    f"Tipo: {resultado.tipo_ataque} | Trecho: {resultado.trecho_suspeito}"
                )

                ip_atacante = extrair_ip(log_raw)

                notifier.enviar_alerta(
                    resultado,
                    ip_origem=ip_atacante,
                )
            else:
                print(
                    f"[LOG INGERIDO] [{pacote['timestamp']}] {log_raw[:60]}...")

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
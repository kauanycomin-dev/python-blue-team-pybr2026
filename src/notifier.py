from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
import urllib.error
import urllib.request

#importa os tipos do seu script de análise
#(caso estejam no arquivo analyzer.py, mantenha assim; se estiverem juntos, ignore o import)
from src.analyzer import ResultadoAnalise, Severidade

logger = logging.getLogger("detector_ameacas.notifier")

DISCORD_WEBHOOK_URL = (
    "https://discord.com/api/webhooks/1544334453919457282/"
    "jSgDwQUV5z4Id5D3T5I2Rf4bDMB9H4YqFZMERFQ5JvFwNKQbfS9jyNH7GtMKf6-rxhoO"
)

#essas sao as cores diretamente para o alerta de Severidade
CORES_SEVERIDADE: dict[Severidade, int] = {
    Severidade.CRITICA: 15158332,  #vermelho
    Severidade.ALTA: 15105570,     #laranja
    Severidade.MEDIA: 16776960,    #amarelo
    Severidade.BAIXA: 3447003,     #azul
}


class DiscordNotifier:
    """essa class é o modulo responsavel por converter o ResultadoAnalise em um alerta, estruturado e despachar via Webhook para o Discord (100% nativo)."""

    def __init__(self, webhook_url: str = DISCORD_WEBHOOK_URL):
        self.webhook_url = webhook_url

    def formatar_embed(self, resultado: ResultadoAnalise, ip_origem: str = "N/A") -> dict:
        """Monta o payload do Discord Embed usando os atributos tipados de ResultadoAnalise."""
        severidade_enum = resultado.severidade or Severidade.BAIXA
        cor = CORES_SEVERIDADE.get(severidade_enum, 3447003)
        trecho_sanitizado = str(resultado.trecho_suspeito or "N/A")[:250]

        embed = {
            "title": f"[ALERTA DE SEGURANÇA] {resultado.tipo_ataque or 'Ameaça Desconhecida'}",
            "description": resultado.descricao or "Atividade suspeita detectada no log.",
            "color": cor,
            "fields": [
                {
                    "name": "IP de Origem",
                    "value": f"`{ip_origem}`",
                    "inline": True,
                },
                {
                    "name": "Severidade",
                    "value": f"**{severidade_enum.value}**",
                    "inline": True,
                },
                {
                    "name": "Evidência Detectada (Payload)",
                    "value": f"```{trecho_sanitizado}```",
                    "inline": False,
                },
            ],
            "footer": {
                "text": "Sistema de Monitoramento Web • Python SOC"
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return {
            "username": "SOC Bot • Intrusion Alert",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2092/2092663.png",
            "embeds": [embed],
        }

    def enviar_alerta(self, resultado: ResultadoAnalise, ip_origem: str = "Desconhecido") -> bool:
        """essa class despacha a notificao via urllib (nativo) sem travar a esteira principal"""
        if not resultado.eh_ameaca():
            return False

        payload = self.formatar_embed(resultado, ip_origem)
        dados_json = json.dumps(payload).encode("utf-8")

        requisicao = urllib.request.Request(
            self.webhook_url,
            data=dados_json,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Python-Security-Monitor/1.0",
            },
            method="POST",
        )

        try:
            #timeout estrito de 3 segundos para resiliencia do pipeline
            with urllib.request.urlopen(requisicao, timeout=3.0) as resposta:
                if resposta.status in (200, 204):
                    logger.info("Alerta de %s enviado com sucesso ao Discord.", resultado.tipo_ataque)
                    return True
                logger.warning("Discord retornou status inesperado: HTTP %s", resposta.status)
                return False

        except urllib.error.HTTPError as erro:
            logger.error("Erro HTTP ao enviar webhook (%s): %s", erro.code, erro.read().decode("utf-8", errors="ignore"))
            return False
        except urllib.error.URLError as erro:
            logger.error("Falha de conexão com a API do Discord: %s", erro.reason)
            return False
        except Exception as erro:
            logger.error("Exceção inesperada ao despachar notificação: %s", erro)
            return False


#bloco de teste direto
if __name__ == "__main__":
    from analyzer import analisar_requisicao
#simula atq
    log_teste = "GET /login.php?user=' OR 1=1 -- HTTP/1.1"
    resultado_teste = analisar_requisicao(log_teste)

    notifier = DiscordNotifier()
    notifier.enviar_alerta(resultado_teste, ip_origem="192.168.1.50")
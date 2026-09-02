from __future__ import annotations

import argparse
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


#configuracao de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("detector_ameacas")


#modelos de dados
class Severidade(str, Enum):
    """essa class é o nivel da severidade da ameaça detectada."""
    BAIXA = "BAIXA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    CRITICA = "CRITICA"


@dataclass
class RegraAmeaca:
    """essa class representa uma assinatura de ataque conhecida."""
    nome: str
    padrao: re.Pattern
    severidade: Severidade
    descricao: str


@dataclass
class ResultadoAnalise:
    """essa clas é o resultado estruturado da analise de uma requisiçao"""
    status: str
    payload_analisado: str
    tipo_ataque: Optional[str] = None
    severidade: Optional[Severidade] = None
    descricao: Optional[str] = None
    trecho_suspeito: Optional[str] = None

    def eh_ameaca(self) -> bool:
        return self.status == "AMEACA_DETECTADA"


#base de assinaturas de ataque
_REGRAS_BRUTAS = [
    (
        "SQL_Injection",
        r"(\b(OR|AND)\b\s+[\w'\"]+\s*=\s*[\w'\"]+|--|\bUNION\b\s+\bSELECT\b|\bDROP\b\s+\bTABLE\b|;\s*--|\bSLEEP\s*\()",
        Severidade.CRITICA,
        "Tentativa de manipular consultas SQL (ex: bypass de login, exfiltração de dados).",
    ),
    (
        "XSS",
        r"(<script\b|%3Cscript\b|javascript:|on(error|load|click|mouseover)\s*=|<iframe\b|document\.cookie)",
        Severidade.ALTA,
        "Tentativa de injetar script malicioso executado no navegador da vítima.",
    ),
    (
        "Path_Traversal",
        r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e/|%2e%2e\\|\.\.%2f|\.\.%5c)",
        Severidade.ALTA,
        "Tentativa de acessar arquivos fora do diretório permitido (ex: /etc/passwd).",
    ),
    (
        "Command_Injection",
        r"(;\s*(ls|cat|whoami|id|rm|wget|curl)\b|\|\s*(ls|cat|whoami|id)\b|`.*`|\$\(.*\))",
        Severidade.CRITICA,
        "Tentativa de executar comandos arbitrários no sistema operacional.",
    ),
    (
        "LDAP_Injection",
        r"(\*\)|\(\|\(|\(\&\(|admin\)\(\|)",
        Severidade.MEDIA,
        "Tentativa de manipular filtros de consultas LDAP (ex: bypass de autenticação).",
    ),
    (
        "SSTI",
        r"(\{\{.*\}\}|\{%.*%\}|\$\{.*\})",
        Severidade.ALTA,
        "Tentativa de injeção em motor de templates (Server-Side Template Injection).",
    ),
    (
        "NoSQL_Injection",
        r"(\$where\b|\$ne\b|\$gt\b|\$regex\b)",
        Severidade.MEDIA,
        "Tentativa de manipular operadores de consulta em bancos NoSQL (ex: MongoDB).",
    ),
]

#compilamos as regras uma única vez, fora da funcaoo de analise.
REGRAS_AMEACAS: list[RegraAmeaca] = [
    RegraAmeaca(nome=nome, padrao=re.compile(padrao, re.IGNORECASE), severidade=sev, descricao=desc)
    for nome, padrao, sev, desc in _REGRAS_BRUTAS
]


#nucleo da análise
def analisar_requisicao(payload: str) -> ResultadoAnalise:
    """analisa uma requis e retorna um objeto resultado com status e detalhes da ameaca, se houver"""
    if not payload or not payload.strip():
        return ResultadoAnalise(status="LEGITIMO", payload_analisado=payload or "")

    for regra in REGRAS_AMEACAS:
        match = regra.padrao.search(payload)
        if match:
            logger.warning(
                "Ameaça detectada [%s | %s]: trecho '%s' em '%s'",
                regra.nome, regra.severidade.value, match.group(0), payload,
            )
            return ResultadoAnalise(
                status="AMEACA_DETECTADA",
                payload_analisado=payload,
                tipo_ataque=regra.nome,
                severidade=regra.severidade,
                descricao=regra.descricao,
                trecho_suspeito=match.group(0),
            )

    logger.info("Requisição legítima: '%s'", payload)
    return ResultadoAnalise(status="LEGITIMO", payload_analisado=payload)


def analisar_lote(payloads: list[str]) -> list[ResultadoAnalise]:
    """analisa uma lista de requisições de uma vez e retorna os resultados."""
    return [analisar_requisicao(p) for p in payloads]


#interface de linha de comando
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detector de ameaças em requisições web (baseado em assinaturas)."
    )
    parser.add_argument(
        "requisicao",
        nargs="?",
        help="String de requisição a ser analisada. Se omitida, roda os testes padrão.",
    )
    args = parser.parse_args()

    if args.requisicao:
        resultado = analisar_requisicao(args.requisicao)
        _imprimir_resultado(args.requisicao, resultado)
        return
#bloco de testes rápidos
    testes = [
        "GET /login.php?user=' OR 1=1 -- HTTP/1.1",
        "GET /index.html HTTP/1.1",
        "GET /search?q=<script>alert(1)</script> HTTP/1.1",

        "GET /download?file=../../../../etc/passwd HTTP/1.1",
        "GET /ping?host=8.8.8.8;cat%20/etc/passwd HTTP/1.1",
        "GET /perfil?nome={{7*7}} HTTP/1.1",
        "GET /produtos?filtro[$where]=this.preco<0 HTTP/1.1",
    ]
    for req in testes:
        resultado = analisar_requisicao(req)
        _imprimir_resultado(req, resultado)


def _imprimir_resultado(requisicao: str, resultado: ResultadoAnalise) -> None:
    print(f"Requisição: {requisicao}")
    if resultado.eh_ameaca():
        print(f"  Status:     {resultado.status}")
        print(f"  Ataque:     {resultado.tipo_ataque}")
        print(f"  Severidade: {resultado.severidade.value}")
        print(f"  Descrição:  {resultado.descricao}")
        print(f"  Trecho:     {resultado.trecho_suspeito!r}")
    else:
        print(f"  Status:     {resultado.status}")
    print()


if __name__ == "__main__":
    main()
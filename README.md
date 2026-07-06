# python-blue-team-pybr2026
Palestra Python Brasil 2026 — Análise de logs e resposta a incidentes

# Python para Blue Team: Análise de Logs e Resposta a Incidentes

Projeto desenvolvido para a **Python Brasil 2026** (Florianópolis, 14–19 de outubro),
sob orientação do professor Tiago Silva no Instituto Infnet.

## Sobre o projeto

Servidores geram milhões de linhas de log por dia. Analisá-las manualmente
é inviável. Este script monitora arquivos de log em tempo real, detecta
padrões de ataque como tentativas repetidas de autenticação e envia alertas
automáticos via webhook — usando apenas bibliotecas nativas do Python.

## Como funciona

O projeto é dividido em três módulos sequenciais:

- `reader.py` — lê o arquivo de log linha a linha sem sobrecarregar a memória
- `analyzer.py` — detecta padrões suspeitos com expressões regulares e extrai o IP do atacante
- `notifier.py` — envia o alerta em tempo real via webhook para o Discord ou Telegram

O `main.py` coordena os três módulos na ordem correta.

## Bibliotecas utilizadas

Apenas bibliotecas nativas do Python. Nenhuma dependência externa.

| Biblioteca | Uso |
|---|---|
| `with open` | Leitura eficiente de arquivos |
| `re` | Detecção de padrões com expressões regulares |
| `urllib.request` | Envio de alertas via webhook |

## Como rodar

```bash
python main.py
```

Nenhuma instalação adicional necessária. Funciona em qualquer ambiente com Python 3.

## Estrutura do projeto

python-blue-team-pybr2026/
├── main.py
├── logs/
│   └── teste.log
└── src/
├── reader.py
├── analyzer.py
└── notifier.py

## Autores

- **Wiliam Maia** — idealizador do projeto, arquitetura técnica e desenvolvimento
- **Kauany Comin** — coautora, estruturação da proposta e desenvolvimento
- **Orientador: Prof. Tiago Silva** — Instituto Infnet, Engenharia de Software

## Contexto

Palestra aprovada para a Python Brasil 2026. Nível: iniciante.
Todo o código usa apenas Python nativo e pode ser replicado
por qualquer pessoa com conhecimento básico de loops e arquivos.

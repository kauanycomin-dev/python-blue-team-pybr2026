# 🛡️ Python para Blue Team: Análise de Logs e Notificação de Incidentes

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com)
[![License](https://img.shields.io/badge/License-Educational-green?style=for-the-badge)](#-licença)

> 🎤 **Projeto desenvolvido para a Python Brasil 2026** (Florianópolis)  
> 🎓 **Orientação:** Prof. Tiago Silva | *Instituto Infnet*

---

## 📋 Sumário
- [Sobre o Projeto](#-sobre-o-projeto)
- [Arquitetura](#-arquitetura)
- [Detalhamento dos Módulos](#-detalhamento-dos-módulos)
- [Por que usar apenas a biblioteca padrão?](#-por-que-usar-apenas-a-biblioteca-padrão)
- [Demonstração](#-demonstração)
- [Limitações Atuais](#-limitações-atuais)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Executar](#-como-executar)
- [Autores](#-autores)

---

## 📌 Sobre o Projeto

O projeto parte de um problema muito comum em administração de sistemas: **servidores produzem uma quantidade enorme de logs, e analisar esses eventos manualmente não escala.**

> [!QUESTION]
> **A pergunta central:**  
> *Dá para automatizar a análise de logs e a notificação de incidentes usando apenas o que o Python já oferece de fábrica, sem nenhuma dependência externa?*

A resposta foi a construção de um **pipeline modular** que acompanha um arquivo de log continuamente, analisa novos eventos em tempo real, registra os resultados em banco de dados e notifica ameaças diretamente no Discord.

> [!NOTE]
> **Foco Didático:** Este projeto foi desenvolvido com finalidade demonstrativa. Ele não substitui uma solução de SIEM comercial, mas ensina como conceitos fundamentais de *Blue Team* podem ser implementados do zero.

---

## 🏗️ Arquitetura

O sistema é sustentado por dois pilares principais:


```

┌─────────────────────────────────────────────────────────┐
│              1. INFRAESTRUTURA E INGESTÃO               │
│   • reader.py    ─► Captura e lê logs continuamente     │
│   • database.py  ─► Armazena eventos e históricos       │
└────────────────────────────┬────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────┐
│               2. INTELIGÊNCIA E RESPOSTA                │
│   • analyzer.py  ─► Aplica regras RegEx e severidade    │
│   • notifier.py  ─► Despacha alertas para o Discord     │
└─────────────────────────────────────────────────────────┘

```

### 🔄 Fluxo Completo dos Dados

```text
 📄 ARQUIVO DE LOG
        │
        ▼
 ┌─────────────┐
 │  reader.py  │ ──► Ingestão contínua
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ analyzer.py │ ──► Detecção via RegEx
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ database.py │ ──► Persistência (SQLite)
 └──────┬──────┘
        │
        ▼
 ┌─────────────┐
 │ notifier.py │ ──► Resposta ao incidente
 └──────┬──────┘
        │
        ▼
 💬 DISCORD

```

---

## 🔍 Detalhamento dos Módulos

### 📥 `reader.py` — Ingestão Contínua

Transforma arquivos de log em um fluxo em tempo real de forma eficiente.

* **📍 Começando pelo presente:** Utiliza `arquivo.seek(0, 2)` para mover o ponteiro direto para o final do arquivo, ignorando históricos antigos e focando apenas em novos eventos.
* **⚡ Processamento com Generators (`yield`):** Entrega uma linha por vez, evitando estourar a memória RAM com arquivos gigabytescos.
* **🔒 Validação de Caminho:** Restringe o acesso apenas aos diretórios autorizados pelo projeto.

---

### 🔍 `analyzer.py` — Detecção de Ameaças

Utiliza **Expressões Regulares (RegEx)** pré-compiladas para identificar assinaturas maliciosas e tratar strings codificadas via `unquote`.

#### 🛡️ Categorias de Ataques Monitorados

| Categoria | Descrição / Padrão Buscado |
| --- | --- |
| 💉 **SQL Injection** | Padrões de manipulação de consultas SQL |
| 🌐 **XSS** | Inserção de scripts e conteúdo executável |
| 📁 **Path Traversal** | Tentativas de navegação fora do diretório web |
| ⚙️ **Command Injection** | Padrões de execução de comandos do sistema |
| 🔑 **LDAP Injection** | Manipulação de consultas em serviços LDAP |
| 📝 **SSTI** | Server-Side Template Injection |
| 🍃 **NoSQL Injection** | Padrões de manipulação de consultas NoSQL |

#### 📊 Níveis de Severidade

`🟢 BAIXA`  |  `🟡 MÉDIA`  |  `🟠 ALTA`  |  `🔴 CRÍTICA`

---

### 💾 `database.py` — Persistência Local

Garante a resiliência dos dados através do **SQLite**.

```text
                     ┌─► 💾 Banco de Dados (SQLite)
                     │
⚡ Evento Detectado ─┤
                     │
                     └─► 💬 Notificação (Discord)

```

* **🛡️ SQL Parametrizado:** Evita que o próprio analisador de SQL Injection fique vulnerável a falhas de injeção ao salvar o payload.
* **⚡ Modo WAL (`Write-Ahead Logging`):** Configurado via `PRAGMA journal_mode=WAL;`, permitindo leituras e escritas concorrentes sem travar o pipeline.

---

### 🔔 `notifier.py` — Resposta a Incidentes

Envia alertas formatados para webhooks do Discord usando a biblioteca nativa `urllib.request`.

> [!WARNING]
> **Tratamento de Rate Limit (HTTP 429):**
> Caso o Discord limite a taxa de requisições, o erro é capturado para que o pipeline de monitoramento **não caia**. O evento continua salvo no banco de dados para consulta posterior.

---

## ⚡ Por que usar apenas a biblioteca padrão?

O projeto desafia a dependência de pacotes de terceiros, utilizando o poder nativo do Python:

| Módulo Nativo | Aplicação no Projeto |
| --- | --- |
| `open()` / `os` | Leitura, manipulação e validação de caminhos |
| `time` / `datetime` | Gerenciamento de tempo e controle de checagem |
| `re` | Expressões regulares para detecção de ameaças |
| `sqlite3` | Armazenamento relacional e seguro |
| `urllib.request` / `json` | Envio de requisições HTTP POST para webhooks |
| `dataclasses` / `enum` | Organização limpa de dados e severidades |

---

## 🎬 Demonstração

O ciclo de vida completo de um incidente:

1. **Entrada:** Nova linha é gravada no log de testes.
2. **Leitura:** `reader.py` captura a linha instantaneamente.
3. **Análise:** `analyzer.py` encontra um payload (ex: `UNION SELECT`).
4. **Persistência:** O incidente é registrado no banco SQLite.
5. **Notificação:** `notifier.py` envia o card formatado para o canal do Discord.

---

## ⚠️ Limitações Atuais

* **Detecção Baseada em Assinaturas:** Suscetível a *falsos positivos* e *falsos negativos* caso o ataque seja insólito/inédito.
* **Escala de Arquivo:** Projetado para monitoramento de arquivos locais em um único servidor.
* **Notificações em Lote:** O tratamento do erro `HTTP 429` evita quedas, mas ainda necessita da implementação de *Backoff Exponencial* para reenvio.

---

## 📂 Estrutura do Repositório

```text
python-blue-team-pybr2026/
├── 📄 main.py            # Orquestrador do pipeline
├── 📁 logs/
│   └── 📄 teste.log      # Arquivo de log alvo
├── 📁 src/
│   ├── 📄 reader.py     # Ingestão de logs
│   ├── 📄 analyzer.py   # Motor de detecção RegEx
│   ├── 📄 database.py   # Conexão SQLite
│   └── 📄 notifier.py   # Webhook Discord
├── 📄 .gitignore
└── 📄 README.md

```

---

## 🚀 Como Executar

### 🛠️ Pré-requisitos

* **Python 3.10+**
* Uma URL de **Webhook do Discord**

### 💻 Passo a Passo

1. **Clone o repositório:**
```bash
git clone [https://github.com/seu-usuario/python-blue-team-pybr2026.git](https://github.com/seu-usuario/python-blue-team-pybr2026.git)
cd python-blue-team-pybr2026

```


2. **Configure a variável de ambiente do Webhook:**
```bash
# Linux / macOS
export DISCORD_WEBHOOK_URL="[https://discord.com/api/webhooks/SEU_WEBHOOK_AQUI](https://discord.com/api/webhooks/SEU_WEBHOOK_AQUI)"

# Windows (PowerShell)
$env:DISCORD_WEBHOOK_URL="[https://discord.com/api/webhooks/SEU_WEBHOOK_AQUI](https://discord.com/api/webhooks/SEU_WEBHOOK_AQUI)"

```


3. **Inicie o monitoramento:**
```bash
python main.py

```



---

## 👥 Autores


<br>Wiliam Maia 
|Idealização, Arquitetura de Segurança, Analisador e Notificações| 
<br>Kauany Comin
|Estruturação, Infraestrutura de Dados, Ingestão e Persistência|

* **Orientador:** Prof. Tiago Silva (*Instituto Infnet — Engenharia de Software*)
* **Evento:** Python Brasil 2026 — Florianópolis/SC *(14 a 19 de outubro de 2026)*

---

## 📄 Licença

Este projeto é disponibilizado exclusivamente para fins **educacionais e de demonstração**.

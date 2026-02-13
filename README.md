# Banco Ágil - Sistema Multi-Agente


## Visão Geral

O **Banco Ágil** é um sistema bancário digital inteligente, construído sobre uma arquitetura **multiagente** com roteamento dinâmico, capaz de autenticar clientes, analisar crédito, realizar entrevistas para atualização de score e fornecer cotações de câmbio. O sistema utiliza **LLMs** (Large Language Models) integrados com ferramentas customizadas, proporcionando atendimento automatizado, seguro e eficiente.

## Tecnologias Utilizadas
<p align="center">
<img src="https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/LangChain-Framework-black?logo=chainlink&logoColor=white" />
<img src="https://img.shields.io/badge/LangGraph-Orchestration-purple" />
<img src="https://img.shields.io/badge/OpenAI-GPT--4o-green?logo=openai&logoColor=white" />
<img src="https://img.shields.io/badge/Streamlit-Interface-red?logo=streamlit&logoColor=white" />
<img src="https://img.shields.io/badge/Pandas-Data-blue?logo=pandas&logoColor=white" />
<img src="https://img.shields.io/badge/Tavily-API-orange" />
</p>

- **LangChain**: Framework para construção de agentes LLM e integração com ferramentas externas.
- **LangGraph**: Orquestração de fluxos multiagente, roteamento dinâmico e controle de estado conversacional.
- **OpenAI GPT-4o**: LLM principal para raciocínio, geração de respostas e decisões de roteamento.
- **Streamlit**: Interface web interativa para chat com o sistema.
- **Pandas**: Manipulação de dados e persistência em CSV.
- **Tavily API**: Consulta de cotações de moedas em tempo real.
- **Python-dotenv**: Gerenciamento de variáveis de ambiente e chaves de API.

---

## Arquitetura do Sistema Banco Ágil

```plaintext
┌──────────────────────────────────────────────────────────────────────────────┐
│                                 Usuário                                     │
│                         (Web/Terminal Interface)                            │
└───────────────┬──────────────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                             Interface Streamlit                             │
│                (Chat Web) / CLI (src/graph/graph.py)                        │
└───────────────┬──────────────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                             LangGraph (Orquestrador)                        │
│        - Gerencia o fluxo conversacional e o roteamento entre agentes        │
│        - Controla contexto, histórico e handoff                              │
└───────────────┬──────────────────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                             Supervisor (LLM)                                │
│        - Analisa intenção do usuário                                        │
│        - Decide qual agente especializado assume o atendimento               │
│        - Justifica decisões de roteamento                                   │
└─────┬─────────┬───────────────┬────────────────────┬────────────────────────┘
      │         │               │                    │
      ▼         ▼               ▼                    ▼
┌──────────┐ ┌───────────┐ ┌──────────────┐ ┌─────────────────┐
│ Triagem  │ │  Crédito  │ │  Entrevista  │ │     Câmbio      │
│  Agent   │ │   Agent   │ │   Agent      │ │     Agent       │
└────┬─────┘ └────┬──────┘ └─────┬────────┘ └────────┬────────┘
     │           │              │                   │
     │           │              │                   │
     │           │              │                   │
     ▼           ▼              ▼                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                              Ferramentas/Tools                              │
│   - Acesso a dados locais (clientes.csv, score_limite.csv, etc)              │
│   - Integração com APIs externas (OpenAI, Tavily)                            │
│   - Persistência de histórico de solicitações                                │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Fluxo Resumido

1. **Usuário** interage via Web (Streamlit) ou CLI.
2. **LangGraph** recebe a mensagem e mantém o contexto.
3. **Supervisor** (LLM) interpreta a intenção e faz o roteamento.
4. O agente especializado (Triagem, Crédito, Entrevista, Câmbio) assume o atendimento.
5. Agentes usam **ferramentas** para acessar dados locais (CSV) ou APIs externas (OpenAI, Tavily).
6. Se necessário, ocorre **handoff** automático e transparente entre agentes, mantendo o contexto.
7. Resposta é enviada ao usuário.

---

**Principais tecnologias e arquivos:**
- `streamlit_app.py`: Interface web.
- `src/graph/graph.py`: Orquestração CLI.
- `src/agents/`: Implementação dos agentes.
- `src/tools/`: Ferramentas de integração (dados, APIs).
- `data/*.csv`: Bases de dados locais.
- `.env`: Configurações e chaves de API.
- **APIs externas**: OpenAI (LLM), Tavily (câmbio).

---

## Arquitetura Multiagente & Handoff

### Estrutura Multiagente

O sistema é composto por múltiplos **agentes especializados**, cada um responsável por um domínio específico:

- **Agente de Triagem**: Autenticação e identificação da necessidade do cliente.
- **Agente de Crédito**: Consultas de limite, solicitações de aumento e análise de score.
- **Agente de Entrevista**: Coleta de dados financeiros para recalcular o score.
- **Agente de Câmbio**: Cotações e conversões de moedas.

### Supervisor Inteligente

Um **Supervisor** (LLM) analisa cada mensagem do usuário e decide, com base em regras e contexto, qual agente deve assumir o atendimento. O supervisor sempre fornece uma justificativa detalhada para cada decisão de roteamento.

### Handoff (Transferência entre Agentes)

O **handoff** é o mecanismo que permite a transferência fluida do atendimento entre agentes, sem que o usuário perceba rupturas. O handoff ocorre de duas formas:

- **Explícito**: O agente detecta, por meio de marcadores especiais (ex: `##HANDOFF_PARA_CREDITO##`), que o cliente deseja tratar um assunto de outro domínio. O sistema então transfere automaticamente o contexto e o histórico para o agente apropriado.
- **Supervisor**: Quando não há marcador explícito, o supervisor analisa a intenção do usuário e faz o roteamento adequado.

**Exemplo de handoff:**
- Usuário: "Quero saber meu limite."
- Triagem: "Perfeito! Vou conectar você ao especialista em crédito. Um momento, por favor.  
  ##HANDOFF_PARA_CREDITO##"
- O sistema transfere o atendimento para o agente de crédito, mantendo o contexto do cliente.

**Regras de handoff:**
- O contexto do cliente (CPF, nome, autenticação) é preservado entre agentes.
- O usuário nunca vê mensagens técnicas sobre transferência.

---

## ⚙️ Funcionalidades

### 1.🔐 Triagem e Autenticação
- Saudação inicial personalizada.
- Solicitação de CPF e data de nascimento (aceita variações de formato).
- Até 2 tentativas de autenticação (configurável).
- Encerramento automático após tentativas excedidas.
- Identificação da necessidade do cliente e roteamento para o agente adequado.

### 2.💳 Crédito
- Consulta de limite e score.
- Solicitação de aumento de limite (validação automática pelo score).
- Registro de todas as solicitações no histórico.
- Resposta clara sobre aprovação ou rejeição, com motivo detalhado.
- Encaminhamento para entrevista de crédito, se necessário.

### 3.📝 Entrevista de Crédito
- Coleta de informações financeiras (renda, emprego, despesas, dependentes, dívidas).
- Cálculo e atualização automática do score.
- Explicação detalhada do novo score e variação.
- Oferecimento de novo pedido de aumento de limite.

### 4.💱 Câmbio
- Consulta de cotações de moedas estrangeiras.
- Conversão de valores entre moedas.
- Apresentação de fontes confiáveis para cotação.
- Encerramento de atendimento de câmbio.

### 5.🎯Supervisor Inteligente
- Análise de mensagens do usuário.
- Roteamento automático para o agente mais adequado.
- Detecção de intenção de encerramento.
- Justificativa detalhada para cada decisão de roteamento.

---

## 📂 Estrutura do Projeto

```
DESAFIO_TECH_FOR_HUMANS/
│
├── 📁 config/                  # Configurações globais do sistema
│
├── 📁 data/                    # Persistência em CSV
│   ├── clientes.csv            # Base de clientes
│   ├── score_limite.csv        # Tabela de score x limite
│   └── solicitacoes_aumento_limite.csv  # Histórico de solicitações
│
├── 📁 src/
│   │
│   ├── 📁 agents/              # Agentes especializados
│   │   ├── triagem.py          # Autenticação e roteamento inicial
│   │   ├── credito.py          # Consulta e aumento de limite
│   │   ├── entrevista.py       # Reavaliação de score
│   │   └── cambio.py           # Conversão de moedas
│   │
│   ├── 📁 graph/               # Orquestração LangGraph
│   │   └── graph.py            # Construção do fluxo multiagente
│   │
│   ├── 📁 prompts/             # Prompts estruturados (separação de contexto)
│   │   ├── triagem.md
│   │   ├── credito.md
│   │   ├── entrevista.md
│   │   ├── cambio.md
│   │   └── supervisor.md
│   │
│   ├── 📁 tools/               # Ferramentas auxiliares
│   │   ├── triagem.py
│   │   ├── credito.py
│   │   ├── entrevista.py
│   │   └── tavily.py           # Integração com API externa
│   │
│   └── 📁 utils/               # Funções utilitárias
│
├── 📁 venv/                    # Ambiente virtual (não versionado)
│
├── .env                        # Variáveis de ambiente
├── .env.example                # Modelo de configuração
├── .gitignore                  # Arquivos ignorados pelo Git
├── requirements.txt            # Dependências do projeto
├── streamlit_app.py            # Interface Web (Streamlit)
└── README.md                   # Documentação principal

```

---

# Banco Ágil - Sistema Multi-Agente

---

## 🚀 Instalação e Execução

### 1. Clone o repositório

```sh
git clone https://github.com/FilipeRocha04/Desafio_Tech_for_humans.git
cd Desafio_Tech_for_humans
```

### 2. Crie um ambiente virtual (Python 3.11)

Recomendado para evitar conflitos de dependências:

- No Windows:
    ```sh
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
- No macOS/Linux:
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```

### 3. Instale as dependências

```sh
pip install -r requirements.txt
```



### 4. Configure as variáveis de ambiente

crie  o arquivo `.env` com suas chaves de API e parâmetros de configuração.
```sh

# Chaves de API
OPENAI_API_KEY=sua-chave-openai-aqui

TAVILY_API_KEY=sua-chave-tavily-aqui

# Configuração do LLM
PROVIDER=openai
MODEL_NAME=gpt-4o-mini
TEMPERATURE=0

# Configuração de Autenticação
MAX_AUTH_ATTEMPTS=2

# Configuração do Streamlit
STREAMLIT_PORT=8501
STREAMLIT_HOST=0.0.0.0


```
### 5. Execute a interface web

```sh
streamlit run streamlit_app.py
```

Acesse pelo navegador em [http://localhost:8501](http://localhost:8501).

### 6. (Opcional) Execute no terminal

```sh
python src/graph/graph.py
```


### 7. (Opcional) Execute no terminal

```sh
python src/graph/graph.py
```

---

## 8. Como Testar

Para iniciar o atendimento, é necessário realizar a autenticação do cliente.

Você pode utilizar os dados abaixo para teste:

### 🔐 Dados de Autenticação

- **CPF:** `55566677788`
- **Data de Nascimento:** `20/12/1980`

> 💡 Alternativamente, consulte o arquivo `data/clientes.csv` para visualizar outros clientes disponíveis para teste.

## Exemplos de Uso

### 📊 Consulta de Limite
 
** Cliente:**👨‍💼 "qual meu score atual?"
> **Sistema:**🏦"Seu score de crédito é 339. Como posso ajudá-lo mais hoje?"




> **Cliente:** 👨‍💼"Qual meu limite atual?"  
> **Sistema:** 🏦"Limite disponível: R$ 5.000,00. Score atual: 650. Deseja solicitar aumento?"

### Solicitação de Aumento

> **Cliente:** 👨‍💼"Quero aumentar para 10.000"  
> **Sistema:** 🏦"Solicitação aprovada! Novo limite: R$ 10.000,00."

### Entrevista de Crédito

> **Cliente:** 👨‍💼"Quero melhorar meu score"  
> **Sistema:** 🏦"Qual é a sua renda mensal aproximada?"  
> ... (perguntas sequenciais) ...  
> "Score atualizado: 800. Gostaria de tentar solicitar um aumento de limite com este novo score?"

### Cotação de Câmbio

> **Cliente:** 👨‍💼"Quanto tá o dólar?"  
> **Sistema:** 🏦"O dólar está cotado a R$ 5,45. Posso ajudar com mais alguma conversão?"



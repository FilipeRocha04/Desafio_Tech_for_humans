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
--
- **LangChain** : Framework para construção de agentes LLM e integração com ferramentas externas.
- **LangGraph** : Orquestração de fluxos multiagente, roteamento dinâmico e controle de estado conversacional.
- **OpenAI GPT-4o** : LLM principal para raciocínio, geração de respostas e decisões de roteamento.
- **Streamlit** : Interface web interativa para chat com o sistema.
- **Pandas** : Manipulação de dados e persistência em CSV.
- **Tavily API** : Consulta de cotações de moedas em tempo real.
- **Python-dotenv** : Gerenciamento de variáveis de ambiente e chaves de API.

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

## Funcionalidades

### 1. Triagem e Autenticação
- Saudação inicial personalizada.
- Solicitação de CPF e data de nascimento (aceita variações de formato).
- Até 2 tentativas de autenticação (configurável).
- Encerramento automático após tentativas excedidas.
- Identificação da necessidade do cliente e roteamento para o agente adequado.

### 2. Crédito
- Consulta de limite e score.
- Solicitação de aumento de limite (validação automática pelo score).
- Registro de todas as solicitações no histórico.
- Resposta clara sobre aprovação ou rejeição, com motivo detalhado.
- Encaminhamento para entrevista de crédito, se necessário.

### 3. Entrevista de Crédito
- Coleta de informações financeiras (renda, emprego, despesas, dependentes, dívidas).
- Cálculo e atualização automática do score.
- Explicação detalhada do novo score e variação.
- Oferecimento de novo pedido de aumento de limite.

### 4. Câmbio
- Consulta de cotações de moedas estrangeiras.
- Conversão de valores entre moedas.
- Apresentação de fontes confiáveis para cotação.
- Encerramento de atendimento de câmbio.

### 5. Supervisor Inteligente
- Análise de mensagens do usuário.
- Roteamento automático para o agente mais adequado.
- Detecção de intenção de encerramento.
- Justificativa detalhada para cada decisão de roteamento.

---

## Estrutura do Projeto

```
├── .env
├── README.md
├── requirements.txt
├── streamlit_app.py
├── config/
├── data/
│   ├── clientes.csv
│   ├── score_limite.csv
│   └── solicitacoes_aumento_limite.csv
├── src/
│   ├── agents/
│   ├── graph/
│   ├── prompts/
│   ├── tools/
│   └── utils/
```

---

## Instalação e Execução

### 1. Clone o repositório

```sh
git clone https://github.com/FilipeRocha04/Desafio_Tech_for_humans.git
cd Desafio_Tech_for_humans
```

# Banco Ágil - Sistema Multi-Agente

---

## Instalação e Execução

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

Edite o arquivo `.env` com suas chaves de API e parâmetros de configuração.

### 5. Execute a interface web

```sh
streamlit run streamlit_app.py
```

Acesse pelo navegador em [http://localhost:8501](http://localhost:8501).

### 6. (Opcional) Execute no terminal

```sh
python src/graph/graph.py
```


### 5. (Opcional) Execute no terminal

```sh
python src/graph/graph.py
```

---

## Exemplos de Uso

### Consulta de Limite

> **Cliente:** "Qual meu limite atual?"  
> **Sistema:** "Limite disponível: R$ 5.000,00. Score atual: 650. Deseja solicitar aumento?"

### Solicitação de Aumento

> **Cliente:** "Quero aumentar para 10.000"  
> **Sistema:** "Solicitação aprovada! Novo limite: R$ 10.000,00."

### Entrevista de Crédito

> **Cliente:** "Quero melhorar meu score"  
> **Sistema:**  
> "Qual é a sua renda mensal aproximada?"  
> ... (perguntas sequenciais) ...  
> "Score atualizado: 800. Gostaria de tentar solicitar um aumento de limite com este novo score?"

### Cotação de Câmbio

> **Cliente:** "Quanto tá o dólar?"  
> **Sistema:** "O dólar está cotado a R$ 5,45. Posso ajudar com mais alguma conversão?"



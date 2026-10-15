# Pipeline de Engenharia de Requisitos com Agentes de IA

Esta é uma pipeline em Python que transforma um contexto de negócio em um pacote rastreável de artefatos de requisitos e arquitetura. Ela usa agentes de IA para elicitar necessidades, escrever e classificar requisitos, corrigir problemas encontrados, gerar ADRs e documentar uma arquitetura inicial.

O contexto de exemplo atual é o de um sistema de impressão 3D personalizada. Para aplicar a outro projeto, edite a constante `CONTEXTO` em `main.py` antes de executar.

## O que é utilizado

- [Python](https://www.python.org/) 3.10 ou superior (recomendado: Python 3.11 ou 3.12);
- [CrewAI](https://www.crewai.com/) para orquestrar agentes, tarefas e a execução sequencial;
- `python-dotenv` para carregar chaves de API do arquivo `.env`;
- OpenAI (`gpt-4o-mini`) e Google Gemini (`gemini/gemini-3.6-flash`) como modelos configurados no código.

Para executar a configuração atual, são necessárias uma chave da OpenAI e uma chave da API do Google/Gemini com acesso aos modelos configurados.

## Início rápido

Após clonar o repositório, execute os comandos abaixo no macOS ou Linux:

```bash
git clone https://github.com/alvsoaress/ai-requirements-engineering-pipeline.git
cd ai-requirements-engineering-pipeline
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Preencha as chaves no arquivo `.env` e inicie a pipeline:

```bash
python main.py
```

No Windows, use os comandos equivalentes de ativação e cópia apresentados nas seções seguintes.

## Instalação

No terminal, entre na pasta do projeto:

```bash
cd /caminho/para/pipeline-requisitos-agentes-ia
```

Crie um ambiente virtual:

```bash
python -m venv venv
```

Ative-o.

No macOS ou Linux:

```bash
source venv/bin/activate
```

No Windows (PowerShell):

```powershell
venv\Scripts\Activate.ps1
```

No Windows (Prompt de Comando):

```bat
venv\Scripts\activate.bat
```

Instale as dependências:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Bibliotecas e extensões para as APIs

Não é necessária nenhuma extensão de navegador ou do VS Code para chamar as APIs da OpenAI e do Gemini: a comunicação ocorre pelas bibliotecas Python e pelas chaves configuradas no `.env`.

- `crewai`: orquestra os agentes e encaminha as chamadas aos modelos configurados;
- `openai`: cliente usado pela integração com o modelo `gpt-4o-mini`;
- `google-genai`: cliente da API Gemini usada pelo modelo configurado com o prefixo `gemini/`;
- `python-dotenv`: lê `GOOGLE_API_KEY` e `CHATGPT_API_KEY` do arquivo `.env`.

Caso utilize o VS Code, a extensão opcional **Python**, da Microsoft, ajuda a selecionar o interpretador do ambiente `venv`, executar o arquivo e depurar. Ela melhora a experiência de desenvolvimento, mas não é requisito para a pipeline funcionar no terminal.

## Configuração das chaves de API

Na raiz do projeto, copie o arquivo de exemplo e informe as suas chaves:

```bash
cp .env.example .env
```

No Windows (Prompt de Comando), use:

```bat
copy .env.example .env
```

Depois, edite o `.env`:

```env
GOOGLE_API_KEY=sua_chave_da_google
CHATGPT_API_KEY=sua_chave_da_openai
```

Não publique esse arquivo nem suas chaves em repositórios, mensagens ou relatórios. A variável `MISTRALAI_API_KEY` pode existir no seu ambiente, mas não é usada pela versão atual da pipeline.
As chamadas aos modelos podem consumir créditos conforme o plano contratado em cada provedor.

## Como executar

Com o ambiente virtual ativado e o `.env` configurado, execute:

```bash
python main.py
```

A execução chama os modelos de IA e pode levar alguns minutos. O progresso e o caminho de cada arquivo salvo aparecem no terminal. Para interromper, use `Ctrl+C`.

Antes de rodar para outro sistema, substitua o conteúdo da constante `CONTEXTO` em `main.py` por uma descrição do domínio, stakeholders, objetivos, fluxos, regras e restrições conhecidas. Quanto mais concreto for o contexto, mais fundamentados serão os requisitos gerados.

## Fluxo da pipeline

1. Confirma o contexto, delimitando fatos, lacunas, stakeholders e assunções.
2. Elicita informações por entrevistas semiestruturadas simuladas.
3. Analisa os achados com a técnica dos Seis Chapéus.
4. Escreve requisitos funcionais e não funcionais atômicos e rastreáveis.
5. Classifica o catálogo em RF, RNF e requisitos arquiteturais (RA).
6. Faz uma verificação formal e uma única correção completa do catálogo.
7. Faz uma validação semântica e uma única correção completa do catálogo.
8. Usa o catálogo corrigido como catálogo final e gera ADRs e o documento de arquitetura.

As etapas de verificação e validação corrigem o catálogo; elas não usam juízes para rejeitar ou filtrar requisitos.

## Artefatos gerados

Cada execução cria uma pasta própria em `artefatos/<data-hora>/`. Nenhuma execução sobrescreve os resultados de outra. A pasta contém:

| Arquivo | Conteúdo |
| --- | --- |
| `01-contexto-confirmado.md` | Contexto, fronteira, fatos, lacunas e assunções. |
| `02-entrevistas.md` | Entrevistas e achados rastreáveis. |
| `03-seis-chapeus.md` | Análise pelos Seis Chapéus. |
| `04-requisitos-iniciais.md` | Primeira especificação de requisitos. |
| `05-classificacao-ra.md` | Catálogo classificado em RF, RNF e RA. |
| `06-verificacao-formal.md` | Diagnóstico da verificação formal. |
| `07-catalogo-pos-verificacao.md` | Catálogo após a correção formal. |
| `08-validacao-semantica.md` | Diagnóstico da validação semântica. |
| `09-catalogo-pos-validacao.md` | Catálogo após a correção semântica. |
| `10-catalogo-final.md` | Catálogo final corrigido. |
| `11-adrs.md` | Architecture Decision Records gerados a partir do catálogo final. |
| `12-arquitetura.md` | Documento de arquitetura rastreável aos requisitos e ADRs. |

O arquivo principal para consumo do time de produto é `10-catalogo-final.md`. Os demais arquivos preservam evidências e decisões tomadas ao longo do processo.

## Verificação rápida da instalação

Sem chamar APIs, é possível verificar se o arquivo principal possui sintaxe Python válida:

```bash
python -m py_compile main.py
```

Se houver testes locais disponíveis, execute:

```bash
python -m unittest -v test_main_prompts.py
```

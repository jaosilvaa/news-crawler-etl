# Teste Técnico - Pipeline de Coleta de Notícias

Este projeto implementa um pipeline de dados para coleta, processamento e armazenamento de notícias publicadas no site The Guardian.

O objetivo é automatizar a extração de artigos utilizando um crawler desenvolvido com Scrapy, realizar a limpeza do conteúdo textual das páginas e armazenar os dados estruturados no Google BigQuery. Como etapa adicional, o projeto disponibiliza uma API simples em FastAPI para consulta de artigos por palavra-chave.

## Arquitetura do Pipeline

O projeto segue um fluxo simples de dados. Primeiro o crawler coleta as notícias no site do The Guardian e salva o HTML bruto de cada página. Em seguida o pipeline processa esse conteúdo para extrair apenas o texto principal do artigo.

Depois da limpeza, os dados estruturados são enviados para o Google BigQuery. A API em FastAPI consulta essa tabela e permite buscar notícias por palavra-chave.

![Arquitetura do pipeline](docs/images/pipeline_diagram.png)

## Estrutura do Projeto

```text
news-crawler-etl/
├── api/
│   └── main.py                 # Rotas da API em FastAPI e consulta ao BigQuery
├── crawler/
│   ├── spiders/
│   │   └── guardian_spider.py  # Coleta de URLs e extração do HTML das notícias
│   ├── items.py                # Estrutura dos dados coletados
│   ├── pipelines.py            # Limpeza do conteúdo com Readability e BeautifulSoup, e envio para o BigQuery
│   └── settings.py             # Configurações do crawler no Scrapy
├── docs/
│   └── tradeoffs.md            # Decisões técnicas e arquitetura do projeto
├── config.yaml                 # Configurações do projeto no Google Cloud
├── postman_collection.json     # Requisições prontas para testar a API
└── requirements.txt            # Dependências do projeto
```
## Pré-requisitos

* Python 3.10 ou superior
* Gerenciador de pacotes pip
* Conta no Google Cloud Platform (GCP) com a API do BigQuery ativada
* Chave de serviço do Google Cloud em formato JSON, nomeada `gcp-credentials.json`

## Decisões Técnicas e Trade-offs

Todas as decisões de arquitetura, escolhas de bibliotecas (como o uso de Scrapy, Readability-lxml e FastAPI), estratégias de nuvem (BigQuery) e justificativas para o tratamento de dados inconsistentes estão detalhadas no documento específico:

[Ler Documentação de Trade-offs](docs/tradeoffs.md)

## Como usar este projeto

Passo a passo para rodar o projeto localmente.

### 1. Configuração Inicial

Prepare o ambiente Python e as credenciais da nuvem.

1.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
2.  Configure o acesso ao banco:
    * Insira o seu arquivo de chave do Google Cloud na raiz do projeto e renomeie para gcp-credentials.json.
    * Abra o arquivo config.yaml e ajuste as variáveis `project_id`, `dataset_id` e `table_id` conforme a sua estrutura no BigQuery.

### 2. Pipeline de Dados ETL (Crawler)

Execute o script principal para extrair as notícias, limpar o conteúdo HTML e realizar a carga no banco de dados.

1.  Pelo terminal, entre na pasta do crawler:
    ```bash
    cd crawler
    ```
2.  Inicie a raspagem:
    ```bash
    scrapy crawl guardian_spider
    ```
Isso varrerá a página inicial, extrairá os textos limpos e salvará os dados automaticamente na tabela do BigQuery.


### 3. Execução da API

Suba o servidor FastAPI para expor os dados armazenados e permitir consultas.


1.  Volte para a raiz do projeto e inicie o backend:
    ```bash
    uvicorn api.main:app --reload
    ```
2.  A API estará disponível em: `http://127.0.0.1:8000`
3.  Acesse a documentação interativa (Swagger) em: `http://127.0.0.1:8000/docs`

### 4. Testes Manuais

Para validar os endpoints isoladamente de forma rápida:

1.  Abra o **Postman**.
2.  Importe o arquivo `postman_collection.json` localizado na raiz do projeto.
3.  Utilize as requisições prontas na pasta "News Crawler API" para testar o status do servidor e a busca por palavra-chave.

## Prévia da Aplicação

### Swagger UI
Documentação interativa gerada automaticamente pelo FastAPI, detalhando as rotas de Health Check e Busca parametrizada.

![Swagger UI](docs/images/swagger.png)

### Consulta via Postman
Exemplo de requisição bem-sucedida consultando a base do BigQuery por palavra-chave e retornando o JSON estruturado da notícia.

![Consulta via Postman](docs/images/postman.png)

*(Screenshots demonstrativos da API REST desenvolvida e em funcionamento)*

## Autor

João Vitor Alcântara da Silva

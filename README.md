# Teste Técnico - Pipeline de Coleta de Notícias

Este projeto implementa um pipeline de dados para coleta, processamento e armazenamento de notícias publicadas no site The Guardian.

O objetivo é automatizar a extração de artigos utilizando um crawler desenvolvido com Scrapy, realizar a limpeza do conteúdo textual das páginas e armazenar os dados estruturados no Google BigQuery. Como etapa adicional, o projeto disponibiliza uma API simples em FastAPI para consulta de artigos por palavra-chave.

## Estrutura do Projeto

* **`crawler/`** Scripts responsáveis pelo web scraping no site The Guardian e processamento do HTML.
    * `spiders/guardian_spider.py`: Spider responsável por navegar no site, coletar URLs válidas e extrair o HTML bruto das notícias.
    * `pipelines.py`: Scripts de ETL (Extração, Transformação e Carga). Realizam a limpeza do texto (removendo menus/anúncios com Readability e BeautifulSoup) e a carga direta dos dados no BigQuery.
    * `items.py`: Definição da estrutura de dados extraída.
    * `settings.py`: Configurações de execução do Scrapy (pipelines, delays, user-agent).
* **`api/`** API REST desenvolvida com FastAPI para expor os dados armazenados na nuvem.
    * `main.py`: Definição das rotas de Health Check e Busca (`/search`), além da conexão parametrizada com o BigQuery.
* **`config.yaml`** Arquivo central de configurações com os dados do projeto, dataset e tabela do GCP.
* **`postman_collection.json`** Collection pronta com exemplos de requisições para facilitar o teste das rotas.
* **`tradeoffs.md`** Documentação das decisões técnicas e trade-offs adotados no projeto.

## Pré-requisitos

* Python 3.10 ou superior
* Gerenciador de pacotes `pip`
* Conta no Google Cloud Platform (GCP) com a API do BigQuery ativada
* Chave de serviço (Service Account) do GCP em formato JSON (`gcp-credentials.json`)

## Decisões Técnicas e Trade-offs

Todas as decisões de arquitetura, escolhas de bibliotecas (como o uso de Scrapy, Readability-lxml e FastAPI), estratégias de nuvem (BigQuery) e justificativas para o tratamento de dados inconsistentes estão detalhadas no documento específico:

[Ler Documentação de Trade-offs](tradeoffs.md)

## Como usar este projeto

Passo a passo para rodar o projeto localmente.

### 1. Configuração Inicial

Prepare o ambiente Python e as credenciais da nuvem.

1.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
2.  Configure o acesso ao banco:
    * Insira o seu arquivo de chave do Google Cloud na raiz do projeto e renomeie para `gcp-credentials.json`.
    * Abra o arquivo `config.yaml` e ajuste as variáveis `project_id`, `dataset_id` e `table_id` conforme a sua estrutura no BigQuery.

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

## Autor

João Vitor Alcântara da Silva
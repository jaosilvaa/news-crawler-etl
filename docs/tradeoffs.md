# Trade-offs e Decisões Técnicas

## 1.1 Escolha da Fonte de Dados

O enunciado sugeria utilizar a BBC ou o The Guardian como fonte para o crawler. Neste projeto, optei por trabalhar apenas com o The Guardian. A principal razão foi a estrutura semântica e bem organizada do site, que entrega o conteúdo diretamente no HTML e não depende de renderizações complexas em JavaScript.

Essa característica simplifica bastante o processo de extração, já que o crawler consegue acessar o conteúdo das páginas sem precisar executar scripts ou simular interações no navegador.

Outro ponto importante é que o corpo das notícias costuma ficar bem separado de anúncios, menus e outros elementos de navegação. Isso facilita a etapa de limpeza do conteúdo utilizando o framework Readability.

O site também disponibiliza metadados estruturados em formato JSON-LD, o que permite capturar informações como título e autor de forma direta. No conjunto, essas características tornam o crawler mais estável e reduzem a chance de quebra caso o layout visual do site sofra alterações.

---

## 1.2 Arquitetura do Crawler

O crawler foi implementado utilizando o framework Scrapy. A escolha se deve principalmente à forma como o framework gerencia requisições assíncronas e filas de coleta, permitindo executar múltiplas requisições de maneira eficiente sem a necessidade de implementar manualmente controle de concorrência.

A arquitetura do projeto segue a separação clássica de um pipeline ETL.

O spider atua exclusivamente na etapa de extração. Sua responsabilidade é localizar as URLs das notícias e armazenar o HTML bruto de cada página coletada.

Nenhuma etapa de limpeza ou transformação do conteúdo é realizada durante o crawl. O objetivo é preservar o HTML original da página para que o processamento seja feito posteriormente em uma etapa separada do pipeline.

Essa decisão permite reprocessar os dados caso as regras de limpeza ou extração mudem no futuro, sem a necessidade de executar um novo crawl no site.

---

## 2.1 Extração de Dados

A coleta de links começou utilizando alguns atributos HTML específicos presentes em elementos da página inicial. Na prática, essa abordagem reduziu a cobertura, já que o site utiliza diferentes estruturas para destacar notícias em seções como manchetes principais, listas laterais e conteúdos recomendados.

Para aumentar a cobertura, a estratégia adotada foi capturar todos os links presentes na página e aplicar uma filtragem baseada no padrão de URL utilizado nas páginas de notícia. Em geral, reportagens seguem um formato consistente de URL que inclui o ano de publicação, o que ajuda a diferenciar artigos de outros tipos de conteúdo do site.

Também foram adicionados filtros simples para ignorar páginas que não seguem o formato tradicional de notícia, como URLs que contêm `/live/`, `/audio/`, `/video/` ou `/gallery/`. Esses formatos costumam ter estrutura diferente ou conteúdo atualizado dinamicamente, o que poderia prejudicar a etapa de processamento do texto.

Por fim, foi aplicada uma deduplicação nas URLs coletadas. Isso evita requisições repetidas quando o mesmo artigo aparece em mais de um bloco da página inicial, como em seções de destaque ou recomendações.

## 2.2 Limpeza do Conteúdo

A etapa de limpeza ocorre no pipeline, operando sobre o HTML bruto previamente coletado pelo spider. Utilizei a biblioteca `readability-lxml` para identificar e isolar o bloco principal da notícia. Essa abordagem funciona bem porque o algoritmo descarta automaticamente elementos periféricos, como menus, rodapés e banners de publicidade, evitando a necessidade de manter seletores ou expressões regulares complexas.

Em seguida, o conteúdo isolado passa pelo `BeautifulSoup` apenas para remover as tags HTML remanescentes, resultando na extração direta do texto limpo.

---

## 2.3 Tratamento e Validação

A deduplicação inicial de URLs é feita ainda no spider utilizando a estrutura de dados `set` do Python. Isso evita que o crawler faça requisições repetidas quando o mesmo link aparece em diferentes blocos da página inicial.

No pipeline de limpeza também foram adicionadas regras de descarte (`DropItem`). Caso o HTML esteja vazio ou a extração não produza conteúdo textual válido, o item é descartado para evitar inserir registros incompletos no banco de dados. Também foi aplicada uma padronização simples no campo de autor, removendo espaços em branco extras.

---

## 3.1 Armazenamento dos Dados

Optei pelo Google BigQuery como destino para armazenar os dados estruturados. A integração ocorre em um pipeline dedicado, que abre a conexão ao iniciar o crawler e a encerra ao final do processo.

As configurações de projeto, dataset, tabela e o caminho das credenciais foram isoladas em um arquivo `config.yaml`. Essa separação evita expor variáveis de infraestrutura diretamente no código.

Como o volume de dados do projeto é pequeno, decidi não utilizar particionamento ou clustering na tabela. Isso mantém a estrutura simples e evita complexidade desnecessária para a escala atual.

---

## 3.2 Estrutura dos Dados

O esquema da tabela no BigQuery foi definido com uma estrutura simples. A coluna `article_url` foi configurada como `STRING` e `REQUIRED`, funcionando como identificador único de cada registro.

Os demais campos (`headline`, `author`, `article_text` e `collected_at`) foram definidos como `NULLABLE`. Essa escolha considera que algumas notícias podem não apresentar autor explícito, como em editoriais ou conteúdos de agência. Dessa forma, o pipeline consegue inserir os dados mesmo quando algumas informações estão ausentes.

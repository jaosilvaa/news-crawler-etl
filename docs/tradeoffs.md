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
import scrapy
from datetime import datetime
from crawler.items import NewsItem


class GuardianSpiderSpider(scrapy.Spider):
    """
    Spider responsável por coletar notícias da seção World do site The Guardian.
    O foco são artigos padrão de notícia. Conteúdos como live blogs, vídeos,
    áudios e galerias são ignorados.
    """
    name = "guardian_spider"
    allowed_domains = ["theguardian.com"]
    start_urls = ["https://www.theguardian.com/world"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_headlines = set()

    def parse(self, response):
        """Percorre a página inicial e separa os links que parecem ser artigos."""
        all_links = response.css('a::attr(href)').getall()

        article_links = [
            link for link in all_links
            if '/202' in link
            and '/live/' not in link
            and '/audio/' not in link
            and '/video/' not in link
            and '/gallery/' not in link
        ]

        unique_links = set(article_links)

        for link in unique_links:
            yield response.follow(link, callback=self.parse_article)

    def parse_article(self, response):
        """Extrai os dados principais de cada artigo."""
        headline = response.css('h1::text').get()

        if not headline:
            return

        headline_clean = headline.strip()
        headline_lower = headline_clean.lower()

        if headline_lower.startswith('live'):
            return
        if '– live' in headline_lower or '- live' in headline_lower:
            return

        # Evita coletar o mesmo título mais de uma vez
        if headline_clean in self.seen_headlines:
            return
            
        self.seen_headlines.add(headline_clean)

        item = NewsItem()
        item['article_url'] = response.url
        item['headline'] = headline_clean
        item['author'] = response.css('address[data-link-name="byline"] a::text').get()

        # O HTML bruto é salvo aqui. A limpeza do texto acontece depois no pipeline
        item['article_text'] = response.text

        item['collected_at'] = datetime.utcnow().isoformat()

        yield item
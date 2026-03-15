import scrapy

class NewsItem(scrapy.Item):
    headline = scrapy.Field()
    author = scrapy.Field()
    article_text = scrapy.Field()
    article_url = scrapy.Field()
    collected_at = scrapy.Field()   
import yaml
from scrapy.exceptions import DropItem
from readability import Document
from bs4 import BeautifulSoup
from google.cloud import bigquery
from google.oauth2 import service_account


class CleaningPipeline:
    """
    Pipeline responsável por limpar o HTML bruto extraído pelo Spider.
    Utiliza readability-lxml para focar no conteúdo principal e BeautifulSoup
    para remover as tags HTML remanescentes.
    """

    def process_item(self, item, spider):
        raw_html = item.get('article_text', '')

        if not raw_html:
            raise DropItem(f"Artigo sem HTML coletado: {item.get('article_url')}")
        
        try:
            doc = Document(raw_html)
            clean_html = doc.summary()

            soup = BeautifulSoup(clean_html, 'lxml')
            pure_text = soup.get_text(separator=' ', strip=True)

            if not pure_text:
                raise DropItem(f"Artigo ficou vazio após a limpeza: {item.get('article_url')}")
            
            item['article_text'] = pure_text

            if item.get('author'):
                item['author'] = item['author'].strip()

            return item
        except Exception as e:
            spider.logger.error(f"Erro ao limpar o HTML da URL {item.get('article_url')}: {e}")
            raise DropItem("Falha na etapa de limpeza de dados.")


class BigQueryPipeline:
    """
    Pipeline responsável por salvar os dados limpos no Google BigQuery.
    Abre a conexão ao iniciar o Spider e fecha ao finalizar.
    """

    def __init__(self):
        self.client = None
        self.table_ref = None
    
    def open_spider(self, spider):
        """Inicializa a conexão com o BigQuery."""
        try:
            with open('../config.yaml', 'r') as file:
                config = yaml.safe_load(file)['gcp']

            credentials = service_account.Credentials.from_service_account_file(
                f"../{config['credentials_file']}"
            )

            self.client = bigquery.Client(credentials=credentials, project=config['project_id'])
            self.table_ref = f"{config['project_id']}.{config['dataset_id']}.{config['table_id']}"

            spider.logger.info("Conexão com o BigQuery estabelecida com sucesso.")

        except Exception as e:
            spider.logger.error(f"Erro ao iniciar conexão com GCP: {e}")

    def close_spider(self, spider):
        """Fecha a conexão com o BigQuery."""
        if self.client:
            self.client.close()
            spider.logger.info("Conexão com BigQuery encerrada.")
    
    def process_item(self, item, spider):
        """Insere cada item limpo como uma nova linha na tabela."""
        if not self.client:
            spider.logger.error("Cliente BigQuery não está ativo. Ignorando item.")
            return item
        
        row_to_insert = [dict(item)]

        try:
            errors = self.client.insert_rows_json(self.table_ref, row_to_insert)

            if errors:
                spider.logger.error(f"Erro ao inserir no BigQuery: {errors}")
            else:
                spider.logger.debug(f"Artigo salvo com sucesso: {item['article_url']}")
        except Exception as e:
            spider.logger.error(f"Exceção ao tentar salvar no banco: {e}")
        
        return item
from fastapi import FastAPI, HTTPException, Query
from google.cloud import bigquery
from google.oauth2 import service_account
import yaml

app = FastAPI(
    title="News API",
    description="API para consulta de notícias do The Guardian salvas no BigQuery"
)

def get_bq_client():
    """Inicializa o cliente do BigQuery a partir do config.yaml."""
    try:
        with open("config.yaml", "r") as file:
            config = yaml.safe_load(file)['gcp']
        
        credentials = service_account.Credentials.from_service_account_file(
            config["credentials_file"]
        )

        client = bigquery.Client(credentials=credentials, project=config["project_id"])
        table_ref = f"{config['project_id']}.{config['dataset_id']}.{config['table_id']}"

        return client, table_ref
    except Exception as e:
        print(f"[BigQuery] erro de conexão: {e}")
        return None, None

@app.get("/")
def health_check():
    return {"status": "API online e operante!"}

@app.get("/search")
def search_articles(keyword: str = Query(..., min_length=2, description="Palavra-chave para busca")):
    """
    Busca notícias no BigQuery a partir de uma palavra-chave.
    """
    client, table_ref = get_bq_client()

    if not client:
        raise HTTPException(status_code=500, detail="Erro de conexão com o banco de dados")
    
    query = f"""
        SELECT article_url, headline, author, article_text, collected_at
        FROM `{table_ref}`
        WHERE LOWER(headline) LIKE @keyword OR LOWER(article_text) LIKE @keyword
        LIMIT 50
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("keyword", "STRING", f"%{keyword.lower()}%")
        ]
    )

    try:
        query_job = client.query(query, job_config=job_config)
        results = [dict(row) for row in query_job]

        if not results:
            return {"message": "Nenhuma notícia encontrada para essa palavra-chave.", "data": []}
        
        return {"count":len(results), "data":results}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao realizar consulta no banco: {e}")
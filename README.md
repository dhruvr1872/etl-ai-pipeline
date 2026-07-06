# ETL AI Pipeline

An Airflow-orchestrated ETL pipeline that ingests news articles, enriches them with LLM-powered classification and entity extraction, then loads into both a SQL warehouse and a ChromaDB vector store — with incremental deduplication on every run.

## Pipeline Architecture

```
NewsAPI / Sample Data
    └── [Extract] Fetch articles
        └── [Transform] Clean, deduplicate, fingerprint
            └── [Enrich] LLM classification + entity extraction
                └── [Load] SQLite warehouse + ChromaDB vector store
                    (incremental — skips already-loaded IDs)
```

## Features

- **Airflow DAG** — scheduled daily at 6am UTC, XCom passing between tasks
- **LLM enrichment** — GPT-4o-mini classifies each article into 8 categories, extracts key entities, scores importance 1-5
- **Dual load** — structured data to SQLite (queryable warehouse) + embeddings to ChromaDB (semantic search)
- **Incremental loads** — ID-based deduplication prevents duplicate inserts on reruns
- **Standalone runner** — `run_pipeline.py` runs the full pipeline without Airflow
- **Sample data included** — 8 bundled articles work out of the box without a NewsAPI key

## Quickstart (no Airflow)

```bash
git clone https://github.com/dhruvr1872/etl-ai-pipeline
cd etl-ai-pipeline
pip install -r requirements.txt
cp .env.example .env
# Add OPENAI_API_KEY to .env

python run_pipeline.py        # uses sample data
python run_pipeline.py 14     # fetch last 14 days (needs NEWS_API_KEY)
```

## Quickstart (Airflow via Docker)

```bash
cp .env.example .env && docker-compose up airflow-init
docker-compose up -d
# Open http://localhost:8080 (admin/admin)
# Enable dag: ai_enriched_etl_pipeline
```

## LLM Enrichment Output

```json
{
  "category": "RAG / Vector Databases",
  "sentiment": "positive",
  "key_entities": ["Pinecone", "ChromaDB", "Weaviate"],
  "summary": "Vector database market grows 400% driven by RAG adoption",
  "importance_score": 4
}
```

## Stack

| Layer | Tech |
|---|---|
| Orchestration | Apache Airflow 2.9 |
| LLM enrichment | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector store | ChromaDB |
| Warehouse | SQLite (swappable to Postgres/BigQuery) |
| Containerization | Docker Compose |
| Config | pydantic-settings |

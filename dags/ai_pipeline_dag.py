"""
Airflow DAG: AI-enriched ETL pipeline.
Schedule: daily at 6am UTC.
Extract news articles -> clean -> LLM enrich -> warehouse + vector store.
"""
from __future__ import annotations
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "dhruvr1872",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


def _extract(**context) -> None:
    from src.extract import extract_articles
    articles = extract_articles(days_back=1)
    context["task_instance"].xcom_push(key="raw_articles", value=articles)


def _transform(**context) -> None:
    from src.transform import transform_articles
    raw = context["task_instance"].xcom_pull(key="raw_articles", task_ids="extract")
    cleaned = transform_articles(raw)
    context["task_instance"].xcom_push(key="cleaned_articles", value=cleaned)


def _enrich(**context) -> None:
    from src.enrich import enrich_batch
    cleaned = context["task_instance"].xcom_pull(key="cleaned_articles", task_ids="transform")
    enriched = enrich_batch(cleaned)
    context["task_instance"].xcom_push(key="enriched_articles", value=enriched)


def _load(**context) -> None:
    from src.load import load_to_warehouse, load_to_vector_store
    enriched = context["task_instance"].xcom_pull(key="enriched_articles", task_ids="enrich")
    wh = load_to_warehouse(enriched)
    vs = load_to_vector_store(enriched)
    print(f"Loaded {wh} to warehouse, {vs} to vector store")


with DAG(
    dag_id="ai_enriched_etl_pipeline",
    description="Daily ETL: extract news -> LLM enrich -> warehouse + vector store",
    schedule_interval="0 6 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["etl", "ai", "nlp"],
) as dag:

    extract  = PythonOperator(task_id="extract",   python_callable=_extract)
    transform = PythonOperator(task_id="transform", python_callable=_transform)
    enrich   = PythonOperator(task_id="enrich",    python_callable=_enrich)
    load     = PythonOperator(task_id="load",      python_callable=_load)

    extract >> transform >> enrich >> load

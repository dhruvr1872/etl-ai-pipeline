"""Extract: pull raw articles from NewsAPI or use bundled sample data."""
from __future__ import annotations
import logging
from datetime import datetime, timedelta

import requests

from src.config import settings

logger = logging.getLogger(__name__)

SAMPLE_ARTICLES = [
    {"title": "OpenAI releases GPT-5 with improved reasoning", "content": "OpenAI has announced GPT-5, featuring significantly improved reasoning capabilities and a 128k context window. The model shows strong performance on coding and reasoning benchmarks.", "source": "TechCrunch", "published_at": "2025-01-15"},
    {"title": "LangChain introduces new agentic framework LangGraph 2.0", "content": "LangChain has released LangGraph 2.0, enabling more complex multi-agent workflows with better state management, human-in-the-loop capabilities, and improved debugging tooling.", "source": "VentureBeat", "published_at": "2025-01-16"},
    {"title": "Databricks acquires MosaicML for AI training infrastructure", "content": "Databricks completed its acquisition of MosaicML, strengthening its position in enterprise AI training infrastructure and open-source model development. The deal is valued at $1.3 billion.", "source": "Bloomberg", "published_at": "2025-01-17"},
    {"title": "Vector database market grows 400% in 2024", "content": "The vector database market has seen explosive growth driven by RAG adoption across enterprises. Pinecone, Weaviate, and ChromaDB lead the market with large-scale enterprise deployments.", "source": "Forbes", "published_at": "2025-01-18"},
    {"title": "EU AI Act enforcement begins for high-risk systems", "content": "The European Union has begun enforcing the AI Act, requiring companies to classify and document AI systems. High-risk AI applications face stricter compliance requirements and auditing obligations.", "source": "Reuters", "published_at": "2025-01-19"},
    {"title": "Anthropic Claude 3 outperforms GPT-4 on reasoning benchmarks", "content": "Anthropic Claude 3 family shows strong improvements over previous models. Claude 3 Opus outperforms GPT-4 on several key benchmarks including MMLU, HumanEval, and MATH.", "source": "The Verge", "published_at": "2025-01-20"},
    {"title": "Apache Airflow 3.0 released with revamped UI and DAG versioning", "content": "Apache Airflow 3.0 brings a completely revamped UI, improved DAG versioning, and better support for data-aware scheduling. The release marks a major milestone for workflow orchestration.", "source": "InfoQ", "published_at": "2025-01-21"},
    {"title": "dbt Labs raises Series D to expand AI-assisted SQL generation", "content": "dbt Labs secured $222M in Series D funding to expand its data transformation platform. The company plans to invest heavily in AI-assisted SQL generation and data governance features.", "source": "TechCrunch", "published_at": "2025-01-22"},
]


def extract_articles(days_back: int = 7) -> list[dict]:
    """Fetch articles. Falls back to sample data if NEWS_API_KEY not set."""
    if not settings.news_api_key:
        logger.info("No NEWS_API_KEY — using %d sample articles", len(SAMPLE_ARTICLES))
        return SAMPLE_ARTICLES

    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    params = {
        "q": "AI OR data engineering OR LLM OR machine learning",
        "from": from_date,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 100,
        "apiKey": settings.news_api_key,
    }
    resp = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
    resp.raise_for_status()
    articles = resp.json().get("articles", [])
    logger.info("Extracted %d articles from NewsAPI", len(articles))
    return [
        {
            "title": a["title"],
            "content": a.get("content") or a.get("description") or "",
            "source": a.get("source", {}).get("name", ""),
            "published_at": a.get("publishedAt", "")[:10],
        }
        for a in articles
        if a.get("title") and (a.get("content") or a.get("description"))
    ]

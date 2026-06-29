"""LLM-powered classification and entity extraction."""
from __future__ import annotations
import json
import logging

from openai import OpenAI

from src.config import settings

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.openai_api_key)

CATEGORIES = [
    "LLM / Foundation Models",
    "RAG / Vector Databases",
    "Data Engineering",
    "AI Agents / Agentic Systems",
    "MLOps / Infrastructure",
    "AI Policy / Regulation",
    "Funding / Business",
    "Other",
]

ENRICH_PROMPT = """Analyze this tech news article and return a JSON object with exactly these keys:
- category: one of [{categories}]
- sentiment: "positive", "neutral", or "negative"
- key_entities: list of up to 5 key companies, products, or people mentioned
- summary: one sentence summary (max 100 chars)
- importance_score: integer 1-5 (5 = major industry news)

Article title: {title}
Article content: {content}

Return only valid JSON."""


def enrich_article(article: dict) -> dict:
    prompt = ENRICH_PROMPT.format(
        categories=", ".join(CATEGORIES),
        title=article["title"],
        content=article["content"][:800],
    )
    try:
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        enrichment = json.loads(resp.choices[0].message.content)
        return {**article, **enrichment}
    except Exception as exc:
        logger.warning("Enrichment failed for '%s': %s", article["title"], exc)
        return {**article, "category": "Other", "sentiment": "neutral",
                "key_entities": [], "summary": article["title"][:100], "importance_score": 1}


def enrich_batch(articles: list[dict]) -> list[dict]:
    enriched = []
    for i, article in enumerate(articles):
        logger.info("Enriching %d/%d: %s", i + 1, len(articles), article["title"][:60])
        enriched.append(enrich_article(article))
    return enriched

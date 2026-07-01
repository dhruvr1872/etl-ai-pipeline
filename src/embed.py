"""Generate embeddings using OpenAI text-embedding-3-small."""
from __future__ import annotations
import logging

from openai import OpenAI
from src.config import settings

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.openai_api_key)


def embed_articles(articles: list[dict], model: str = "text-embedding-3-small") -> list[list[float]]:
    texts = [a["full_text"] for a in articles]
    resp = client.embeddings.create(input=texts, model=model)
    embeddings = [item.embedding for item in resp.data]
    logger.info("Generated %d embeddings", len(embeddings))
    return embeddings

"""
Load: write enriched articles to SQLite warehouse + ChromaDB.
Uses ID-based deduplication for safe reruns.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime

import chromadb
from sqlalchemy import create_engine, text

from src.config import settings
from src.embed import embed_articles

logger = logging.getLogger(__name__)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    source TEXT,
    published_at TEXT,
    category TEXT,
    sentiment TEXT,
    key_entities TEXT,
    summary TEXT,
    importance_score INTEGER,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS watermark (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    last_loaded_at TEXT
);
"""


def _get_existing_ids(engine) -> set[str]:
    with engine.connect() as conn:
        return {row[0] for row in conn.execute(text("SELECT id FROM articles")).fetchall()}


def load_to_warehouse(articles: list[dict]) -> int:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        conn.execute(text(SCHEMA_SQL)); conn.commit()
    existing = _get_existing_ids(engine)
    new_articles = [a for a in articles if a["id"] not in existing]
    if not new_articles:
        logger.info("No new articles for warehouse"); return 0
    with engine.connect() as conn:
        for a in new_articles:
            conn.execute(text("""
                INSERT OR IGNORE INTO articles
                (id,title,content,source,published_at,category,sentiment,key_entities,summary,importance_score)
                VALUES (:id,:title,:content,:source,:published_at,:category,:sentiment,:key_entities,:summary,:importance_score)
            """), {**a, "key_entities": json.dumps(a.get("key_entities", []))})
        conn.execute(text("INSERT OR REPLACE INTO watermark (id, last_loaded_at) VALUES (1, :ts)"),
                     {"ts": datetime.now().isoformat()})
        conn.commit()
    logger.info("Loaded %d articles to warehouse", len(new_articles))
    return len(new_articles)


def load_to_vector_store(articles: list[dict]) -> int:
    chroma = chromadb.PersistentClient(path=settings.chroma_persist_dir)
    collection = chroma.get_or_create_collection("articles", metadata={"hnsw:space": "cosine"})
    existing = set(collection.get(ids=[a["id"] for a in articles])["ids"])
    new_articles = [a for a in articles if a["id"] not in existing]
    if not new_articles:
        logger.info("No new articles for vector store"); return 0
    embeddings = embed_articles(new_articles)
    collection.add(
        ids=[a["id"] for a in new_articles],
        embeddings=embeddings,
        documents=[a["full_text"] for a in new_articles],
        metadatas=[{"title": a["title"], "category": a.get("category",""), "source": a["source"]} for a in new_articles],
    )
    logger.info("Added %d articles to vector store", len(new_articles))
    return len(new_articles)

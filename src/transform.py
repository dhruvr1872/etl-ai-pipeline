"""Transform: clean and normalise raw articles."""
from __future__ import annotations
import hashlib
import re
from datetime import datetime


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\[.*?\]", "", text)
    return text.strip()


def transform_articles(raw: list[dict]) -> list[dict]:
    """Clean, deduplicate by title fingerprint, and normalise."""
    seen: set[str] = set()
    cleaned = []
    for article in raw:
        title = clean_text(article.get("title") or "")
        content = clean_text(article.get("content") or "")
        if not title or not content or len(content) < 50:
            continue
        fingerprint = hashlib.md5(title.encode()).hexdigest()
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        cleaned.append({
            "id": fingerprint,
            "title": title,
            "content": content,
            "source": article.get("source", ""),
            "published_at": article.get("published_at", datetime.now().strftime("%Y-%m-%d")),
            "full_text": f"{title}. {content}",
        })
    return cleaned

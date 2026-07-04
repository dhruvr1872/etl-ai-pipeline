#!/usr/bin/env python3
"""Run the full ETL pipeline without Airflow — for local dev and testing."""
import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main(days_back: int = 7) -> None:
    from src.extract import extract_articles
    from src.transform import transform_articles
    from src.enrich import enrich_batch
    from src.load import load_to_warehouse, load_to_vector_store

    logger.info("=== ETL AI Pipeline ===")

    logger.info("Step 1/4: Extract")
    raw = extract_articles(days_back=days_back)
    logger.info("Extracted %d raw articles", len(raw))

    logger.info("Step 2/4: Transform")
    cleaned = transform_articles(raw)
    logger.info("Cleaned to %d articles", len(cleaned))

    logger.info("Step 3/4: Enrich (LLM)")
    enriched = enrich_batch(cleaned)

    logger.info("Step 4/4: Load")
    wh = load_to_warehouse(enriched)
    vs = load_to_vector_store(enriched)
    logger.info("Pipeline complete: %d to warehouse, %d to vector store", wh, vs)


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    main(days_back=days)

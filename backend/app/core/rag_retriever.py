from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from sentence_transformers import SentenceTransformer
import chromadb

logger = logging.getLogger(__name__)

CHROMA_DIR = str(Path(__file__).resolve().parent.parent / "data" / "chroma_db")
MODEL_NAME = "BAAI/bge-small-zh-v1.5"

_model: Optional[SentenceTransformer] = None
_client: Optional[chromadb.PersistentClient] = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s", MODEL_NAME)
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("Embedding model loaded (dim=%d)", _model.get_embedding_dimension())
    return _model


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        logger.info("Connecting to ChromaDB at: %s", CHROMA_DIR)
        _client = chromadb.PersistentClient(path=CHROMA_DIR)
    return _client


def _encode_query(query: str) -> list[float]:
    model = _get_model()
    emb = model.encode([query], normalize_embeddings=True, show_progress_bar=False)
    return emb.tolist()[0]


def search_law_articles(
    query: str,
    top_k: int = 3,
    min_score: float = 0.3,
) -> list[dict]:
    client = _get_client()
    try:
        collection = client.get_collection("law_articles")
    except Exception:
        logger.warning("Collection 'law_articles' not found")
        return []

    query_embedding = _encode_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    items = []
    if not results or not results["ids"] or not results["ids"][0]:
        return items

    for i, doc_id in enumerate(results["ids"][0]):
        distance = results["distances"][0][i]
        score = 1.0 - distance
        if score < min_score:
            continue
        meta = results["metadatas"][0][i] if results["metadatas"] else {}
        items.append({
            "chunk_id": doc_id,
            "score": round(score, 4),
            "law_name": meta.get("law_name", ""),
            "part": meta.get("part", ""),
            "article_number": meta.get("article_number", ""),
            "content": meta.get("content", ""),
        })

    return items


def search_judicial_interpretations(
    query: str,
    top_k: int = 2,
    min_score: float = 0.3,
) -> list[dict]:
    client = _get_client()
    try:
        collection = client.get_collection("judicial_interpretations")
    except Exception:
        logger.warning("Collection 'judicial_interpretations' not found")
        return []

    query_embedding = _encode_query(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    items = []
    if not results or not results["ids"] or not results["ids"][0]:
        return items

    for i, doc_id in enumerate(results["ids"][0]):
        distance = results["distances"][0][i]
        score = 1.0 - distance
        if score < min_score:
            continue
        meta = results["metadatas"][0][i] if results["metadatas"] else {}
        items.append({
            "chunk_id": doc_id,
            "score": round(score, 4),
            "title": meta.get("title", ""),
            "document_number": meta.get("document_number", ""),
            "article_number": meta.get("article_number", ""),
            "content": meta.get("content", ""),
        })

    return items


def search_court_cases(
    query: str,
    dispute_type: str | None = None,
    top_k: int = 2,
    min_score: float = 0.3,
) -> list[dict]:
    client = _get_client()
    try:
        collection = client.get_collection("court_cases")
    except Exception:
        logger.warning("Collection 'court_cases' not found")
        return []

    query_embedding = _encode_query(query)

    where_filter = None
    if dispute_type:
        where_filter = {"dispute_type": {"$contains": dispute_type}}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    items = []
    if not results or not results["ids"] or not results["ids"][0]:
        return items

    for i, doc_id in enumerate(results["ids"][0]):
        distance = results["distances"][0][i]
        score = 1.0 - distance
        if score < min_score:
            continue
        meta = results["metadatas"][0][i] if results["metadatas"] else {}
        items.append({
            "chunk_id": doc_id,
            "score": round(score, 4),
            "case_id": meta.get("case_id", ""),
            "title": meta.get("title", ""),
            "court": meta.get("court", ""),
            "case_number": meta.get("case_number", ""),
            "dispute_type": meta.get("dispute_type", ""),
            "province": meta.get("province", ""),
            "is_guiding_case": meta.get("is_guiding_case", "False") == "True",
            "content": meta.get("content", ""),
        })

    return items


def search_all(
    query: str,
    dispute_type: str | None = None,
    law_top_k: int = 3,
    judicial_top_k: int = 2,
    case_top_k: int = 2,
) -> dict[str, list[dict]]:
    return {
        "law_articles": search_law_articles(query, top_k=law_top_k),
        "judicial_interpretations": search_judicial_interpretations(query, top_k=judicial_top_k),
        "court_cases": search_court_cases(query, dispute_type=dispute_type, top_k=case_top_k),
    }


def format_law_context(articles: list[dict]) -> str:
    if not articles:
        return ""
    parts = ["\n\n【检索到的相关法律条文】"]
    for art in articles:
        label = f"{art['law_name']} {art['part']} {art['article_number']}"
        parts.append(f"- {label}：{art['content']}")
    return "\n".join(parts)


def format_judicial_context(interpretations: list[dict]) -> str:
    if not interpretations:
        return ""
    parts = ["\n\n【检索到的相关司法解释】"]
    for interp in interpretations:
        label = f"{interp['title']} {interp['article_number']}"
        parts.append(f"- {label}：{interp['content']}")
    return "\n".join(parts)


def format_case_context(cases: list[dict]) -> str:
    if not cases:
        return ""
    parts = ["\n\n【检索到的相关案例】"]
    for case in cases:
        parts.append(
            f"- {case['title']}（{case['case_number']}）\n"
            f"  法院：{case['court']}\n"
            f"  争议类型：{case['dispute_type']}\n"
            f"  案件概要：{case['content']}\n"
            f"  每个案件情况不同，此案例仅供参考。"
        )
    return "\n".join(parts)


def format_rag_context(results: dict[str, list[dict]]) -> str:
    ctx = ""
    ctx += format_law_context(results.get("law_articles", []))
    ctx += format_judicial_context(results.get("judicial_interpretations", []))
    ctx += format_case_context(results.get("court_cases", []))
    return ctx

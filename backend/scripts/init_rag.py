import json
import time
from pathlib import Path
from datetime import datetime

from sentence_transformers import SentenceTransformer
import chromadb

RAGDATA_ROOT = Path(r"d:\project\marriage_agent\RAGdata")
CHROMA_PERSIST_DIR = str(Path(r"d:\project\marriage_agent\backend\app\data\chroma_db"))
MODEL_NAME = "BAAI/bge-small-zh-v1.5"
BATCH_SIZE = 32

COLLECTIONS_CONFIG = {
    "law_articles": {
        "json_file": RAGDATA_ROOT / "法律条文" / "law_articles.json",
        "text_field": "chunk_text",
        "id_field": "chunk_id",
        "meta_fields": ["law_name", "part", "article_number", "content", "category"],
    },
    "judicial_interpretations": {
        "json_file": RAGDATA_ROOT / "司法解释" / "judicial_interpretations.json",
        "text_field": "chunk_text",
        "id_field": "chunk_id",
        "meta_fields": ["title", "document_number", "article_number", "content", "category"],
    },
    "court_cases": {
        "json_file": RAGDATA_ROOT / "裁判案例" / "court_cases.json",
        "text_field": "chunk_text",
        "id_field": "chunk_id",
        "meta_fields": [
            "case_id", "title", "court", "case_number", "dispute_type",
            "sub_type", "province", "is_guiding_case", "content", "category",
        ],
    },
}


def load_chunks(json_path: Path) -> list[dict]:
    if not json_path.exists():
        print(f"  WARNING: {json_path} not found, skipping")
        return []
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_batch_data(chunks: list[dict], config: dict) -> tuple[list[str], list[str], list[dict], list[str]]:
    ids = []
    texts = []
    metas = []
    contents = []

    for chunk in chunks:
        cid = chunk.get(config["id_field"], "")
        text = chunk.get(config["text_field"], "")
        content = chunk.get("content", "")

        if not cid or not text.strip():
            continue

        meta = {}
        for field in config["meta_fields"]:
            val = chunk.get(field, "")
            if isinstance(val, list):
                val = ", ".join(str(v) for v in val)
            elif isinstance(val, bool):
                val = str(val)
            meta[field] = str(val) if val is not None else ""

        ids.append(cid)
        texts.append(text)
        metas.append(meta)
        contents.append(content)

    return ids, texts, metas, contents


def init_collection(
    client: chromadb.ClientAPI,
    collection_name: str,
    ids: list[str],
    texts: list[str],
    metas: list[dict],
    model: SentenceTransformer,
):
    print(f"\n  Initializing collection: {collection_name}")
    print(f"  Total chunks: {len(ids)}")

    try:
        client.delete_collection(collection_name)
        print(f"  Deleted existing collection")
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    total = len(texts)
    for i in range(0, total, BATCH_SIZE):
        batch_texts = texts[i : i + BATCH_SIZE]
        batch_ids = ids[i : i + BATCH_SIZE]
        batch_metas = metas[i : i + BATCH_SIZE]

        embeddings = model.encode(
            batch_texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            documents=batch_texts,
            metadatas=batch_metas,
        )

        done = min(i + BATCH_SIZE, total)
        print(f"  Embedded & stored: {done}/{total}")

    count = collection.count()
    print(f"  Collection '{collection_name}' ready: {count} vectors")
    return count


def main():
    print("=" * 60)
    print("  RAG Vector Database Initialization")
    print(f"  Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    print(f"\nLoading embedding model: {MODEL_NAME}")
    t0 = time.time()
    model = SentenceTransformer(MODEL_NAME)
    print(f"Model loaded in {time.time() - t0:.1f}s")
    print(f"Embedding dimension: {model.get_embedding_dimension()}")

    print(f"\nInitializing ChromaDB at: {CHROMA_PERSIST_DIR}")
    Path(CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    results = {}

    for coll_name, config in COLLECTIONS_CONFIG.items():
        print(f"\n{'=' * 50}")
        print(f"  Processing: {coll_name}")
        print(f"{'=' * 50}")

        chunks = load_chunks(config["json_file"])
        if not chunks:
            results[coll_name] = {"status": "skipped", "count": 0}
            continue

        ids, texts, metas, contents = build_batch_data(chunks, config)
        count = init_collection(client, coll_name, ids, texts, metas, model)
        results[coll_name] = {"status": "ok", "count": count}

    print("\n" + "=" * 60)
    print("  Initialization Complete")
    print("=" * 60)
    for coll_name, info in results.items():
        print(f"  {coll_name}: {info['status']} ({info['count']} vectors)")
    total = sum(r["count"] for r in results.values())
    print(f"  Total: {total} vectors")
    print(f"  Persisted at: {CHROMA_PERSIST_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()

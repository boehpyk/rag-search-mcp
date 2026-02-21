import os
import uuid
import requests
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

NGINX_BASE_URL = os.environ.get("NGINX_BASE_URL", "http://nginx")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://qdrant:6333")
COLLECTION_NAME = "docs"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DIM = 384
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def crawl_directory(base_url: str, path: str = "/docs/") -> list[str]:
    """Recursively crawl nginx JSON autoindex and return all .md file paths."""
    url = base_url + path
    resp = requests.get(url, headers={"Accept": "application/json"}, timeout=10)
    resp.raise_for_status()
    entries = resp.json()

    md_paths = []
    for entry in entries:
        name = entry["name"]
        entry_type = entry["type"]
        if entry_type == "directory":
            subpath = path + name + "/"
            md_paths.extend(crawl_directory(base_url, subpath))
        elif entry_type == "file" and name.endswith(".md"):
            md_paths.append(path + name)

    return md_paths


def fetch_document(base_url: str, path: str) -> str:
    """Fetch document text from nginx."""
    url = base_url + path
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def main():
    print("=== Indexer starting ===")

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"Connecting to Qdrant at {QDRANT_URL}")
    client = QdrantClient(url=QDRANT_URL)

    print(f"Recreating collection '{COLLECTION_NAME}'")
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
    )

    print(f"Crawling docs from {NGINX_BASE_URL}/docs/")
    md_paths = crawl_directory(NGINX_BASE_URL)
    print(f"Found {len(md_paths)} markdown files: {md_paths}")

    all_points = []
    for doc_path in md_paths:
        # Strip leading /docs/ to get a clean relative path for payloads
        clean_path = doc_path.removeprefix("/docs/")
        source_url = NGINX_BASE_URL + doc_path

        print(f"  Fetching: {doc_path}")
        try:
            text = fetch_document(NGINX_BASE_URL, doc_path)
        except Exception as e:
            print(f"  ERROR fetching {doc_path}: {e}")
            continue

        chunks = chunk_text(text)
        print(f"  → {len(chunks)} chunks")

        vectors = model.encode(chunks, show_progress_bar=False).tolist()

        for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
            all_points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "path": clean_path,
                        "chunk_index": i,
                        "content": chunk,
                        "source_url": source_url,
                    },
                )
            )

    print(f"Upserting {len(all_points)} points into Qdrant...")
    batch_size = 100
    for i in range(0, len(all_points), batch_size):
        batch = all_points[i : i + batch_size]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)

    info = client.get_collection(COLLECTION_NAME)
    print(f"Collection now has {info.points_count} points.")
    print("=== Indexer done. Exiting. ===")


if __name__ == "__main__":
    main()
